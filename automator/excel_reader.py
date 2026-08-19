import pandas as pd
import os
import glob


def find_excel(excel_dir="."):
    pattern = os.path.join(excel_dir, "KrezcoCargo Trazabilidad *.xlsx")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not files:
        raise FileNotFoundError(
            f"No se encontro archivo Excel en {excel_dir} con patron 'KrezcoCargo Trazabilidad *.xlsx'"
        )
    return files[0]


def read_excel(filepath):
    xl = pd.ExcelFile(filepath)
    df = pd.read_excel(xl, sheet_name="Movimientos", header=None)
    headers = df.iloc[3].tolist()
    df = df.iloc[4:].copy()
    df.columns = headers
    df = df.reset_index(drop=True)
    df_salidas = df[df["Tipo"] == "salida"].copy().reset_index(drop=True)
    return df_salidas


def get_references(df_salidas):
    refs = df_salidas["Referencia"].dropna().unique()
    return [str(r) for r in refs]


def get_references_with_dates(df_salidas):
    grouped = df_salidas.groupby("Referencia")
    result = []
    for ref, group in grouped:
        fecha = group["Fecha"].iloc[0]
        if pd.notna(fecha):
            try:
                fecha_str = pd.to_datetime(fecha).strftime("%d/%m/%Y")
            except Exception:
                fecha_str = str(fecha)
        else:
            fecha_str = ""
        result.append({"ref": str(ref), "date": fecha_str})
    return result


def get_products_for_reference(df_salidas, referencia):
    ex = df_salidas[df_salidas["Referencia"].astype(str) == referencia].copy()
    products = {}
    for _, row in ex.iterrows():
        nombre = str(row["Producto"]).strip().upper()
        lote_raw = row["Lote"] if pd.notna(row["Lote"]) else None
        if lote_raw is not None:
            lote_str = str(lote_raw).strip()
            lote = lote_str if lote_str else None
        else:
            lote = None
        cantidad = int(row["Cantidad"])
        if nombre in products:
            prev_lote, prev_cant = products[nombre]
            products[nombre] = (lote, prev_cant + cantidad)
        else:
            products[nombre] = (lote, cantidad)
    return products


def get_all_products_map(df_salidas):
    products = df_salidas[["C\u00f3digo Producto", "Producto"]].drop_duplicates()
    result = {}
    for _, row in products.iterrows():
        result[str(row["C\u00f3digo Producto"])] = str(row["Producto"]).strip().upper()
    return result
