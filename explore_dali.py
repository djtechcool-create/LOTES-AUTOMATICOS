from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("=== PASO 1: Ir a DALI ===")
    driver.get("https://sistemapae.nutri.com.ec/")
    time.sleep(3)
    print(f"URL: {driver.current_url}")
    
    if "inputUser" in driver.page_source:
        print("Pagina de login detectada")
        
        user_input = driver.find_element(By.ID, "inputUser")
        pass_input = driver.find_element(By.ID, "inputClave")
        user_input.clear()
        user_input.send_keys("azapata")
        pass_input.clear()
        pass_input.send_keys("azapata123")
        time.sleep(1)
        
        # Click the button directly (not form.submit because button name="submit" overrides it)
        print("Clickeando boton Ingresar...")
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(8)
        
        print(f"URL despues del login: {driver.current_url}")
        
        page_source = driver.page_source
        if "inputUser" in page_source:
            print("ERROR: Sigue en login. Guardando pagina...")
            with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_login_fail.html", "w", encoding="utf-8") as f:
                f.write(page_source)
        else:
            print("LOGIN EXITOSO!")
            with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_dashboard.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            
            # Explore menu
            print("\n=== BUSCANDO MENU/NAVEGACION ===")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                text = link.text.strip()
                href = link.get_attribute("href") or ""
                classes = link.get_attribute("class") or ""
                if text and len(text) < 100:
                    print(f"  [{classes[:40]}] '{text}' -> {href[:100]}")
    else:
        print("No se detecto login, posible sesion activa")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nScript terminado. Navegador sigue abierto.")
time.sleep(600)
