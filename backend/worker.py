import cv2
import logging
import os
import time
from datetime import datetime
from yolotest import detect_vehicles, load_yolo_model
from shared_state import road_results, road_results_lock, yolo_inference_lock

logger = logging.getLogger(__name__)

GREEN_TIME = {
    "LOW": 40,
    "MEDIUM": 60,
    "HIGH": 120,
}


class Worker:
    def __init__(self, road_id, video_source, frame_skip=5):
        self.road_id = road_id
        self.video_source = video_source
        self.frame_skip = max(1, frame_skip)
        self.model = load_yolo_model()
        self.capture = None
        self.frame_index = 0
        self.is_running = False
        self._current_source = video_source

    def _open_video(self):
        if self.capture is not None:
            self.capture.release()
        self.capture = cv2.VideoCapture(self.video_source)
        if not self.capture.isOpened():
            raise IOError(f"Cannot open video source: {self.video_source}")

    def _close_video(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def _refresh_video_if_needed(self):
        if self.video_source != self._current_source:
            logger.info("Video source changed for %s: reopening %s", self.road_id, self.video_source)
            self._close_video()
            self._current_source = self.video_source
            self.frame_index = 0

    def _calculate_density(self, vehicle_count):
        return round(min(vehicle_count / 30.0, 1.0), 3)

    def _density_level(self, density_score):
        if density_score >= 0.67:
            return "HIGH"
        if density_score >= 0.33:
            return "MEDIUM"
        return "LOW"

    def _generate_prediction(self, vehicle_count, density_score):
        if vehicle_count >= 20:
            return "high"
        if vehicle_count >= 10:
            return "medium"
        return "low"

    def _recommend_green_time(self, density_level):
        level = (density_level or "LOW").upper()
        return GREEN_TIME.get(level, GREEN_TIME["LOW"])

    def _update_road_results(self, vehicle_count, density, prediction, recommended_green_time):
        timestamp = datetime.now().isoformat()
        density_level = self._density_level(density)
        with road_results_lock:
            road_results[self.road_id].update({
                "vehicle_count": vehicle_count,
                "density_score": density,
                "density_level": density_level,
                "prediction": prediction,
                "recommended_green_time": recommended_green_time,
                "signal_status": road_results[self.road_id].get("signal_status", "red"),
                "last_updated": timestamp,
            })

    def process_loop(self):
        self.is_running = True
        try:
            if not os.path.exists(self.video_source):
                raise FileNotFoundError(f"Video file does not exist: {self.video_source}")

            self._open_video()

            while self.is_running:
                self._refresh_video_if_needed()
                if self.capture is None:
                    self._open_video()

                ret, frame = self.capture.read()
                if not ret:
                    self._open_video()
                    continue

                self.frame_index += 1
                if self.frame_index % self.frame_skip != 0:
                    continue

                try:
                    with yolo_inference_lock:
                        vehicle_count, _, _ = detect_vehicles(frame, model=self.model)
                except Exception as e:
                    logger.error("YOLO inference error for %s: %s", self.road_id, e)
                    continue

                density = self._calculate_density(vehicle_count)
                density_level = self._density_level(density)
                prediction = self._generate_prediction(vehicle_count, density)
                recommended_green_time = self._recommend_green_time(density_level)

                self._update_road_results(vehicle_count, density, prediction, recommended_green_time)

        except FileNotFoundError as e:
            logger.error("Worker file error for %s: %s", self.road_id, e)
        except IOError as e:
            logger.error("Worker IO error for %s: %s", self.road_id, e)
        except Exception as e:
            logger.error("Unexpected worker error for %s: %s", self.road_id, e)
        finally:
            self._close_video()
            self.is_running = False

    def stop(self):
        self.is_running = False
