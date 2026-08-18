import pandas as pd

xl = pd.ExcelFile(r'C:\Users\ELTIOZAP\OneDrive - Krezcocargo SAS\OTRO\APPS\LASF\KrezcoCargo Trazabilidad 2026-08-18 1400.xlsx')
df = pd.read_excel(xl, sheet_name='Movimientos', header=None)

# Use row 3 as header
headers = df.iloc[3].tolist()
df = df.iloc[4:].copy()
df.columns = headers
df = df.reset_index(drop=True)

# Filter only salidas
df_salidas = df[df['Tipo'] == 'salida'].copy()

# Get unique references (exclude header)
refs = df_salidas['Referencia'].dropna().unique()
print(f'Total referencias unicas: {len(refs)}')

# Show example for first real reference
sample_ref = str(refs[0])
print(f'\n--- EJEMPLO REFERENCIA {sample_ref} ---')
sample = df_salidas[df_salidas['Referencia'].astype(str) == sample_ref]
print(sample[['C\u00f3digo Producto', 'Producto', 'Lote', 'Cantidad', 'Ruta/Cliente']].to_string())

# Show all products and their codes
print(f'\n--- MAPA DE PRODUCTOS ---')
products = df_salidas[['C\u00f3digo Producto', 'Producto']].drop_duplicates()
for _, row in products.iterrows():
    print(f'  {row["C\u00f3digo Producto"]} -> {row["Producto"]}')
