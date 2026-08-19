import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DALI_BASE_URL, DALI_USER, DALI_PASS


class DaliClient:
    def __init__(self, on_log=None):
        self.session = requests.Session()
        self.base = DALI_BASE_URL
        self.ui = None
        self.logged_in = False
        self.on_log = on_log or (lambda msg: None)

    def _log(self, msg):
        self.on_log(msg)

    def _ts(self):
        return str(int(time.time() * 1000))

    def login(self):
        self._log("Obteniendo pagina de login...")
        self.session.get(f"{self.base}/")
        self._log("Enviando credenciales...")
        r = self.session.post(
            f"{self.base}/login/",
            data={"user_name": DALI_USER, "user_password": DALI_PASS, "submit": ""},
            headers={"Referer": f"{self.base}/"},
            allow_redirects=True,
        )
        if "inputUser" in r.text:
            self._log("ERROR: Login fallido - credenciales incorrectas")
            return False
        self._log("Login exitoso, obteniendo UID...")
        tr = self.session.post(
            f"{self.base}/tracker/?{self._ts()}", data={"gmapk": "1"}
        )
        data = tr.json().get("data", [{}])
        if not data:
            self._log("ERROR: No se pudo obtener UID del tracker")
            return False
        self.ui = data[0].get("u")
        self.logged_in = True
        self._log(f"UID obtenido: {self.ui}")
        return True

    def post_json(self, endpoint, params=None):
        data = {"json": str(endpoint), "uid": str(self.ui)}
        if params:
            data.update(params)
        r = self.session.post(
            f"{self.base}/?option=json&seed={self._ts()}", data=data
        )
        return r.json()

    def listar_egresos(self):
        self._log("Listando egresos generados (json 2093)...")
        result = self.post_json(2093)
        egresos = result.get("data", [])
        self._log(f"  Encontrados {len(egresos)} egresos")
        return egresos

    def cargar_egreso(self, mbocodigo):
        self._log(f"Cargando datos del egreso {mbocodigo} (json 2091)...")
        result = self.post_json(2091, {"mbocodigo": mbocodigo})
        data = result.get("data", [])
        if data:
            self._log(f"  Hoja Ruta: {data[0].get('HOJARUTA', 'N/A')}")
        return data

    def cargar_productos(self, mbocodigo):
        self._log(f"Cargando productos del egreso {mbocodigo} (json 2094)...")
        result = self.post_json(2094, {"mbocodigo": mbocodigo, "page": "1", "rp": "100"})
        productos = result.get("data", [])
        self._log(f"  {len(productos)} productos encontrados")
        return productos

    def cargar_lotes_disponibles(self, dmbcodigo):
        result = self.post_json(2092, {"dmbcodigo": dmbcodigo})
        lotes = result.get("data", [])
        return lotes

    def cargar_lotes_asignados(self, mbocodigo, pgecodigo, pescodigo):
        result = self.post_json(
            2095,
            {
                "mbocodigo": mbocodigo,
                "pgecodigo": pgecodigo,
                "pescodigo": pescodigo,
            },
        )
        return result.get("data", [])

    def asignar_lote(self, dmborigen, dmbdestino, ilocodigo, cantidad):
        self._log(f"  Asignando lote: origen={dmborigen}, destino={dmbdestino}, lote={ilocodigo}, cant={cantidad}")
        result = self.post_json(
            2096,
            {
                "dmborigen": str(dmborigen),
                "dmbdestino": str(dmbdestino),
                "ilocodigo": str(ilocodigo),
                "cantidad": str(cantidad),
            },
        )
        msg = result.get("data", [{}])[0].get("MSG", "")
        ok = msg == "ok"
        if not ok:
            self._log(f"  ERROR al asignar lote: {msg}")
        return ok

    def eliminar_lote(self, dmborigen, dmbdestino):
        result = self.post_json(
            2097, {"dmborigen": str(dmborigen), "dmbdestino": str(dmbdestino)}
        )
        msg = result.get("data", [{}])[0].get("MSG", "")
        return msg == "ok"

    def procesar_egreso(self, mbocodigo):
        self._log(f"Procesando egreso {mbocodigo} (json 2099)...")
        result = self.post_json(2099, {"mbocodigo": mbocodigo})
        msg = result.get("data", [{}])[0].get("MSG", "")
        ok = msg == "ok"
        if ok:
            self._log(f"  Egreso {mbocodigo} PROCESADO exitosamente")
        else:
            self._log(f"  ERROR al procesar egreso {mbocodigo}: {msg}")
        return ok
