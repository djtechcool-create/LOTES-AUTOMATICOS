import requests

session = requests.Session()

# Login
print("1. Login...")
r1 = session.get("https://sistemapae.nutri.com.ec/")
login_data = {"user_name": "azapata", "user_password": "1753112158", "submit": ""}
r2 = session.post(
    "https://sistemapae.nutri.com.ec/login/",
    data=login_data,
    headers={"Referer": "https://sistemapae.nutri.com.ec/"},
    allow_redirects=True
)
print(f"Login OK: {'inputUser' not in r2.text}")

# Navigate to Procesar Egreso por Ruta
print("\n2. Accediendo a Procesar Egreso por Ruta...")
r3 = session.get(
    "https://sistemapae.nutri.com.ec/?option=load&module=logistica&file=procesaregresohojaruta&type=html",
    headers={"Referer": "https://sistemapae.nutri.com.ec/"}
)
print(f"Status: {r3.status_code}, Size: {len(r3.text)}")

with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_egresos.html", "w", encoding="utf-8") as f:
    f.write(r3.text)
print("Pagina guardada en dali_egresos.html")

# Also try Generar Egreso por Ruta
print("\n3. Accediendo a Generar Egreso por Ruta...")
r4 = session.get(
    "https://sistemapae.nutri.com.ec/?option=load&module=logistica&file=generaregresohojaruta&type=html",
    headers={"Referer": "https://sistemapae.nutri.com.ec/"}
)
print(f"Status: {r4.status_code}, Size: {len(r4.text)}")

with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_generar_egresos.html", "w", encoding="utf-8") as f:
    f.write(r4.text)
print("Pagina guardada en dali_generar_egresos.html")

# Get core.js to understand loadContent and menu logic
print("\n4. Obteniendo core.js...")
r5 = session.get(
    "https://sistemapae.nutri.com.ec/?option=load&module=core&file=core&type=js",
    headers={"Referer": "https://sistemapae.nutri.com.ec/"}
)
print(f"core.js status: {r5.status_code}, size: {len(r5.text)}")
with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_core.js", "w", encoding="utf-8") as f:
    f.write(r5.text)
print("core.js guardado")
