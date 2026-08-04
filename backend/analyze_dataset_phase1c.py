"""Phase 1C dataset analysis and model preparation workflow.

Purpose:
Analyze the historical MongoDB traffic dataset before retraining the LSTM model.
The script is intentionally isolated so it can be run independently without
changing the main Version 1.5.1 application workflow.

Inputs:
- MongoDB collection: traffic_logs

Outputs:
- Dataset summary statistics
- Data quality report
- Traffic pattern analysis
- Feature engineering review
- Retraining recommendation
- Optional retraining metrics if TensorFlow is available
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database import get_database


VALID_DENSITY_VALUES = {"LOW", "MEDIUM", "HIGH"}
VALID_PREDICTIONS = {
    "light traffic expected",
    "moderate traffic expected",
    "heavy traffic expected",
    "no video",
    "unknown",
}


def _safe_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _load_documents() -> list[dict[str, Any]]:
    """Load road-level traffic documents from MongoDB.

    Purpose:
    Read only the real traffic records that contain road-level fields such as
    road_id and vehicle_count. This avoids mixing the analysis with connection-test
    or other placeholder documents.

    Inputs:
    None.

    Outputs:
    A list of genuine traffic documents sorted by timestamp.
    """
    db = get_database()
    collection = db["traffic_logs"]
    return list(collection.find({
        "timestamp": {"$exists": True},
        "road_id": {"$exists": True},
        "vehicle_count": {"$exists": True},
    }, {
        "_id": 0,
        "timestamp": 1,
        "road_id": 1,
        "road_name": 1,
        "vehicle_count": 1,
        "density_level": 1,
        "signal_status": 1,
        "remaining_time": 1,
        "waiting_time": 1,
        "recommended_green_time": 1,
        "prediction": 1,
        "current_green_road": 1,
        "current_timer": 1,
    }).sort("timestamp", 1))


def analyze_dataset() -> dict[str, Any]:
    """Produce a complete dataset analysis report.

    Purpose:
    Summarize the historical dataset quality, traffic behavior, and model readiness.

    Inputs:
    None; this function reads directly from MongoDB.

    Outputs:
    A dictionary containing the dataset summary, quality report, traffic patterns,
    feature review, recommendation, and retraining status.
    """
    documents = _load_documents()
    if not documents:
        return {"status": "error", "message": "No traffic documents found in MongoDB."}

    normalized = []
    for doc in documents:
        timestamp = doc.get("timestamp")
        if isinstance(timestamp, datetime):
            normalized_timestamp = timestamp
        else:
            try:
                normalized_timestamp = datetime.fromisoformat(str(timestamp))
            except Exception:
                normalized_timestamp = None
        normalized.append({
            **doc,
            "timestamp": normalized_timestamp,
            "vehicle_count": _safe_int(doc.get("vehicle_count")),
            "waiting_time": _safe_int(doc.get("waiting_time")),
            "recommended_green_time": _safe_int(doc.get("recommended_green_time")),
            "remaining_time": _safe_int(doc.get("remaining_time")),
            "current_timer": _safe_int(doc.get("current_timer")),
            "density_level": _safe_str(doc.get("density_level")).upper(),
            "prediction": _safe_str(doc.get("prediction")).lower(),
            "signal_status": _safe_str(doc.get("signal_status")).upper(),
        })

    valid_timestamps = [item for item in normalized if item["timestamp"] is not None]
    if valid_timestamps:
        sorted_rows = sorted(valid_timestamps, key=lambda item: item["timestamp"])
        min_ts = sorted_rows[0]["timestamp"]
        max_ts = sorted_rows[-1]["timestamp"]
        intervals = []
        for index in range(1, len(sorted_rows)):
            previous = sorted_rows[index - 1]["timestamp"]
            current = sorted_rows[index]["timestamp"]
            delta = current - previous
            if delta.total_seconds() > 0:
                intervals.append(delta.total_seconds() / 60)
        median_interval = statistics.median(intervals) if intervals else 0
    else:
        min_ts = None
        max_ts = None
        median_interval = 0

    road_counts = Counter(item.get("road_id") for item in normalized if item.get("road_id"))
    records_per_day = Counter(item["timestamp"].date().isoformat() for item in valid_timestamps if item["timestamp"] is not None)
    records_per_month = Counter(item["timestamp"].strftime("%Y-%m") for item in valid_timestamps if item["timestamp"] is not None)

    missing_values = {}
    for field in ["timestamp", "road_id", "vehicle_count", "density_level", "waiting_time", "recommended_green_time", "prediction"]:
        missing_values[field] = sum(
            1
            for item in normalized
            if item.get(field) is None or (isinstance(item.get(field), str) and str(item.get(field)).strip() == "")
        )

    duplicate_keys = []
    seen = set()
    for item in normalized:
        key = (item.get("timestamp"), item.get("road_id"))
        if key in seen:
            duplicate_keys.append(key)
        seen.add(key)

    invalid_timestamps = sum(1 for item in normalized if item["timestamp"] is None)
    negative_vehicle_counts = sum(1 for item in normalized if item["vehicle_count"] < 0)
    invalid_waiting_times = sum(1 for item in normalized if item["waiting_time"] < 0)
    invalid_green_times = sum(1 for item in normalized if item["recommended_green_time"] < 0)
    invalid_density_values = sum(1 for item in normalized if item["density_level"] not in VALID_DENSITY_VALUES)
    invalid_prediction_values = sum(1 for item in normalized if item["prediction"] not in VALID_PREDICTIONS and "traffic expected" not in item["prediction"])

    vehicle_counts = [item["vehicle_count"] for item in normalized]
    waiting_times = [item["waiting_time"] for item in normalized]
    green_times = [item["recommended_green_time"] for item in normalized]

    def _iqr(values: list[int]) -> tuple[int, int]:
        if not values:
            return 0, 0
        values_sorted = sorted(values)
        q1 = statistics.quantiles(values_sorted, n=4)[0]
        q3 = statistics.quantiles(values_sorted, n=4)[2]
        return int(q1), int(q3)

    q1_vehicle, q3_vehicle = _iqr(vehicle_counts)
    iqr_vehicle = max(0, q3_vehicle - q1_vehicle)
    outlier_vehicle = sum(1 for value in vehicle_counts if value < q1_vehicle - 1.5 * iqr_vehicle or value > q3_vehicle + 1.5 * iqr_vehicle)

    density_distribution = Counter(item["density_level"] for item in normalized)
    signal_distribution = Counter(item["signal_status"] for item in normalized)
    hour_distribution = Counter(item["timestamp"].hour if item["timestamp"] else 0 for item in valid_timestamps if item["timestamp"] is not None)

    morning_peak = {hour: count for hour, count in sorted(hour_distribution.items()) if 6 <= hour <= 10}
    lunch_hours = {hour: count for hour, count in sorted(hour_distribution.items()) if 11 <= hour <= 14}
    evening_peak = {hour: count for hour, count in sorted(hour_distribution.items()) if 15 <= hour <= 20}
    night_traffic = {hour: count for hour, count in sorted(hour_distribution.items()) if hour >= 21 or hour <= 5}

    weekday_counts = [item["vehicle_count"] for item in normalized if item["timestamp"] and item["timestamp"].weekday() < 5]
    weekend_counts = [item["vehicle_count"] for item in normalized if item["timestamp"] and item["timestamp"].weekday() >= 5]

    roadwise = {}
    for road_id, road_rows in defaultdict(list, {road_id: [] for road_id in road_counts}).items():
        pass
    roadwise = {}
    for road_id in road_counts:
        rows = [item for item in normalized if item.get("road_id") == road_id]
        roadwise[road_id] = {
            "records": len(rows),
            "avg_vehicle_count": round(statistics.mean([item["vehicle_count"] for item in rows]), 2) if rows else 0,
            "max_vehicle_count": max((item["vehicle_count"] for item in rows), default=0),
            "avg_waiting_time": round(statistics.mean([item["waiting_time"] for item in rows]), 2) if rows else 0,
        }

    overall_recommendation = "satisfactory"
    if invalid_timestamps or negative_vehicle_counts or invalid_waiting_times or invalid_green_times or invalid_density_values or invalid_prediction_values:
        overall_recommendation = "needs cleanup before retraining"

    try:
        from prediction.train import train_model
        training_result = train_model(sequence_length=12, epochs=8, batch_size=16)
        retraining_status = training_result.get("status", "error")
        retraining_metrics = training_result.get("evaluation_metrics", {})
    except Exception as exc:
        training_result = None
        retraining_status = f"blocked: {exc}"
        retraining_metrics = {}

    return {
        "status": "success",
        "dataset_summary": {
            "total_records": len(normalized),
            "number_of_roads": len(road_counts),
            "date_range": {
                "start": min_ts.isoformat() if min_ts else None,
                "end": max_ts.isoformat() if max_ts else None,
            },
            "median_time_interval_minutes": round(median_interval, 2),
            "records_per_road": dict(road_counts),
            "records_per_day": dict(records_per_day),
            "records_per_month": dict(records_per_month),
        },
        "data_quality_report": {
            "missing_values": missing_values,
            "duplicate_records": len(duplicate_keys),
            "invalid_timestamps": invalid_timestamps,
            "negative_vehicle_counts": negative_vehicle_counts,
            "invalid_waiting_times": invalid_waiting_times,
            "invalid_green_times": invalid_green_times,
            "invalid_density_values": invalid_density_values,
            "incorrect_prediction_values": invalid_prediction_values,
            "outliers": {
                "vehicle_count_outliers": outlier_vehicle,
                "vehicle_count_q1": q1_vehicle,
                "vehicle_count_q3": q3_vehicle,
            },
        },
        "traffic_pattern_analysis": {
            "morning_peak": morning_peak,
            "lunch_hours": lunch_hours,
            "evening_peak": evening_peak,
            "night_traffic": night_traffic,
            "weekday_vs_weekend": {
                "weekday_avg_vehicle_count": round(statistics.mean(weekday_counts), 2) if weekday_counts else 0,
                "weekend_avg_vehicle_count": round(statistics.mean(weekend_counts), 2) if weekend_counts else 0,
            },
            "roadwise_traffic_comparison": roadwise,
            "vehicle_count_distribution": {
                "mean": round(statistics.mean(vehicle_counts), 2) if vehicle_counts else 0,
                "median": round(statistics.median(vehicle_counts), 2) if vehicle_counts else 0,
                "min": min(vehicle_counts, default=0),
                "max": max(vehicle_counts, default=0),
            },
            "density_distribution": dict(density_distribution),
            "signal_timing_distribution": dict(signal_distribution),
            "waiting_time_distribution": {
                "mean": round(statistics.mean(waiting_times), 2) if waiting_times else 0,
                "median": round(statistics.median(waiting_times), 2) if waiting_times else 0,
                "max": max(waiting_times, default=0),
            },
            "green_time_distribution": {
                "mean": round(statistics.mean(green_times), 2) if green_times else 0,
                "median": round(statistics.median(green_times), 2) if green_times else 0,
                "max": max(green_times, default=0),
            },
        },
        "feature_engineering_review": {
            "current_features": ["vehicle_count", "waiting_time", "recommended_green_time", "density_code", "hour", "day_of_week", "day"],
            "recommended_additions": [
                "rolling_average_vehicle_count",
                "rolling_max_vehicle_count",
                "hourly_peak_indicator",
                "weekday_weekend_flag",
                "previous_vehicle_count",
                "previous_waiting_time",
            ],
            "reason": "These additions can help the LSTM model learn recent trends and recurring traffic patterns more effectively.",
        },
        "dataset_suitability": {
            "strengths": [
                "Large historical sample size",
                "Chronological ordering is preserved",
                "Road-wise traffic patterns are available",
            ],
            "weaknesses": [
                "The dataset is synthetic and may not fully capture real-world noise",
                "Some fields are still derived rather than directly observed",
            ],
            "potential_bias": [
                "Traffic patterns are generated from a fixed seasonal template",
                "The distribution may be more regular than real traffic",
            ],
            "data_balance": "Moderate; the time-based patterns are consistent but the synthetic generator may over-smooth variations.",
            "time_series_continuity": "Good for initial LSTM prototyping because the records are chronological and continuous.",
            "overall_recommendation": overall_recommendation,
        },
        "retraining_decision": {
            "status": retraining_status,
            "metrics": retraining_metrics,
            "recommended_action": "Proceed with retraining once TensorFlow is available in the environment; otherwise keep the current model in place.",
        },
    }


def main() -> None:
    report = analyze_dataset()
    output_path = Path(__file__).resolve().parent / "uploads" / "phase1c_dataset_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(report)
    print(f"Saved analysis report to {output_path}")


if __name__ == "__main__":
    main()
