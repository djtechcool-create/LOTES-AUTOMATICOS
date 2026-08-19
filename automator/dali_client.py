import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
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
        self.driver.find_element(By.ID, "inputUser").send_keys("azapata")
        self.driver.find_element(By.ID, "inputClave").send_keys("1753112158")
        time.sleep(0.5)
        self._log("Clickeando boton Ingresar...")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        if "inputUser" in self.driver.page_source:
            self._log("ERROR: Login fallido")
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
        raise Exception("UI no se pudo definir.")

    def navigate_to_egresos(self):
        self._log("Cargando pagina de Procesar Egreso via loadContent()...")
        self.driver.execute_script("""
            loadContent(
                '/?option=load&module=logistica&file=procesaregresohojaruta&type=html',
                'Procesar Egreso por Ruta'
            );
        """)
        self._log("Esperando a que la pagina cargue...")
        time.sleep(8)
        self._log(f"URL: {self.driver.current_url}")

    def buscar_y_seleccionar_egreso(self, referencia):
        self._log(f"Buscando egreso con HR terminando en {referencia}...")

        grid_id = "procesaregresoshojaruta_flex_listaegresos"

        # Buscar en las filas del grid la HR que termine en la referencia
        result = self.driver.execute_script(f"""
            var rows = $('#{grid_id} tbody tr');
            for (var i = 0; i < rows.length; i++) {{
                var cells = $(rows[i]).find('td div');
                for (var j = 0; j < cells.length; j++) {{
                    var text = $(cells[j]).text().trim();
                    if (text.indexOf('{referencia}') >= 0 && text.length > 8) {{
                        $(rows[i]).trigger('click');
                        return {{
                            found: true,
                            rowIndex: i,
                            rowData: text
                        }};
                    }}
                }}
            }}
            return {{ found: false }};
        """)

        if not result or not result.get("found"):
            self._log(f"  No se encontro fila con {referencia}")
            # Mostrar todas las HR disponibles para debug
            all_hrs = self.driver.execute_script(f"""
                var hrs = [];
                $('#{grid_id} tbody tr').each(function() {{
                    var cells = $(this).find('td div');
                    cells.each(function() {{
                        var t = $(this).text().trim();
                        if (t.indexOf('HRU') >= 0) hrs.push(t);
                    }});
                }});
                return hrs;
            """)
            self._log(f"  HRs disponibles en grid: {all_hrs}")
            return False

        self._log(f"  Fila encontrada y seleccionada (verde): {result.get('rowData')}")
        time.sleep(1)

        # Click en boton "Ver"
        self.driver.execute_script(f"""
            var btns = $('#{grid_id} .pDiv .pButton');
            btns.each(function() {{
                var title = $(this).attr('title') || '';
                var val = $(this).find('input').val() || '';
                if (title === 'Ver' || val === 'Ver') {{
                    $(this).trigger('click');
                    return false;
                }}
            }});
        """)
        self._log("  Boton 'Ver' clickeado")
        time.sleep(3)
        return True

    def get_egreso_actual(self):
        self._log("Leyendo datos del egreso seleccionado...")
        data = self.driver.execute_script("""
            return {
                mbocodigo: $('#procesaregresoshojaruta_codigo').val() || '',
                hojaruta: $('#procesaregresoshojaruta_hojaruta').val() || '',
                estado: $('#procesaregresoshojaruta_estado').val() || '',
                dcaestado: $('#procesaregresoshojaruta_dcaestado').val() || '',
                responsable: $('#procesaregresoshojaruta_responsableruta').val() || ''
            };
        """)
        self._log(f"  MBO={data['mbocodigo']} HR={data['hojaruta']} Estado={data['estado']}")
        return data

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
        return self.driver.execute_script(js)

    def cargar_productos_egreso(self, mbocodigo):
        self._log(f"Cargando productos del egreso {mbocodigo}...")
        result = self._ajax_json("2094", {
            "mbocodigo": str(mbocodigo),
            "page": "1",
            "rp": "100"
        })
        productos = result.get("data", []) if result else []
        self._log(f"  {len(productos)} productos encontrados")
        for p in productos:
            self._log(f"    {p.get('PRODUCTO','')} DMB={p.get('DMB_CODIGO','')} Cant={p.get('CANTIDAD','')}")
        return productos

    def cargar_lotes_disponibles(self, dmbcodigo):
        result = self._ajax_json("2092", {"dmbcodigo": str(dmbcodigo)})
        return result.get("data", []) if result else []

    def click_producto(self, dmb_codigo):
        self._log(f"  Click en producto DMB={dmb_codigo}...")
        self.driver.execute_script(f"""
            var rows = $('#procesaregresoshojaruta_flex_detalle_egreso tbody tr');
            rows.each(function() {{
                var divs = $(this).find('td div');
                for (var i = 0; i < divs.length; i++) {{
                    if ($(divs[i]).text().trim() === '{dmb_codigo}') {{
                        $(this).find('td:first div').trigger('click');
                        return false;
                    }}
                }}
            }});
        """)
        time.sleep(2)

    def asignar_lote(self, ilocodigo, cantidad):
        self._log(f"  Asignando lote={ilocodigo}, cant={cantidad}...")
        self.driver.execute_script(f"""
            $('#procesaregresoshojaruta_lote').val('{ilocodigo}').trigger('change');
            $('#procesaregresoshojaruta_cantidad').val('{cantidad}');
        """)
        time.sleep(0.5)

        # Click Agregar en el flexigrid de lotes
        self.driver.execute_script("""
            var btns = $('#procesaregresoshojaruta_flex_detalle_lote .pDiv .pButton');
            btns.each(function() {
                var val = $(this).find('input').val() || '';
                if (val === 'Agregar' || $(this).hasClass('add')) {
                    $(this).trigger('click');
                    return false;
                }
            });
        """)
        time.sleep(2)
        self._log("  Lote asignado OK")

    def procesar_egreso(self):
        self._log("Procesando egreso...")
        self.driver.execute_script("""
            $('#procesaregresoshojaruta_procesar').trigger('click');
        """)
        time.sleep(2)
        self.driver.execute_script("""
            if ($('#confirmModalYes').length && $('#confirmModalYes').is(':visible')) {
                $('#confirmModalYes').trigger('click');
            }
        """)
        time.sleep(3)
        self._log("  Egreso procesado")

    def close(self):
        if self.driver:
            self.driver.quit()
