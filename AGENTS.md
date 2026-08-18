# LOTES AUTOMATICOS - Guia del Proyecto

## Contexto General
Sistema para automatizar la carga de egresos en DALI (web de logistica). El usuario procesa egresos por ruta diariamente y necesita automatizar el proceso de asignar lotes y cantidades a productos.

## Stack Tecnologico
- Frontend: Flask (interfaz web local)
- Backend: Python 3
- Automatizacion web: Selenium + Chrome
- Excel: pandas + openpyxl
- Matching: fuzzywuzzy

## Estado Actual
FASE: Investigacion completa. Se descubrio la estructura de DALI y los endpoints JSON. FALTA implementar la app.

## Credenciales DALI
- URL: https://sistemapae.nutri.com.ec/
- Usuario: azapata
- Password: 1753112158
- Login: POST a /login/ con user_name, user_password, submit

## Estructura del Excel
- Archivo: KrezcoCargo Trazabilidad YYYY-MM-DD HHMM.xlsx
- Hoja principal: "Movimientos"
- Columnas: Fecha, Tipo, Codigo Producto, Producto, Lote, Cantidad, Unidad, Almacen, Origen, Recepcion N, Packing List N, Ruta/Cliente, Creado Por, Email, Creado En, Referencia
- Filtrar solo tipo="salida"
- 21 productos unicos con codigos (01-001 a 08-003)
- ~79 referencias por archivo
- Cada referencia tiene ~10-17 productos
- Tiempo manual actual: 3-4 horas diarias

## Importante: Matching de Nombres
Los nombres NO coinciden exactamente entre Excel y DALI:
- Excel: "GRANOLA SABOR CHOCOPASAS"
- DALI: "GRANOLA DE CEREALES CHOCOPASAS FUNDA"
- Se requiere matching fuzzy (fuzzywuzzy)
- Hay un archivo mapping.json que guarda matches exitosos para reusar

## Como funciona DALI

### Login
POST a https://sistemapae.nutri.com.ec/login/ con:
- user_name=azapata
- user_password=1753112158
- submit=""
Retorna cookie secured_session_id

### Navegacion
El menu se carga dinamicamente en #mainMenu via JavaScript.
Las paginas se cargan via jQuery .load() en #mainBox.
URL de pages: /?option=load&module=logistica&file=<nombre>&type=html
URL de JS: /?option=load&module=logistica&file=<nombre>&type=js

### Pagina clave: Procesar Egreso por Ruta
URL: /?option=load&module=logistica&file=procesaregresohojaruta&type=html
JS: /?option=load&module=logistica&file=procesaregresohojaruta&type=js

### API JSON - Endpoints importantes
Todos van a POST /?option=json con parametro "json" = ID del endpoint

| json ID | Funcion | Parametros | Response |
|---------|---------|------------|----------|
| 2093 | Lista egresos generados | (ninguno) | Lista con EGRESO, FECHA, BODEGA, ORDEN, DIA, TRANSPORTE, HOJARUTA, ESTADO, RESPONSABLE, OBSERVACION, MBO_CODIGO |
| 2091 | Carga datos de un egreso | mbocodigo | MBOCODIGO, SECUENCIAL, FECHA, BODEGA, ORDEN, DIA, PLACA, DESCRIPCIONTRANSPORTE, HOJARUTA, DESCRIPCIONHOJARUTA, RESPONSABLE, ESTADO, OBSERVACION, DCAESTADO |
| 2094 | Carga productos de un egreso | mbocodigo | GRUPO, PRODUCTO, CANTIDAD, SALDO, DMB_CODIGO, PGE_CODIGO, PES_CODIGO |
| 2092 | Carga lotes disponibles | dmbcodigo | Lista de lotes con V (value) y T (text) para combo |
| 2095 | Carga lotes asignados | mbocodigo, pgecodigo, pescodigo | LOTE, CANTIDAD, DMB_CODIGO, ILO_CODIGO |
| 2096 | ASIGNA lote a producto | dmborigen, dmbdestino, ilocodigo, cantidad | {MSG: "ok"} |
| 2097 | Elimina lote asignado | dmborigen, dmbdestino | {MSG: "ok"} |
| 2099 | Procesa/finaliza egreso | mbocodigo | {MSG: "ok"} |

### Filtro de busqueda por Hoja de Ruta
El FlexiGrid de egresos tiene un combo de filtro con opciones:
- EGRESO (EGR)
- BODEGA (BOD)
- ORDEN (ORD) - default
- TRANSPORTE (TRA)
- HOJA RUTA (HOJ)

IMPORTANTE: La referencia del Excel son los ULTIMOS 5 DIGITOS de la Hoja de Ruta en DALI.
Ejemplo: Referencia 21222 = Hoja de Ruta que termina en 21222

### Flujo automatizado completo
1. Login a DALI (requests.Session)
2. GET json 2093 para listar egresos
3. Para cada referencia del Excel:
   a. Buscar en la lista el egreso cuya HOJARUTA termina en la referencia
   b. POST json 2091 con mbocodigo para cargar datos
   c. POST json 2094 para cargar productos
   d. Para cada producto del egreso:
      - Hacer match con producto del Excel
      - POST json 2092 para ver lotes disponibles
      - Seleccionar lote (el del Excel si existe, sino el primero con stock)
      - POST json 2096 para asignar lote + cantidad
   e. POST json 2099 para finalizar el egreso
4. Generar reporte

## Lo que se hizo hasta ahora
1. Repositorio creado: https://github.com/djtechcool-create/LOTES-AUTOMATICOS
2. Git configurado en PC del trabajo
3. .gitignore configurado
4. Investigacion completa de DALI:
   - Login exitoso via requests
   - Menu completo mapeado (36 items)
   - JS de Procesar Egreso descargado y analizado
   - JS de Generar Egreso descargado y analizado
   - core.js descargado y analizado
   - Todos los endpoints JSON identificados
5. Excel analizado (21 productos, 79 referencias)
6. Archivos de investigacion guardados:
   - dali_procesar_egreso.js (el mas importante)
   - dali_generar_egreso.js
   - dali_core.js
   - dali_egresos.html
   - dali_generar_egresos.html
   - dali_menu.html
   - read_excel.py (analisis del Excel)

## Que DEBE hacer el asistente ahora
1. LEER este archivo para entender todo el contexto
2. LEER los archivos de investigacion (dali_procesar_egreso.js es el mas importante)
3. IMPLEMENTAR la app:
   - automator/dali_client.py: Cliente API DALI (login + llamadas JSON)
   - automator/excel_reader.py: Lee Excel del dia
   - automator/matcher.py: Matching fuzzy productos Excel vs DALI
   - automator/report.py: Genera reportes
   - app.py: Flask server con interfaz web
   - templates/index.html: Interfaz amigable
   - config.py: Credenciales
   - requirements.txt: Dependencias
   - iniciar.bat: Para ejecutar facil
4. PROBAR con el Excel de hoy
5. Hacer commit y push

## Notas del Usuario
- No quiere hacer nada manual, prefiere que la PC haga todo
- Trabaja desde la PC del trabajo y la de casa
- En casa usa otra cuenta de OpenCode
- Procesa 40-50 referencias diarias
- Tiempo manual: 3-4 horas
- Meta: reducir a 20-30 min
- El usuario solo quiere revisar los errores al final

## Comandos Utiles
- git pull: bajar cambios del repositorio
- git add .: agregar todos los cambios
- git commit -m "mensaje": guardar cambios
- git push: subir cambios a GitHub
