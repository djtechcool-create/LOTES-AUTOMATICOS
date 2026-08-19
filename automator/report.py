import os
from datetime import datetime


def generate_report(results, excel_file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reportes")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"reporte_{timestamp}.txt")

    lines = []
    lines.append("=" * 70)
    lines.append(f"REPORTE DE EGRESOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Archivo Excel: {excel_file}")
    lines.append("=" * 70)

    procesados = [r for r in results if r["status"] == "ok"]
    no_procesados = [r for r in results if r["status"] != "ok"]

    lines.append(f"\nRESUMEN:")
    lines.append(f"  Total referencias: {len(results)}")
    lines.append(f"  Procesados: {len(procesados)}")
    lines.append(f"  No procesados: {len(no_procesados)}")

    if no_procesados:
        lines.append(f"\n--- REFERENCIAS NO PROCESADAS ---")
        for r in no_procesados:
            lines.append(f"\n  Referencia: {r['referencia']}")
            lines.append(f"  Error: {r.get('error', 'Desconocido')}")
            if "productos_fallidos" in r:
                for pf in r["productos_fallidos"]:
                    lines.append(f"    - {pf['excel']} -> {pf.get('error', 'sin match')}")

    if procesados:
        lines.append(f"\n--- REFERENCIAS PROCESADAS ---")
        for r in procesados:
            lines.append(f"\n  Referencia: {r['referencia']}")
            lines.append(f"  Egreso DALI: {r.get('egreso_code', 'N/A')}")
            lines.append(f"  Productos asignados: {r.get('productos_asignados', 0)}")
            if "productos_detallado" in r:
                for pd_item in r["productos_detallado"]:
                    lines.append(f"    - {pd_item['excel']} -> {pd_item['dali']} (score: {pd_item['score']}, lote: {pd_item.get('lote', 'N/A')})")

    lines.append("\n" + "=" * 70)

    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return report_path, content
