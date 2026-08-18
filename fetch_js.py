import requests
import re

session = requests.Session()

# Login
r1 = session.get("https://sistemapae.nutri.com.ec/")
login_data = {"user_name": "azapata", "user_password": "1753112158", "submit": ""}
r2 = session.post("https://sistemapae.nutri.com.ec/login/", data=login_data,
    headers={"Referer": "https://sistemapae.nutri.com.ec/"}, allow_redirects=True)
print(f"Login: {'OK' if 'inputUser' not in r2.text else 'FAIL'}")

# Fetch the page-specific JS for Procesar Egreso
print("\n=== JS Procesar Egreso ===")
r3 = session.get("https://sistemapae.nutri.com.ec/?option=load&module=logistica&file=procesaregresohojaruta&type=js",
    headers={"Referer": "https://sistemapae.nutri.com.ec/"})
print(f"Status: {r3.status_code}, Size: {len(r3.text)}")
with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_procesar_egreso.js", "w", encoding="utf-8") as f:
    f.write(r3.text)

# Fetch the page-specific JS for Generar Egreso
print("\n=== JS Generar Egreso ===")
r4 = session.get("https://sistemapae.nutri.com.ec/?option=load&module=logistica&file=generaregresohojaruta&type=js",
    headers={"Referer": "https://sistemapae.nutri.com.ec/"})
print(f"Status: {r4.status_code}, Size: {len(r4.text)}")
with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_generar_egreso.js", "w", encoding="utf-8") as f:
    f.write(r4.text)

# Find json IDs in both files
for fname, content in [("Procesar", r3.text), ("Generar", r4.text)]:
    json_ids = re.findall(r'json["\s:=]+(\d+)', content)
    print(f"\n{fname} - JSON IDs: {set(json_ids)}")
    
    # Find getJson calls
    getjson_calls = re.findall(r'getJson\([^)]+\)', content)
    print(f"{fname} - getJson calls: {len(getjson_calls)}")
    for call in getjson_calls[:10]:
        print(f"  {call[:150]}")
    
    # Find guardarFormulario calls
    save_calls = re.findall(r'guardar(?:Formulario|ObjetoData)\([^)]+\)', content)
    print(f"{fname} - save calls: {len(save_calls)}")
    for call in save_calls[:5]:
        print(f"  {call[:150]}")
    
    # Find llenaCombo calls
    combo_calls = re.findall(r'llenaCombo\([^)]+\)', content)
    print(f"{fname} - llenaCombo calls: {len(combo_calls)}")
    for call in combo_calls[:10]:
        print(f"  {call[:150]}")
