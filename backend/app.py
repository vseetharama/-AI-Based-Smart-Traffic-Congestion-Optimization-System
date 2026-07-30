from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from threading import Thread
from werkzeug.utils import secure_filename
from shared_state import controller_state, controller_state_lock
from worker import Worker
from traffic_controller import TrafficController

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


if __name__ == "__main__":
    start_background_threads()
    print("🚀 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host="localhost", port=5000)
