import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class DaliClient:
    def __init__(self, on_log=None):
        self.driver = None
        self.base = "https://sistemapae.nutri.com.ec"
        self.logged_in = False
        self.on_log = on_log or (lambda msg: None)

    def _log(self, msg):
        self.on_log(msg)

    def start_browser(self):
        self._log("Abriendo Google Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self._log("Chrome abierto correctamente")

    def login(self):
        self._log("Navegando a DALI...")
        self.driver.get(f"{self.base}/")
        time.sleep(3)

        if "inputUser" not in self.driver.page_source:
            self._log("Sesion ya activa, esperando dashboard...")
            self._wait_for_ui()
            self.logged_in = True
            return True

        self._log("Pagina de login detectada, ingresando credenciales...")
        user_input = self.driver.find_element(By.ID, "inputUser")
        pass_input = self.driver.find_element(By.ID, "inputClave")
        user_input.clear()
        user_input.send_keys("azapata")
        pass_input.clear()
        pass_input.send_keys("1753112158")
        time.sleep(0.5)

        self._log("Clickeando boton Ingresar...")
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(5)

        url = self.driver.current_url
        self._log(f"URL despues del login: {url}")

        if "inputUser" in self.driver.page_source:
            self._log("ERROR: Login fallido, sigue en pagina de login")
            return False

        self._log("Login exitoso, esperando que UI se defina...")
        self._wait_for_ui()
        self.logged_in = True
        return True

    def _wait_for_ui(self, timeout=30):
        self._log("Esperando inicializacion de UI (tracker)...")
        for i in range(timeout):
            try:
                is_defined = self.driver.execute_script(
                    "return typeof UI !== 'undefined' && UI !== false && UI !== 0;"
                )
                if is_defined:
                    uid = self.driver.execute_script("return UI;")
                    self._log(f"UI definido: {uid}")
                    return True
            except Exception:
                pass
            time.sleep(1)
        self._log("UI no se definio solo, intentando tracker manual...")
        try:
            self.driver.execute_script("""
                $.ajax({
                    url: '/tracker/?' + new Date().getTime(),
                    data: {gmapk: '1'},
                    type: 'POST',
                    dataType: 'json',
                    async: false,
                    success: function(data) {
                        if (data && data.data && data.data[0] && data.data[0].u) {
                            UI = data.data[0].u * 1;
                        }
                    }
                });
            """)
            time.sleep(2)
            uid = self.driver.execute_script("return UI;")
            if uid and uid is not False:
                self._log(f"UI obtenido via tracker manual: {uid}")
                return True
        except Exception as e:
            self._log(f"Tracker manual fallo: {e}")
        raise Exception("UI no se pudo definir. Verifica conexion a DALI.")

    def _js(self, script, *args):
        return self.driver.execute_script(script, *args)

    def _ajax_json(self, endpoint, params=None):
        params = params or {}
        js = f"""
            var result = null;
            var params = {json.dumps(params)};
            params['json'] = '{endpoint}';
            params['uid'] = UI;
            $.ajax({{
                url: '/?option=json&seed=' + new Date().getTime(),
                type: 'POST',
                data: params,
                dataType: 'json',
                async: false,
                success: function(data) {{ result = data; }}
            }});
            return result;
        """
        return self._js(js)

    def listar_egresos(self):
        self._log("Obteniendo lista de egresos...")
        result = self._ajax_json("2093")
        egresos = result.get("data", []) if result else []
        self._log(f"  {len(egresos)} egresos encontrados")
        return egresos

    def cargar_egreso(self, mbocodigo):
        self._log(f"Cargando egreso {mbocodigo}...")
        result = self._ajax_json("2091", {"mbocodigo": str(mbocodigo)})
        data = result.get("data", []) if result else []
        if data:
            hr = data[0].get("HOJARUTA", "N/A")
            self._log(f"  Hoja Ruta: {hr}")
        return data

    def cargar_productos(self, mbocodigo):
        self._log(f"Cargando productos del egreso {mbocodigo}...")
        result = self._ajax_json("2094", {
            "mbocodigo": str(mbocodigo),
            "page": "1",
            "rp": "100"
        })
        productos = result.get("data", []) if result else []
        self._log(f"  {len(productos)} productos encontrados")
        return productos

    def cargar_lotes_disponibles(self, dmbcodigo):
        result = self._ajax_json("2092", {"dmbcodigo": str(dmbcodigo)})
        return result.get("data", []) if result else []

    def asignar_lote(self, dmborigen, dmbdestino, ilocodigo, cantidad):
        self._log(f"  Asignando: lote={ilocodigo}, cant={cantidad}")
        result = self._ajax_json("2096", {
            "dmborigen": str(dmborigen),
            "dmbdestino": str(dmbdestino),
            "ilocodigo": str(ilocodigo),
            "cantidad": str(cantidad),
        })
        if result and result.get("data"):
            msg = result["data"][0].get("MSG", "")
            ok = msg == "ok"
            if not ok:
                self._log(f"  ERROR: {msg}")
            return ok
        self._log("  ERROR: Sin respuesta del servidor")
        return False

    def procesar_egreso(self, mbocodigo):
        self._log(f"Procesando egreso {mbocodigo}...")
        result = self._ajax_json("2099", {"mbocodigo": str(mbocodigo)})
        if result and result.get("data"):
            msg = result["data"][0].get("MSG", "")
            ok = msg == "ok"
            if ok:
                self._log(f"  Egreso {mbocodigo} PROCESADO OK")
            else:
                self._log(f"  ERROR al procesar: {msg}")
            return ok
        self._log("  ERROR: Sin respuesta")
        return False

    def close(self):
        if self.driver:
            self.driver.quit()
