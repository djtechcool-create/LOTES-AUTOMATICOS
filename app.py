import os
import sys
import json
import threading
import queue
import time
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, Response
from config import FLASK_HOST, FLASK_PORT
from automator.dali_client import DaliClient
from automator.excel_reader import read_excel, get_references, get_products_for_reference
from automator.matcher import match_product
from automator.report import generate_report

app = Flask(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "excels")
os.makedirs(UPLOAD_DIR, exist_ok=True)

processing_state = {
    "running": False,
    "logs": [],
    "progress": {"current": 0, "total": 0, "current_ref": ""},
    "result": None,
    "queue": queue.Queue(),
}


def log_callback(msg):
    processing_state["logs"].append(msg)
    processing_state["queue"].put(("log", msg))


def process_egresos(excel_path, selected_refs=None):
    state = processing_state
    state["running"] = True
    state["logs"] = []
    state["progress"] = {"current": 0, "total": 0, "current_ref": ""}
    state["result"] = None

    client = None
    try:
        log_callback("=== INICIANDO PROCESAMIENTO DE EGRESOS ===")
        log_callback(f"Archivo: {os.path.basename(excel_path)}")

        log_callback("Abriendo Google Chrome...")
        client = DaliClient(on_log=log_callback)
        client.start_browser()

        log_callback("Ingresando a DALI...")
        if not client.login():
            raise Exception("No se pudo iniciar sesion en DALI")

        log_callback("Cargando pagina de Procesar Egreso por Ruta...")
        client.navigate_to_egresos()

        log_callback("Leyendo Excel...")
        df = read_excel(excel_path)
        all_refs = get_references(df)
        log_callback(f"Referencias en Excel: {len(all_refs)}")

        if selected_refs:
            refs = [r for r in all_refs if r in selected_refs]
            log_callback(f"Filtradas {len(refs)} referencias seleccionadas")
        else:
            refs = all_refs

        results = []
        state["progress"]["total"] = len(refs)

        for i, ref in enumerate(refs):
            state["progress"]["current"] = i + 1
            state["progress"]["current_ref"] = ref
            state["queue"].put(("progress", state["progress"]))

            log_callback(f"\n--- Referencia {ref} ({i+1}/{len(refs)}) ---")

            excel_products = get_products_for_reference(df, ref)
            log_callback(f"  Productos en Excel: {len(excel_products)}")

            # Buscar egreso en el grid (ya cargado)
            found = client.buscar_y_seleccionar_egreso(ref)
            if not found:
                log_callback(f"  ERROR: No se encontro egreso con HR={ref}")
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "Egreso no encontrado en DALI",
                })
                continue

            # Leer datos del egreso cargado
            egreso = client.get_egreso_actual()
            mbo_codigo = egreso["mbocodigo"]
            log_callback(f"  Egreso cargado: MBO={mbo_codigo} HR={egreso['hojaruta']}")

            if str(egreso.get("estado", "")).upper() == "PROCESADO":
                log_callback("  Ya PROCESADO, saltando...")
                results.append({
                    "referencia": ref,
                    "status": "skip",
                    "error": "Ya procesado",
                    "egreso_code": mbo_codigo,
                })
                continue

            # Cargar productos del egreso
            dali_products = client.cargar_productos_egreso(mbo_codigo)
            if not dali_products:
                log_callback("  ERROR: Sin productos en el egreso")
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "Sin productos",
                    "egreso_code": mbo_codigo,
                })
                continue

            dali_names = [p["PRODUCTO"] for p in dali_products]
            assigned_count = 0
            result_detail = []
            fail_detail = []
            sin_stock_detail = []

            for excel_name, (excel_lote, excel_cant) in excel_products.items():
                match_name, score, method = match_product(excel_name, dali_names)
                log_callback(f"  {excel_name} -> {match_name} ({score}%, {method})")

                if match_name is None:
                    fail_detail.append({"excel": excel_name, "error": "Sin match"})
                    continue

                matching_prods = [p for p in dali_products if p["PRODUCTO"] == match_name]
                if not matching_prods:
                    fail_detail.append({"excel": excel_name, "error": "No encontrado"})
                    continue

                for dali_prod in matching_prods:
                    dmb = dali_prod["DMB_CODIGO"]
                    pge = dali_prod["PGE_CODIGO"]
                    pes = dali_prod["PES_CODIGO"]
                    saldo = int(dali_prod.get("SALDO", 0) or 0)

                    if saldo <= 0:
                        log_callback(f"    DMB={dmb} SALDO=0, saltando")
                        sin_stock_detail.append({
                            "excel": excel_name, "dali": match_name,
                            "dmb": dmb, "error": "SALDO=0 en DALI"
                        })
                        continue

                    available = client.cargar_lotes_disponibles(dmb)
                    if not available:
                        log_callback(f"    DMB={dmb} Sin lotes disponibles")
                        fail_detail.append({
                            "excel": excel_name, "dali": match_name,
                            "dmb": dmb, "error": "Sin lotes disponibles"
                        })
                        continue

                    chosen_v = None
                    chosen_t = None
                    if not excel_lote:
                        log_callback(f"    DMB={dmb} Sin lote en Excel, saltando")
                        sin_stock_detail.append({
                            "excel": excel_name, "dali": match_name,
                            "dmb": dmb, "error": "Sin lote en Excel"
                        })
                        continue

                    el = str(excel_lote).strip()
                    for lote in available:
                        v = str(lote.get("V", "")).strip()
                        t = str(lote.get("T", ""))
                        if v == el or el in t:
                            chosen_v = v
                            chosen_t = t
                            break

                    if chosen_v is None:
                        log_callback(f"    Lote '{el}' no encontrado en lotes disponibles, saltando")
                        sin_stock_detail.append({
                            "excel": excel_name, "dali": match_name,
                            "dmb": dmb, "error": f"Lote '{el}' no existe en DALI"
                        })
                        continue

                    log_callback(f"    DMB={dmb} Lote: {chosen_t} (Saldo = {saldo}) Cant: {saldo}")
                    ok = client.asignar_lote(dmb, chosen_v, saldo)
                    if ok:
                        assigned_count += 1
                        result_detail.append({
                            "excel": excel_name,
                            "dali": match_name,
                            "dmb": dmb,
                            "score": score,
                            "lote": chosen_t,
                            "cantidad": saldo,
                        })
                    else:
                        fail_detail.append({
                            "excel": excel_name, "dali": match_name,
                            "dmb": dmb, "lote": chosen_t,
                            "error": "Error al asignar lote"
                        })

            log_callback(f"  Asignados: {assigned_count}/{len(excel_products)}")

            all_saldo_cero = len(sin_stock_detail) > 0 and assigned_count == 0 and len(fail_detail) == 0

            if all_saldo_cero:
                log_callback("  >> Todos los productos con SALDO=0. Requiere revision/procesamiento.")
                results.append({
                    "referencia": ref,
                    "status": "review",
                    "error": "Todos los lotes con SALDO=0 - egreso ya tiene lotes asignados, requiere revision y procesamiento",
                    "egreso_code": mbo_codigo,
                    "productos_asignados": 0,
                    "sin_stock": sin_stock_detail,
                })
            elif assigned_count > 0:
                procesado = client.procesar_egreso()
                if procesado and not fail_detail:
                    results.append({
                        "referencia": ref,
                        "status": "ok",
                        "egreso_code": mbo_codigo,
                        "productos_asignados": assigned_count,
                    })
                else:
                    reason = []
                    if not procesado:
                        reason.append("Proceso falllo en DALI")
                    if fail_detail:
                        reason.append(f"{len(fail_detail)} productos con errores")
                    results.append({
                        "referencia": ref,
                        "status": "error",
                        "error": "; ".join(reason),
                        "egreso_code": mbo_codigo,
                        "productos_asignados": assigned_count,
                        "productos_fallidos": fail_detail,
                        "sin_stock": sin_stock_detail,
                    })
            else:
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "Ningun producto asignado",
                    "egreso_code": mbo_codigo,
                    "productos_fallidos": fail_detail,
                    "sin_stock": sin_stock_detail,
                })

        log_callback("\n=== GENERANDO REPORTE ===")
        report_path, report_content = generate_report(results, os.path.basename(excel_path))
        log_callback(f"Reporte: {report_path}")

        state["result"] = {
            "results": results,
            "report_path": report_path,
            "report_content": report_content,
        }
        state["queue"].put(("done", state["result"]))

    except Exception as e:
        log_callback(f"ERROR FATAL: {str(e)}")
        state["result"] = {"error": str(e)}
        state["queue"].put(("error", str(e)))
    finally:
        state["running"] = False
        state["queue"].put(("finished", None))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No se envio archivo"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Nombre vacio"}), 400
    save_path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(save_path)
    return jsonify({"path": save_path, "name": f.filename, "size": os.path.getsize(save_path)})


