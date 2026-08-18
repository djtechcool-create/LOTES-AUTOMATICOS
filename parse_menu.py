import re

with open(r'C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\dali_menu.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all data-url attributes
urls = re.findall(r'data-url="([^"]+)"', html)
print("=== URLs ENCONTRADAS ===")
for u in urls:
    u = u.replace('&amp;', '&')
    print(f"  {u}")

# Extract all text items  
texts = re.findall(r'nav-link-text ps-1">([^<]+)<', html)
print(f"\n=== TEXTOS DEL MENU ({len(texts)}) ===")
for t in texts:
    print(f"  {t}")

# Extract nav items with their IDs
items = re.findall(r'<li class="nav-item" id="([^"]+)"', html)
print(f"\n=== NAV ITEMS ({len(items)}) ===")
for i in items:
    print(f"  {i}")
