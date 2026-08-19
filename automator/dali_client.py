import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def buscar_por_hojaruta(self, referencia):
        self._log(f"Buscando HR: {referencia} via FlexiGrid UI...")
        wait = WebDriverWait(self.driver, 10)

        grid_id = "procesaregresoshojaruta_flex_listaegresos"

        try:
            # 1. Click en el icono de busqueda (lupa)
            search_toggle = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"#{grid_id} .pSearch")
            ))
            search_toggle.click()
            time.sleep(1)
            self._log("  Panel de busqueda abierto")

            # 2. Seleccionar "HOJA RUTA" en el combo de busqueda
            search_select = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"#{grid_id} select[name='qtype']")
            ))
            # Buscar la opcion HOJ
            self.driver.execute_script("""
                var sel = arguments[0];
                for (var i = 0; i < sel.options.length; i++) {
                    if (sel.options[i].value === 'HOJ') {
                        sel.selectedIndex = i;
                        $(sel).trigger('change');
                        break;
                    }
                }
            """, search_select)
            time.sleep(0.5)
            self._log("  Filtro seleccionado: HOJA RUTA")

            # 3. Escribir la referencia en el campo de busqueda
            search_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"#{grid_id} input[name='q']")
            ))
            search_input.clear()
            search_input.send_keys(str(referencia))
            time.sleep(0.5)
            self._log(f"  Texto buscado: {referencia}")

            # 4. Presionar Enter para buscar
            search_input.send_keys(Keys.RETURN)
            self._log("  Enter presionado, esperando resultados...")
            time.sleep(3)

            # 5. Verificar si hay resultados
            rows = self.driver.find_elements(
                By.CSS_SELECTOR, f"#{grid_id} tbody tr"
            )
            data_rows = [r for r in rows if r.get_attribute("class") and "trSelected" in r.get_attribute("class") or len(r.find_elements(By.TAG_NAME, "td")) > 1]

            # Contar filas con datos (no header)
            count = self.driver.execute_script(f"""
                return $('#{grid_id} tbody tr').length;
            """)
            self._log(f"  Filas de resultados: {count}")

            if count == 0:
                self._log(f"  No se encontraron resultados para {referencia}")
                return None

            # 6. Seleccionar la primera fila (click para que se pinte de verde)
            first_row = self.driver.execute_script(f"""
                var row = $('#{grid_id} tbody tr')[0];
                if (row) {{ $(row).trigger('click'); return true; }}
                return false;
            """)
            time.sleep(1)
            self._log("  Fila seleccionada (verde)")

            # 7. Click en boton "Ver"
            ver_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"#{grid_id} .pDiv .pButton[title='Ver'], #{grid_id} .pDiv input[value='Ver']")
            ))
            # Si no encuentra por titulo, buscar por clase
            if not ver_btn:
                ver_btn = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"#{grid_id} .view")
                ))
            ver_btn.click()
            self._log("  Boton 'Ver' clickeado")
            time.sleep(3)

            return True

        except Exception as e:
            self._log(f"  ERROR en busqueda UI: {e}")
            return None

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

    def get_egreso_actual(self):
        self._log("Leyendo datos del egreso seleccionado...")
        mbo = self._js("return $('#procesaregresoshojaruta_codigo').val();")
        hr = self._js("return $('#procesaregresoshojaruta_hojaruta').val();")
        estado = self._js("return $('#procesaregresoshojaruta_estado').val();")
        dcaestado = self._js("return $('#procesaregresoshojaruta_dcaestado').val();")
        self._log(f"  MBO={mbo} HR={hr} Estado={estado} DCAEstado={dcaestado}")
        return {
            "mbocodigo": mbo,
            "hojaruta": hr,
            "estado": estado,
            "dcaestado": dcaestado,
        }

    def cargar_productos_egreso(self):
        self._log("Cargando productos del egreso...")
        result = self._ajax_json("2094", {
            "mbocodigo": self.get_egreso_actual()["mbocodigo"],
            "page": "1",
            "rp": "100"
        })
        productos = result.get("data", []) if result else []
        self._log(f"  {len(productos)} productos encontrados")
        return productos

    def cargar_lotes_disponibles(self, dmbcodigo):
        result = self._ajax_json("2092", {"dmbcodigo": str(dmbcodigo)})
        return result.get("data", []) if result else []

    def seleccionar_producto(self, dmb_codigo):
        self._log(f"  Seleccionando producto DMB={dmb_codigo}...")
        self.driver.execute_script(f"""
            var rows = $('#procesaregresoshojaruta_flex_detalle_egreso tbody tr');
            rows.each(function() {{
                var divs = $(this).find('td div');
                for (var i = 0; i < divs.length; i++) {{
                    if ($(divs[i]).text().trim() === '{dmb_codigo}') {{
                        $(this).trigger('click');
                        return false;
                    }}
                }}
            }});
        """)
        time.sleep(1)

    def seleccionar_lote(self, ilocodigo):
        self._log(f"  Seleccionando lote {ilocodigo}...")
        self.driver.execute_script(f"""
            $('#procesaregresoshojaruta_lote').val('{ilocodigo}');
        """)
        time.sleep(0.5)

    def asignar_lote_ui(self, ilocodigo, cantidad):
        self._log(f"  Asignando lote {ilocodigo}, cantidad {cantidad}...")
        # Seleccionar lote en el combo
        self.driver.execute_script(f"""
            $('#procesaregresoshojaruta_lote').val('{ilocodigo}');
            $('#procesaregresoshojaruta_cantidad').val('{cantidad}');
        """)
        time.sleep(0.5)

        # Click en boton Agregar del flexigrid de lotes
        self.driver.execute_script("""
            var btns = $('#procesaregresoshojaruta_flex_detalle_lote .pDiv .pButton');
            btns.each(function() {
                if ($(this).hasClass('add') || $(this).find('input').val() === 'Agregar') {
                    $(this).trigger('click');
                    return false;
                }
            });
        """)
        time.sleep(2)
        self._log("  Lote asignado")

    def seleccionar_producto_y_cargar_lotes(self, dmb_codigo):
        self._log(f"  Clickeando producto DMB={dmb_codigo}...")
        # Simular doble click en el producto del flexigrid
        self.driver.execute_script(f"""
            var rows = $('#procesaregresoshojaruta_flex_detalle_egreso tbody tr');
            rows.each(function() {{
                var hidden = $(this).find('td:has(div)');
                var text = '';
                hidden.find('div').each(function() {{ text += $(this).text().trim() + '|'; }});
                if (text.indexOf('{dmb_codigo}') >= 0) {{
                    $(this).find('td:first div').trigger('click');
                    return false;
                }}
            }});
        """)
        time.sleep(2)

    def procesar_egreso_ui(self):
        self._log("Procesando egreso via UI...")
        self.driver.execute_script("""
            $('#procesaregresoshojaruta_procesar').trigger('click');
        """)
        time.sleep(2)
        # Confirmar si aparece dialogo
        self.driver.execute_script("""
            if ($('#confirmModalYes').length) {
                $('#confirmModalYes').trigger('click');
            }
        """)
        time.sleep(3)
        self._log("  Egreso procesado")

    def close(self):
        if self.driver:
            self.driver.quit()
