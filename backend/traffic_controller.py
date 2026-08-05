import logging
import threading
from datetime import datetime, timezone
import time
from shared_state import (
    road_results,
    controller_state,
    road_results_lock,
    controller_state_lock,
)
from traffic_logger import TrafficLogger

logger = logging.getLogger(__name__)


class TrafficController:
    def __init__(self, cycle_interval=1.0):
        self.cycle_interval = cycle_interval
        self.is_running = False
        self._lock = threading.Lock()
        self._traffic_logger = TrafficLogger()

    def _hybrid_score(self, data):
        """Hybrid Decision Engine.

        Combines current traffic and predicted traffic into a single score.
        Current traffic is weighted higher (60%) because it reflects the
        present road state and avoids overreacting to uncertain forecasts.
        Predicted traffic is weighted lower (40%) to incorporate future trends
        while keeping the controller stable and responsive.
        """
        current = data.get("vehicle_count", 0) or 0
        status = (data.get("prediction_status") or "").lower()

        if status != "success":
            # If prediction is unavailable or failed, ignore predicted traffic.
            return float(current)

        predicted = data.get("predicted_vehicle_count", 0) or 0
        return float(round(current * 0.6 + predicted * 0.4, 3))

    def _select_green_road(self, snapshot, exclude_road=None):
        candidates = []

        for road_id, data in snapshot.items():
            if exclude_road and road_id == exclude_road:
                continue
            hybrid_score = self._hybrid_score(data)
            candidates.append((hybrid_score, road_id))

        # Choose the RED road with the highest Hybrid Score when switching.
        # This prevents the currently GREEN road from immediately regaining
        # green unless it genuinely has the highest priority after it becomes RED.
        best = max(candidates, key=lambda item: (item[0], -int(item[1].replace("road", ""))))
        return best[1]

    def _compute_waiting_time(self, snapshot, current_green_road, current_timer, target_road_id):
        """Estimate waiting time by simulating future GREEN order among RED roads.

        This function builds the future order by repeatedly selecting the highest
        priority RED road (by Hybrid Score) and summing recommended green times
        until the target road is reached. This produces realistic staggered
        waiting times (e.g., 35, 95, 135 seconds) rather than identical waits.
        """
        if not current_green_road:
            return 0

        if target_road_id == current_green_road:
            return 0

        waiting_time = max(int(current_timer or 0), 0)
        # Start by considering the next switch; exclude the currently green road
        # from immediate consideration and simulate RED-only competition.
        simulated_snapshot = {rid: data.copy() for rid, data in snapshot.items()}
        seen_roads = set()

        while True:
            # pick next red road with highest hybrid score excluding already seen
            next_road = self._select_green_road(simulated_snapshot, exclude_road=current_green_road)
            if next_road in seen_roads:
                break
            seen_roads.add(next_road)

            if next_road == target_road_id:
                return waiting_time

            next_time = simulated_snapshot.get(next_road, {}).get("recommended_green_time", 0) or 0
            waiting_time += max(int(next_time), 0)

            # simulate that this road will be green next (so it won't be chosen again)
            simulated_snapshot[next_road]["_simulated_played"] = True
            # to avoid reselecting it, remove it from consideration
            simulated_snapshot.pop(next_road, None)

        return waiting_time

    def _build_road_summaries(self, snapshot, current_green_road, current_timer):
        summaries = {}
        for road_id, data in snapshot.items():
            vehicle_count = data.get("vehicle_count", 0) or 0
            last_updated = data.get("last_updated")
            has_video = vehicle_count > 0 and last_updated is not None

            prediction = data.get("prediction", "unknown")
            if not has_video:
                prediction = "No Video"

            summaries[road_id] = {
                "vehicle_count": vehicle_count,
                "predicted_vehicle_count": data.get("predicted_vehicle_count", 0),
                "prediction_status": data.get("prediction_status", "pending"),
                "density_score": data.get("density_score", 0.0),
                "density_level": "LOW" if not has_video else (data.get("density_level", "LOW") or "LOW"),
                "prediction": prediction,
                "recommended_green_time": data.get("recommended_green_time", 0),
                "signal_status": data.get("signal_status", "red"),
                "last_updated": last_updated,
                "remaining_time": current_timer if current_green_road == road_id else 0,
                "waiting_time": 0 if current_green_road == road_id else self._compute_waiting_time(snapshot, current_green_road, current_timer, road_id),
            }
        return summaries

    def _update_controller_state(self, current_green_road, current_timer, snapshot):
        # store controller timestamps as timezone-aware UTC ISO strings
        timestamp = datetime.now(timezone.utc).isoformat()

        processed_snapshot = {}
        for road_id, data in snapshot.items():
            processed_data = data.copy()
            processed_data["signal_status"] = "GREEN" if road_id == current_green_road else "RED"
            processed_snapshot[road_id] = processed_data

        road_summaries = self._build_road_summaries(processed_snapshot, current_green_road, current_timer)

        # Compute priorities and attach hybrid scores and estimated waiting times.
        # Only RED roads participate in priority calculation; the current GREEN
        # road is labeled as CURRENT.
        red_roads = [r for r in road_summaries.keys() if r != current_green_road]
        # sort red roads by hybrid score descending
        sorted_red = sorted(
            red_roads,
            key=lambda rid: (
                road_summaries[rid].get("hybrid_score", 0),
                -int(rid.replace("road", "")),
            ),
            reverse=True,
        )

        # assign priority labels
        priorities = {}
        labels = ["NEXT GREEN", "SECOND", "THIRD"]
        for i, rid in enumerate(sorted_red):
            priorities[rid] = labels[i] if i < len(labels) else f"P{i+1}"

        # current green road priority
        if current_green_road:
            priorities[current_green_road] = "CURRENT"

        # attach priority and hybrid score to summaries
        for rid, summary in road_summaries.items():
            summary["hybrid_score"] = self._hybrid_score(processed_snapshot.get(rid, {}))
            summary["priority"] = priorities.get(rid, "")
            # ensure waiting_time is recalculated using the simulated ordering
            summary["waiting_time"] = 0 if rid == current_green_road else self._compute_waiting_time(processed_snapshot, current_green_road, current_timer, rid)

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
                    # When switching, exclude the current green road from
                    # consideration so only RED roads compete for the next green.
                    exclude = self.current_green_road
                    selected_road = self._select_green_road(snapshot, exclude_road=exclude)
                    selected_time = snapshot.get(selected_road, {}).get("recommended_green_time", 0) or 0
                    self.current_green_road = selected_road
                    self.current_timer = selected_time
                    logger.info(
                        "Switching green to %s for %s seconds",
                        self.current_green_road,
                        self.current_timer,
                    )

                self._update_controller_state(self.current_green_road, self.current_timer, snapshot)
                with controller_state_lock:
                    road_summaries = controller_state.get("road_summaries", {})
                self._traffic_logger.log_snapshot(road_summaries, self.current_green_road, self.current_timer)
            except Exception as e:
                logger.error("TrafficController error: %s", e)
            finally:
                time.sleep(self.cycle_interval)

    def stop(self):
        self.is_running = False
        logger.info("TrafficController stopped")
