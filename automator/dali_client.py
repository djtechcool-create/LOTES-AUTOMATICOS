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
            self._log("Sesion ya activa o pagina diferente")
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

        if "inputUser" in self.driver.page_source:
            self._log("ERROR: Login fallido")
            return False

        self._log("Login exitoso!")
        self.logged_in = True
        return True

    def navigate_to_egresos(self):
        self._log("Navegando a Procesar Egreso por Ruta...")
        url = f"{self.base}/?option=load&module=logistica&file=procesaregresohojaruta&type=html"
        self.driver.get(url)
        time.sleep(5)
        self._log("Pagina de Procesar Egreso cargada")

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
