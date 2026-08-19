import os
from datetime import datetime


def generate_report(results, excel_file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reportes")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"reporte_{timestamp}.txt")

    lines = []
    lines.append(f"REPORTE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Excel: {os.path.basename(excel_file)}")

    procesados = [r for r in results if r["status"] == "ok"]
    saltados = [r for r in results if r["status"] == "skip"]
    fallidos = [r for r in results if r["status"] == "error"]

    lines.append(f"\nOK: {len(procesados)} | SALTADOS: {len(saltados)} | ERRORES: {len(fallidos)}")

    if procesados:
        lines.append(f"\n--- OK ---")
        for r in procesados:
            lines.append(f"  {r['referencia']} ({r.get('productos_asignados',0)} productos)")

    if fallidos:
        lines.append(f"\n--- ERRORES ---")
        for r in fallidos:
            lines.append(f"\n  {r['referencia']}: {r.get('error','?')}")
            if "productos_fallidos" in r:
                for pf in r["productos_fallidos"]:
                    lines.append(f"    - {pf['excel']}: {pf.get('error','?')}")

    if saltados:
        lines.append(f"\n--- SALTADOS (ya procesados) ---")
        for r in saltados:
            lines.append(f"  {r['referencia']}")

    lines.append("")
    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return report_path, content
