import os
import sys
import json
import threading
import queue
import time
import glob
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, Response
from config import FLASK_HOST, FLASK_PORT, EXCEL_DIR
from automator.dali_client import DaliClient
from automator.excel_reader import find_excel, read_excel, get_references, get_products_for_reference
from automator.matcher import match_product, find_reference_in_egresos
from automator.report import generate_report

app = Flask(__name__)

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

    try:
        log_callback("=== INICIANDO PROCESAMIENTO DE EGRESOS ===")

        log_callback(f"Leyendo Excel: {os.path.basename(excel_path)}")
        df = read_excel(excel_path)
        all_refs = get_references(df)
        log_callback(f"Referencias encontradas: {len(all_refs)}")

        if selected_refs:
            refs = [r for r in all_refs if r in selected_refs]
            log_callback(f"Filtradas {len(refs)} referencias seleccionadas")
        else:
            refs = all_refs

        log_callback("Conectando a DALI...")
        client = DaliClient(on_log=log_callback)
        if not client.login():
            raise Exception("No se pudo iniciar sesion en DALI")

        log_callback("Listando egresos en DALI...")
        egresos = client.listar_egresos()

        results = []
        state["progress"]["total"] = len(refs)

        for i, ref in enumerate(refs):
            state["progress"]["current"] = i + 1
            state["progress"]["current_ref"] = ref
            state["queue"].put(("progress", state["progress"]))

            log_callback(f"\n--- Procesando referencia {ref} ({i+1}/{len(refs)}) ---")

            excel_products = get_products_for_reference(df, ref)
            log_callback(f"  Productos en Excel: {len(excel_products)}")

            egreso = find_reference_in_egresos(ref, egresos)
            if not egreso:
                log_callback(f"  ERROR: No se encontro egreso con Hoja de Ruta que termine en {ref}")
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "Egreso no encontrado en DALI",
                })
                continue

            mbo_codigo = egreso.get("MBO_CODIGO", "")
            log_callback(f"  Egreso encontrado: MBO_CODIGO={mbo_codigo}, Hoja Ruta={egreso.get('HOJARUTA', '')}")

            egreso_data = client.cargar_egreso(mbo_codigo)
            if egreso_data:
                dcaestado = egreso_data[0].get("DCAESTADO")
                if str(dcaestado) == "23":
                    log_callback("  El egreso ya esta PROCESADO, saltando...")
                    results.append({
                        "referencia": ref,
                        "status": "skip",
                        "error": "Egreso ya procesado",
                        "egreso_code": mbo_codigo,
                    })
                    continue

            dali_products = client.cargar_productos(mbo_codigo)
            if not dali_products:
                log_callback(f"  ERROR: No se encontraron productos en DALI para egreso {mbo_codigo}")
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "No hay productos en DALI",
                    "egreso_code": mbo_codigo,
                })
                continue

            dali_names = [p["PRODUCTO"] for p in dali_products]
            result_detail = []
            fail_detail = []
            assigned_count = 0

            for excel_name, (excel_lote, excel_cant) in excel_products.items():
                match_name, score, method = match_product(excel_name, dali_names)
                log_callback(f"  Excel: {excel_name} -> DALI: {match_name} (score={score}, {method})")

                if match_name is None:
                    fail_detail.append({"excel": excel_name, "error": "Sin match fuzzy"})
                    continue

                dali_prod = next((p for p in dali_products if p["PRODUCTO"] == match_name), None)
                if not dali_prod:
                    fail_detail.append({"excel": excel_name, "error": "Producto no encontrado en egreso"})
                    continue

                dmb_codigo = dali_prod["DMB_CODIGO"]
                pge_codigo = dali_prod["PGE_CODIGO"]
                pes_codigo = dali_prod["PES_CODIGO"]

                available_lotes = client.cargar_lotes_disponibles(dmb_codigo)
                log_callback(f"  Lotes disponibles: {len(available_lotes)}")

                if not available_lotes:
                    log_callback(f"  WARNING: No hay lotes disponibles para {match_name}")
                    fail_detail.append({"excel": excel_name, "error": "Sin lotes disponibles"})
                    continue

                chosen_lote = None
                chosen_ilocodigo = None

                if excel_lote:
                    excel_lote_str = str(excel_lote).strip()
                    for lote in available_lotes:
                        if str(lote.get("V", "")).strip() == excel_lote_str or excel_lote_str in str(lote.get("T", "")):
                            chosen_lote = lote.get("T", lote.get("V", ""))
                            chosen_ilocodigo = lote.get("V", "")
                            break

                if chosen_lote is None:
                    chosen_lote = available_lotes[0].get("T", "")
                    chosen_ilocodigo = available_lotes[0].get("V", "")

                log_callback(f"  Lote seleccionado: {chosen_lote} (ilocodigo={chosen_ilocodigo})")

                ok = client.asignar_lote(
                    dmborigen=dmb_codigo,
                    dmbdestino=dmb_codigo,
                    ilocodigo=chosen_ilocodigo,
                    cantidad=excel_cant,
                )

                if ok:
                    assigned_count += 1
                    result_detail.append({
                        "excel": excel_name,
                        "dali": match_name,
                        "score": score,
                        "lote": chosen_lote,
                        "cantidad": excel_cant,
                    })
                else:
                    fail_detail.append({"excel": excel_name, "error": "Error al asignar lote"})

            log_callback(f"  Asignados: {assigned_count}/{len(excel_products)}")

            if assigned_count > 0:
                log_callback(f"  Procesando egreso {mbo_codigo}...")
                proc_ok = client.procesar_egreso(mbo_codigo)
                if proc_ok:
                    results.append({
                        "referencia": ref,
                        "status": "ok",
                        "egreso_code": mbo_codigo,
                        "productos_asignados": assigned_count,
                        "productos_detallado": result_detail,
                    })
                else:
                    results.append({
                        "referencia": ref,
                        "status": "error",
                        "error": "Error al procesar egreso",
                        "egreso_code": mbo_codigo,
                        "productos_fallidos": fail_detail,
                    })
            else:
                results.append({
                    "referencia": ref,
                    "status": "error",
                    "error": "Ningun producto pudo ser asignado",
                    "egreso_code": mbo_codigo,
                    "productos_fallidos": fail_detail,
                })

        log_callback("\n=== GENERANDO REPORTE ===")
        report_path, report_content = generate_report(results, os.path.basename(excel_path))
        log_callback(f"Reporte guardado en: {report_path}")

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


@app.route("/api/excels")
def list_excels():
    pattern = os.path.join(EXCEL_DIR, "KrezcoCargo Trazabilidad *.xlsx")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    result = []
    for f in files:
        result.append({"name": os.path.basename(f), "path": f, "size": os.path.getsize(f)})
    return jsonify(result)


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
                    yield f"data: {json.dumps({'type': 'done', 'data': {'report_path': msg_data.get('report_path', '')}})}\n\n"
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
