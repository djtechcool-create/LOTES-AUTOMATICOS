from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://sistemapae.nutri.com.ec/")
    time.sleep(3)
    
    # Login
    driver.find_element(By.ID, "inputUser").send_keys("azapata")
    driver.find_element(By.ID, "inputClave").send_keys("1753112158")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)
    
    print(f"URL: {driver.current_url}")
    
    # Get the menu content (loaded dynamically)
    main_menu = driver.find_element(By.ID, "mainMenu")
    menu_html = main_menu.get_attribute("innerHTML")
    
    with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_menu.html", "w", encoding="utf-8") as f:
        f.write(menu_html)
    print(f"Menu guardado ({len(menu_html)} chars)")
    
    # Print all menu items
    links = main_menu.find_elements(By.TAG_NAME, "a")
    print(f"\n=== MENU ITEMS ({len(links)}) ===")
    for link in links:
        text = link.text.strip()
        onclick = link.get_attribute("onclick") or ""
        href = link.get_attribute("href") or ""
        data_bs = link.get_attribute("data-bs-target") or ""
        if text:
            print(f"  '{text}' | onclick={onclick[:100]} | href={href[:80]} | target={data_bs}")

    # Also get the full page source (with JS rendered)
    page = driver.page_source
    with open(r"C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_full.html", "w", encoding="utf-8") as f:
        f.write(page)
    print("\nPagina completa guardada en dali_full.html")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nNavegador abierto. Cerrando en 10 seg...")
time.sleep(10)
driver.quit()
