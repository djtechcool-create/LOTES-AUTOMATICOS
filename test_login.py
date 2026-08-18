import requests

session = requests.Session()

# Get login page
print("1. Obteniendo pagina de login...")
r1 = session.get("https://sistemapae.nutri.com.ec/")
print(f"   Cookies: {dict(session.cookies)}")

# Try login with new password
print("\n2. Enviando login...")
login_data = {
    "user_name": "azapata",
    "user_password": "1753112158",
    "submit": ""
}
r2 = session.post(
    "https://sistemapae.nutri.com.ec/login/",
    data=login_data,
    headers={"Referer": "https://sistemapae.nutri.com.ec/"},
    allow_redirects=True
)
print(f"   Status: {r2.status_code}")
print(f"   URL final: {r2.url}")

if "inputUser" in r2.text:
    print("   Login FALLIDO")
    # Save for inspection
    with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_login_fail2.html", "w", encoding="utf-8") as f:
        f.write(r2.text)
else:
    print("   Login EXITOSO!")
    with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_dashboard.html", "w", encoding="utf-8") as f:
        f.write(r2.text)
    print("   Dashboard guardado")
    
    # Explore the dashboard
    print("\n3. Explorando dashboard...")
    import re
    # Find all links
    links = re.findall(r'href="([^"]*)"', r2.text)
    print(f"   Links encontrados: {len(links)}")
    for link in links[:30]:
        print(f"     {link}")
    
    # Find all JS files
    scripts = re.findall(r'src="([^"]*\.js)"', r2.text)
    print(f"\n   Scripts: {len(scripts)}")
    for s in scripts[:10]:
        print(f"     {s}")
