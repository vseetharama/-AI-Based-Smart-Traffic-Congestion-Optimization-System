from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import base64
import os
import time
from threading import Thread
from werkzeug.utils import secure_filename
from shared_state import controller_state, controller_state_lock
from worker import Worker
from traffic_controller import TrafficController
from database import get_database, get_database_name
from analytics import get_history, get_today_summary, get_weekly_summary, get_monthly_summary
from reports import build_pdf_report, build_csv_report

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB max file size

# Create worker instances and controller
workers = {}
worker_threads = []
controller = TrafficController()
controller_thread = None
_threads_started = False


def _worker_thread_main(worker):
    while True:
        if worker.video_source and os.path.exists(worker.video_source):
            worker.process_loop()
        else:
            time.sleep(1)


def _initialize_worker_threads():
    for road in ["road1", "road2", "road3", "road4"]:
        worker = Worker(road, "")
        workers[road] = worker
        thread = Thread(target=_worker_thread_main, args=(worker,), daemon=True)
        thread.start()
        worker_threads.append(thread)


def _initialize_controller_thread():
    global controller_thread
    controller_thread = Thread(target=controller.start, daemon=True)
    controller_thread.start()


def initialize_threads():
    global _threads_started
    if _threads_started:
        return
    _threads_started = True
    _initialize_worker_threads()
    _initialize_controller_thread()


def start_background_threads():
    initialize_threads()


def initialize_mongodb():
    """Initialize MongoDB at startup without affecting current APIs."""
    try:
        db = get_database()
        db.command("ping")
        print(f"MongoDB initialization complete for database: {get_database_name()}")
    except Exception as exc:
        print(f"MongoDB initialization skipped: {exc}")


@app.route("/upload", methods=["POST"])
def upload_files():
    """
    Handle file uploads from the frontend.
    Expects up to 4 files: road1, road2, road3, road4
    """
    try:
        uploaded_files = {}

        for road in ["road1", "road2", "road3", "road4"]:
            if road in request.files:
                file = request.files[road]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    uploaded_files[road] = filepath
                    if road in workers:
                        workers[road].video_source = filepath

        if not uploaded_files:
            return jsonify({"message": "No files received"}), 400

        return jsonify({
            "message": "Files uploaded successfully",
            "files": uploaded_files,
        }), 200
    except Exception as e:
        return jsonify({"message": f"Upload failed: {str(e)}"}), 500


@app.route("/dashboard", methods=["GET"])
def dashboard():
    with controller_state_lock:
        road_summaries = {
            road_id: summary.copy()
            for road_id, summary in controller_state.get("road_summaries", {}).items()
        }
        response = {
            "current_green_road": controller_state.get("current_green_road"),
            "current_timer": controller_state.get("current_timer"),
            "road_summaries": road_summaries,
            "timestamp": controller_state.get("timestamp"),
        }
    return jsonify(response), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "Backend is running"}), 200


@app.route("/analytics/history", methods=["GET"])
def analytics_history():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        records = get_history(start_date=start_date, end_date=end_date)
        if not records:
            return jsonify({"status": "error", "message": "No analytics records found"}), 404
        return jsonify({"status": "success", "records": records}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analytics/today", methods=["GET"])
def analytics_today():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        result = get_today_summary(start_date=start_date, end_date=end_date)
        if not result:
            return jsonify({"status": "error", "message": "No analytics records found"}), 404
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analytics/weekly", methods=["GET"])
def analytics_weekly():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        result = get_weekly_summary(start_date=start_date, end_date=end_date)
        if not result:
            return jsonify({"status": "error", "message": "No analytics records found"}), 404
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/analytics/monthly", methods=["GET"])
def analytics_monthly():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        result = get_monthly_summary(start_date=start_date, end_date=end_date)
        if not result:
            return jsonify({"status": "error", "message": "No analytics records found"}), 404
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/reports/pdf", methods=["GET"])
def export_pdf_report():
    try:
        range_name = request.args.get("range", "today")
        pdf_content = build_pdf_report(range_name)
        pdf_bytes = base64.b64decode(pdf_content)
        headers = {
            "Content-Disposition": f"attachment; filename=traffic-report-{range_name}.pdf"
        }
        return Response(pdf_bytes, mimetype="application/pdf", headers=headers), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/reports/csv", methods=["GET"])
def export_csv_report():
    try:
        range_name = request.args.get("range", "today")
        csv_content = build_csv_report(range_name)
        headers = {
            "Content-Disposition": f"attachment; filename=traffic-report-{range_name}.csv"
        }
        return Response(csv_content, mimetype="text/csv", headers=headers), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    initialize_mongodb()
    start_background_threads()
    print("🚀 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host="localhost", port=5000)