@app.route("/api/references")
def get_refs():
    excel_path = request.args.get("excel")
    if not excel_path or not os.path.exists(excel_path):
        return jsonify({"error": "Excel no encontrado"}), 400
    try:
        df = read_excel(excel_path)
        refs = get_references(df)
        return jsonify({"references": refs, "count": len(refs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/process", methods=["POST"])
def start_processing():
    if processing_state["running"]:
        return jsonify({"error": "Ya hay un proceso en ejecucion"}), 400

    data = request.json
    excel_path = data.get("excel")
    selected_refs = data.get("refs")

    if not excel_path or not os.path.exists(excel_path):
        return jsonify({"error": "Excel no encontrado"}), 400

    processing_state["queue"] = queue.Queue()
    t = threading.Thread(target=process_egresos, args=(excel_path, selected_refs))
    t.daemon = True
    t.start()
    return jsonify({"status": "started"})


@app.route("/api/status")
def get_status():
    return jsonify({
        "running": processing_state["running"],
        "progress": processing_state["progress"],
        "logs": processing_state["logs"],
        "result": processing_state["result"],
    })


@app.route("/api/stream")
def stream():
    def generate():
        while True:
            try:
                msg_type, msg_data = processing_state["queue"].get(timeout=30)
                if msg_type == "log":
                    yield f"data: {json.dumps({'type': 'log', 'message': msg_data})}\n\n"
                elif msg_type == "progress":
                    yield f"data: {json.dumps({'type': 'progress', 'data': msg_data})}\n\n"
                elif msg_type == "done":
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                elif msg_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': msg_data})}\n\n"
                    break
                elif msg_type == "finished":
                    yield f"data: {json.dumps({'type': 'finished'})}\n\n"
                    break
            except queue.Empty:
                if not processing_state["running"]:
                    yield f"data: {json.dumps({'type': 'finished'})}\n\n"
                    break
                yield f": keepalive\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, threaded=True)
