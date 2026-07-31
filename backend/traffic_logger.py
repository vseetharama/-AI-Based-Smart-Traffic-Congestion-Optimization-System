import logging
import queue
import threading
from datetime import datetime, timezone

from database import get_database

logger = logging.getLogger(__name__)


class TrafficLogger:
    """Background traffic logger that writes to MongoDB without blocking the live controller."""

    def __init__(self, flush_interval_seconds: int = 10):
        self.flush_interval_seconds = flush_interval_seconds
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._last_logged_state = {}
        self._worker_thread = threading.Thread(target=self._run, daemon=True)
        self._worker_thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            try:
                document = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            try:
                self._persist_document(document)
            except Exception as exc:
                logger.exception("Traffic logging failed: %s", exc)
            finally:
                self._queue.task_done()

    def _persist_document(self, document):
        try:
            db = get_database()
            collection = db["traffic_logs"]
            collection.insert_one(document)
        except Exception as exc:
            logger.exception("MongoDB traffic insert failed: %s", exc)

    def log_snapshot(self, road_summaries, current_green_road=None, current_timer=0):
        if not road_summaries:
            return

        now = datetime.now(timezone.utc)

        for road_id, summary in road_summaries.items():
            road_name = summary.get("road_name") or f"Road {str(road_id).replace('road', '')}"
            tracked_state = {
                "vehicle_count": int(summary.get("vehicle_count", 0) or 0),
                "density_level": (summary.get("density_level") or "LOW").upper(),
                "signal_status": (summary.get("signal_status") or "RED").upper(),
                "recommended_green_time": int(summary.get("recommended_green_time", 0) or 0),
            }

            with self._lock:
                previous_state = self._last_logged_state.get(road_id)
                should_log = False

                if previous_state is None:
                    should_log = True
                else:
                    changed = (
                        previous_state.get("vehicle_count") != tracked_state["vehicle_count"]
                        or previous_state.get("density_level") != tracked_state["density_level"]
                        or previous_state.get("signal_status") != tracked_state["signal_status"]
                        or previous_state.get("recommended_green_time") != tracked_state["recommended_green_time"]
                    )
                    if changed:
                        should_log = True
                    else:
                        last_logged_at = previous_state.get("last_logged_at")
                        if last_logged_at is None:
                            should_log = True
                        else:
                            should_log = (now - last_logged_at).total_seconds() >= self.flush_interval_seconds

                if should_log:
                    document = {
                        "timestamp": now,
                        "road_id": str(road_id),
                        "road_name": road_name,
                        "vehicle_count": tracked_state["vehicle_count"],
                        "density_level": tracked_state["density_level"],
                        "signal_status": tracked_state["signal_status"],
                        "remaining_time": int(summary.get("remaining_time", 0) or 0),
                        "waiting_time": int(summary.get("waiting_time", 0) or 0),
                        "recommended_green_time": tracked_state["recommended_green_time"],
                        "prediction": summary.get("prediction", "unknown"),
                        "current_green_road": current_green_road,
                        "current_timer": int(current_timer or 0),
                    }
                    self._queue.put(document)
                    self._last_logged_state[road_id] = {
                        **tracked_state,
                        "last_logged_at": now,
                    }

    def shutdown(self):
        self._stop_event.set()
        self._queue.put_nowait(None)
