import os
from datetime import datetime


def generate_report(results, excel_file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reportes")
    os.makedirs(report_dir, exist_ok=True)

    procesados = [r for r in results if r["status"] == "ok"]
    saltados = [r for r in results if r["status"] == "skip"]
    fallidos = [r for r in results if r["status"] == "error"]
    revision = [r for r in results if r["status"] == "review"]

    # === REPORTE GENERAL ===
    general_path = os.path.join(report_dir, f"reporte_{timestamp}.txt")
    general_lines = []
    general_lines.append("=" * 60)
    general_lines.append(f"REPORTE GENERAL - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    general_lines.append(f"Excel: {os.path.basename(excel_file)}")
    general_lines.append("=" * 60)
    general_lines.append("")
    general_lines.append("RESUMEN:")
    general_lines.append(f"  OK:        {len(procesados)} egresos ({sum(r.get('productos_asignados',0) for r in procesados)} productos)")
    general_lines.append(f"  ERRORES:   {len(fallidos)} egresos")
    general_lines.append(f"  SALTADOS:  {len(saltados)} egresos (ya procesados)")
    general_lines.append(f"  REVISAR:   {len(revision)} egresos (asignados sin procesar)")
    general_lines.append("")

    if fallidos:
        general_lines.append("-" * 60)
        general_lines.append("ERRORES DETALLADOS:")
        general_lines.append("-" * 60)
        for r in fallidos:
            general_lines.append("")
            general_lines.append(f"  Egreso {r.get('egreso_code','?')} - Ref {r['referencia']}:")
            general_lines.append(f"    Error general: {r.get('error','?')}")
            if "productos_fallidos" in r and r["productos_fallidos"]:
                general_lines.append(f"    Productos con error:")
                for pf in r["productos_fallidos"]:
                    general_lines.append(f"      - {pf.get('excel','?')} -> {pf.get('dali','?')} (DMB={pf.get('dmb','?')})")
                    general_lines.append(f"        Error: {pf.get('error','?')}")
                    if pf.get("lote"):
                        general_lines.append(f"        Lote intentado: {pf['lote']}")
            if "sin_stock" in r and r["sin_stock"]:
                general_lines.append(f"    Productos sin lote o sin stock:")
                for ss in r["sin_stock"]:
                    general_lines.append(f"      - {ss.get('excel','?')} -> {ss.get('dali','?')} (DMB={ss.get('dmb','?')})")
                    general_lines.append(f"        Razon: {ss.get('error','?')}")
        general_lines.append("")

    if revision:
        general_lines.append("-" * 60)
        general_lines.append("REVISAR (requieren procesamiento manual):")
        general_lines.append("-" * 60)
        for r in revision:
            general_lines.append(f"  Egreso {r.get('egreso_code','?')} - Ref {r['referencia']}")
        general_lines.append("")

    if procesados:
        general_lines.append("-" * 60)
        general_lines.append("OK:")
        general_lines.append("-" * 60)
        for r in procesados:
            general_lines.append(f"  Ref {r['referencia']} - Egreso {r.get('egreso_code','?')} ({r.get('productos_asignados',0)} productos)")

    if saltados:
        general_lines.append("")
        general_lines.append("-" * 60)
        general_lines.append(f"SALTADOS ({len(saltados)} - ya procesados):")
        general_lines.append("-" * 60)
        for r in saltados:
            general_lines.append(f"  Ref {r['referencia']}")

    general_lines.append("")
    general_content = "\n".join(general_lines)
    with open(general_path, "w", encoding="utf-8") as f:
        f.write(general_content)

    # === REPORTE DE ERRORES ===
    error_path = os.path.join(report_dir, f"reporte_errores_{timestamp}.txt")
    error_lines = []
    error_lines.append("=" * 60)
    error_lines.append(f"REPORTE DE ERRORES - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    error_lines.append(f"Excel: {os.path.basename(excel_file)}")
    error_lines.append("=" * 60)

    if fallidos:
        for r in fallidos:
            error_lines.append("")
            error_lines.append(f"EGRESO {r.get('egreso_code','?')} - Ref {r['referencia']}")
            error_lines.append(f"  Error: {r.get('error','?')}")
            if "productos_fallidos" in r and r["productos_fallidos"]:
                error_lines.append(f"  Detalle por producto:")
                for pf in r["productos_fallidos"]:
                    error_lines.append(f"")
                    error_lines.append(f"    Producto Excel:  {pf.get('excel','?')}")
                    error_lines.append(f"    Producto DALI:   {pf.get('dali','?')}")
                    error_lines.append(f"    Codigo DMB:     {pf.get('dmb','?')}")
                    error_lines.append(f"    Lote intentado: {pf.get('lote','N/A')}")
                    error_lines.append(f"    Error:          {pf.get('error','?')}")
                    error_lines.append(f"    Accion:         Producto sin asignar")
            if "sin_stock" in r and r["sin_stock"]:
                error_lines.append(f"  Productos sin lote/disponibles:")
                for ss in r["sin_stock"]:
                    error_lines.append(f"")
                    error_lines.append(f"    Producto Excel:  {ss.get('excel','?')}")
                    error_lines.append(f"    Producto DALI:   {ss.get('dali','?')}")
                    error_lines.append(f"    Codigo DMB:     {ss.get('dmb','?')}")
                    error_lines.append(f"    Razon:          {ss.get('error','?')}")
                    error_lines.append(f"    Accion:         Producto saltado")
    else:
        error_lines.append("")
        error_lines.append("No hubo errores.")

    error_lines.append("")
    error_content = "\n".join(error_lines)
    with open(error_path, "w", encoding="utf-8") as f:
        f.write(error_content)

    # === REPORTE DE EXITOS ===
    ok_path = os.path.join(report_dir, f"reporte_ok_{timestamp}.txt")
    ok_lines = []
    ok_lines.append("=" * 60)
    ok_lines.append(f"REPORTE DE EXITOS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    ok_lines.append(f"Excel: {os.path.basename(excel_file)}")
    ok_lines.append("=" * 60)

    total_productos = 0
    for r in procesados:
        ok_lines.append("")
        ok_lines.append(f"EGRESO {r.get('egreso_code','?')} - Ref {r['referencia']}")
        detail = r.get("productos_detalle", [])
        for d in detail:
            total_productos += 1
            ok_lines.append(f"  {d.get('excel','?')}")
            ok_lines.append(f"    Excel: {d.get('lote_excel','?')}  ->  DALI: {d.get('lote_dali','?')}  (OK)")
        ok_lines.append(f"  Total: {len(detail)} productos")

    ok_lines.append("")
    ok_lines.append("-" * 60)
    ok_lines.append(f"RESUMEN: {total_productos} productos OK en {len(procesados)} egresos")
    ok_lines.append("-" * 60)
    ok_lines.append("")
    ok_content = "\n".join(ok_lines)
    with open(ok_path, "w", encoding="utf-8") as f:
        f.write(ok_content)

    return general_path, general_content
