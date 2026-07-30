import logging
import threading
from datetime import datetime
import time
from shared_state import (
    road_results,
    controller_state,
    road_results_lock,
    controller_state_lock,
)

logger = logging.getLogger(__name__)


class TrafficController:
    def __init__(self, cycle_interval=1.0):
        self.cycle_interval = cycle_interval
        self.is_running = False
        self._lock = threading.Lock()

    def _select_green_road(self, snapshot):
        candidates = []

        for road_id, data in snapshot.items():
            recommended_time = data.get("recommended_green_time", 0) or 0
            vehicle_count = data.get("vehicle_count", 0) or 0
            candidates.append((recommended_time, vehicle_count, road_id))

        best = max(candidates, key=lambda item: (item[0], item[1], -int(item[2].replace("road", ""))))
        return best[2]

    def _build_road_summaries(self, snapshot):
        summaries = {}
        for road_id, data in snapshot.items():
            summaries[road_id] = {
                "vehicle_count": data.get("vehicle_count", 0),
                "density_score": data.get("density_score", 0.0),
                "density_level": data.get("density_level", "LOW"),
                "prediction": data.get("prediction", "unknown"),
                "recommended_green_time": data.get("recommended_green_time", 0),
                "signal_status": data.get("signal_status", "red"),
                "last_updated": data.get("last_updated"),
            }
        return summaries

    def _update_controller_state(self, current_green_road, current_timer, snapshot):
        timestamp = datetime.now().isoformat()

        processed_snapshot = {}
        for road_id, data in snapshot.items():
            processed_data = data.copy()
            processed_data["signal_status"] = "GREEN" if road_id == current_green_road else "RED"
            processed_snapshot[road_id] = processed_data

        road_summaries = self._build_road_summaries(processed_snapshot)
        with controller_state_lock:
            controller_state.update({
                "current_green_road": current_green_road,
                "current_timer": current_timer,
                "road_summaries": road_summaries,
                "timestamp": timestamp,
            })

    def start(self):
        self.is_running = True
        self.current_green_road = None
        self.current_timer = 0
        logger.info("TrafficController started")

        while self.is_running:
            try:
                with road_results_lock:
                    snapshot = {road_id: data.copy() for road_id, data in road_results.items()}

                if self.current_timer > 0 and self.current_green_road is not None:
                    self.current_timer -= 1
                    logger.info(
                        "Keeping %s green for %s more seconds",
                        self.current_green_road,
                        self.current_timer,
                    )
                else:
                    selected_road = self._select_green_road(snapshot)
                    selected_time = snapshot.get(selected_road, {}).get("recommended_green_time", 0) or 0
                    self.current_green_road = selected_road
                    self.current_timer = selected_time
                    logger.info(
                        "Switching green to %s for %s seconds",
                        self.current_green_road,
                        self.current_timer,
                    )

                self._update_controller_state(self.current_green_road, self.current_timer, snapshot)
            except Exception as e:
                logger.error("TrafficController error: %s", e)
            finally:
                time.sleep(self.cycle_interval)

    def stop(self):
        self.is_running = False
        logger.info("TrafficController stopped")
