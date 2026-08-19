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
        # y extraer el MBO_CODIGO (ultimo td oculto)
        result = self.driver.execute_script(f"""
            var rows = $('#{grid_id} tbody tr');
            for (var i = 0; i < rows.length; i++) {{
                var cells = $(rows[i]).find('td div');
                for (var j = 0; j < cells.length; j++) {{
                    var text = $(cells[j]).text().trim();
                    if (text.indexOf('{referencia}') >= 0 && text.length > 8) {{
                        // El MBO_CODIGO esta en el ultimo td (oculto)
                        var lastDiv = $(rows[i]).find('td:last div');
                        var mbo = lastDiv.text().trim();
                        // Tambien intentar desde el id de la fila
                        var rowId = $(rows[i]).attr('id');
                        $(rows[i]).trigger('click');
                        return {{
                            found: true,
                            rowIndex: i,
                            rowData: text,
                            mbocodigo: mbo,
                            rowId: rowId
                        }};
                    }}
                }}
            }}
            return {{ found: false }};
        """)

        if not result or not result.get("found"):
            self._log(f"  No se encontro fila con {referencia}")
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

        self._log(f"  Fila encontrada: {result.get('rowData')}")
        self._log(f"  MBO_CODIGO: {result.get('mbocodigo')}")
        time.sleep(1)

        # Cargar datos del egreso directamente via JSON 2091
        mbo = result.get("mbocodigo", "")
        if mbo:
            self._log(f"  Cargando egreso via JSON 2091...")
            egreso_data = self._ajax_json("2091", {"mbocodigo": str(mbo)})
            if egreso_data and egreso_data.get("data"):
                d = egreso_data["data"][0]
                # Llenar los campos del formulario via JS
                self.driver.execute_script(f"""
                    $('#procesaregresoshojaruta_codigo').val('{d.get("MBOCODIGO", "")}');
                    $('#procesaregresoshojaruta_secuencial').val('{d.get("SECUENCIAL", "")}');
                    $('#procesaregresoshojaruta_fecha').val('{d.get("FECHA", "")}');
                    $('#procesaregresoshojaruta_bodega').val('{d.get("BODEGA", "")}');
                    $('#procesaregresoshojaruta_orden').val('{d.get("ORDEN", "")}');
                    $('#procesaregresoshojaruta_dia').val('{d.get("DIA", "")}');
                    $('#procesaregresoshojaruta_placa').val('{d.get("PLACA", "")}');
                    $('#procesaregresoshojaruta_descripciontransporte').val('{d.get("DESCRIPCIONTRANSPORTE", "")}');
                    $('#procesaregresoshojaruta_hojaruta').val('{d.get("HOJARUTA", "")}');
                    $('#procesaregresoshojaruta_descripcionhojaruta').val('{d.get("DESCRIPCIONHOJARUTA", "")}');
                    $('#procesaregresoshojaruta_responsableruta').val('{d.get("RESPONSABLE", "")}');
                    $('#procesaregresoshojaruta_estado').val('{d.get("ESTADO", "")}');
                    $('#procesaregresoshojaruta_observacion').val('{d.get("OBSERVACION", "")}');
                    $('#procesaregresoshojaruta_dcaestado').val('{d.get("DCAESTADO", "")}');
                """)
                self._log(f"  Egreso cargado via JSON: HR={d.get('HOJARUTA','')}")
                return True
            else:
                self._log(f"  JSON 2091 no devolvio datos para MBO={mbo}")
                return False
        else:
            self._log(f"  No se pudo obtener MBO_CODIGO de la fila")
            return False

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

    def click_producto(self, dmb_codigo, pge, pes):
        self._log(f"  Seleccionando producto DMB={dmb_codigo}...")
        mbo = self.driver.execute_script("return $('#procesaregresoshojaruta_codigo').val() || '';")
        if mbo:
            result = self._ajax_json("2095", {
                "mbocodigo": str(mbo),
                "pgecodigo": str(pge),
                "pescodigo": str(pes)
            })
            lotes_asignados = result.get("data", []) if result else []
            self._log(f"  Lotes ya asignados: {len(lotes_asignados)}")
            return lotes_asignados
        return []

    def asignar_lote(self, dmb_origen, ilocodigo, cantidad):
        self._log(f"  Asignando lote via JSON 2096: DMB={dmb_origen}, ILO={ilocodigo}, cant={cantidad}...")
        result = self._ajax_json("2096", {
            "dmborigen": str(dmb_origen),
            "dmbdestino": "NULL",
            "ilocodigo": str(ilocodigo),
            "cantidad": str(cantidad)
        })
        if result and result.get("data") and result["data"][0].get("MSG") == "ok":
            self._log("  Lote asignado OK")
            return True
        else:
            msg = result.get("data", [{}])[0].get("MSG", "error desconocido") if result else "sin respuesta"
            self._log(f"  ERROR asignando lote: {msg}")
            return False

    def procesar_egreso(self):
        self._log("Procesando egreso via JSON 2099...")
        mbo = self.driver.execute_script("return $('#procesaregresoshojaruta_codigo').val() || '';")
        result = self._ajax_json("2099", {"mbocodigo": str(mbo)})
        if result and result.get("data") and result["data"][0].get("MSG") == "ok":
            self.driver.execute_script("$('#procesaregresoshojaruta_estado').val('PROCESADO');")
            self._log("  Egreso PROCESADO OK")
            return True
        else:
            msg = result.get("data", [{}])[0].get("MSG", "error desconocido") if result else "sin respuesta"
            self._log(f"  ERROR procesando: {msg}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
