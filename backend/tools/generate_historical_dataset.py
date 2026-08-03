"""Generate a realistic historical traffic dataset for Version 2.

Purpose:
Create a CSV file that can be imported into the existing MongoDB traffic_logs
collection without changing the live YOLO or analytics workflow.

This utility is intentionally isolated so Version 1.5.1 behavior stays intact
while MongoDB gains richer historical coverage for analytics and LSTM training.
"""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_ROADS = ["road1", "road2", "road3", "road4"]
DEFAULT_ROAD_NAMES = {
    "road1": "Road 1",
    "road2": "Road 2",
    "road3": "Road 3",
    "road4": "Road 4",
}

SCHEMA_COLUMNS = [
    "timestamp",
    "road_id",
    "road_name",
    "vehicle_count",
    "density_level",
    "signal_status",
    "remaining_time",
    "waiting_time",
    "recommended_green_time",
    "prediction",
    "current_green_road",
    "current_timer",
]


def _density_from_vehicle_count(vehicle_count: int) -> str:
    if vehicle_count >= 40:
        return "HIGH"
    if vehicle_count >= 20:
        return "MEDIUM"
    return "LOW"


def _signal_status_for_time(hour: int, weekend: bool) -> str:
    if weekend:
        if 7 <= hour < 10 or 17 <= hour < 21:
            return "GREEN"
        if 12 <= hour < 14:
            return "YELLOW"
        return "RED"

    if 7 <= hour < 10 or 17 <= hour < 21:
        return "GREEN"
    if 12 <= hour < 14:
        return "YELLOW"
    return "RED"


def _base_vehicle_count(hour: int, weekend: bool) -> int:
    if weekend:
        if 7 <= hour < 10:
            return 14
        if 12 <= hour < 14:
            return 18
        if 17 <= hour < 21:
            return 22
        return 8

    if 7 <= hour < 10:
        return 28
    if 12 <= hour < 14:
        return 20
    if 17 <= hour < 21:
        return 34
    return 9


def _prediction_for_vehicle_count(vehicle_count: int) -> str:
    if vehicle_count >= 35:
        return "Heavy traffic expected"
    if vehicle_count >= 20:
        return "Moderate traffic expected"
    return "Light traffic expected"


def _select_green_road(bucket_rows: list[dict[str, Any]], controller_state: dict[str, dict[str, int]], time_index: int) -> str:
    """Choose the most suitable road for green using traffic pressure and fairness."""
    scores: dict[str, float] = {}
    for row in bucket_rows:
        road_id = row["road_id"]
        state = controller_state[road_id]
        demand_score = (
            row["vehicle_count"] * 1.5
            + row["waiting_time"] * 1.2
            + row["recommended_green_time"] * 0.1
        )
        backlog_penalty = state["wait"] * 3.0
        fairness_boost = max(0, 6 - (time_index - state["last_green_index"]))
        scores[road_id] = demand_score + backlog_penalty + fairness_boost

    return max(scores, key=scores.get)


def _compute_green_duration(row: dict[str, Any]) -> int:
    """Compute a realistic green duration for the active road."""
    base_duration = int(row["recommended_green_time"] * 0.7)
    traffic_bonus = min(12, int(row["vehicle_count"] * 0.2))
    return max(10, min(45, base_duration + traffic_bonus))


def generate_historical_dataset(days: int = 90, interval_minutes: int = 5, roads: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """Generate realistic historical traffic records.

    Purpose:
    Create a CSV-friendly list of traffic records that mimic actual daily traffic
    peaks without using purely random values.

    Inputs:
    days : number of historical days to generate
    interval_minutes : time spacing between records
    roads : iterable of road IDs to generate data for

    Outputs:
    List of dictionaries matching the traffic_logs schema.
    """
    roads = list(roads or DEFAULT_ROADS)
    rows: list[dict[str, Any]] = []
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    random.seed(42)
    controller_state = {
        road_id: {"wait": 0, "last_green_index": -999}
        for road_id in roads
    }
    time_index = 0

    for day_offset in range(days):
        current_day = start + timedelta(days=day_offset)
        weekend = current_day.weekday() >= 5
        for minute_offset in range(0, 24 * 60, interval_minutes):
            timestamp = current_day + timedelta(minutes=minute_offset)
            hour = timestamp.hour
            bucket_rows: list[dict[str, Any]] = []
            for road_id in roads:
                base_count = _base_vehicle_count(hour, weekend)
                variation = random.randint(-3, 3)
                vehicle_count = max(0, base_count + variation)
                if hour in {7, 8, 9, 17, 18, 19, 20}:
                    vehicle_count += 4
                if hour in {12, 13}:
                    vehicle_count += 2
                density_level = _density_from_vehicle_count(vehicle_count)
                remaining_time = max(0, 25 - vehicle_count // 4)
                waiting_time = max(0, vehicle_count // 3)
                recommended_green_time = max(10, min(60, 20 + vehicle_count // 2))
                prediction = _prediction_for_vehicle_count(vehicle_count)
                bucket_rows.append({
                    "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                    "road_id": road_id,
                    "road_name": DEFAULT_ROAD_NAMES.get(road_id, road_id),
                    "vehicle_count": vehicle_count,
                    "density_level": density_level,
                    "signal_status": "RED",
                    "remaining_time": remaining_time,
                    "waiting_time": waiting_time,
                    "recommended_green_time": recommended_green_time,
                    "prediction": prediction,
                    "current_green_road": None,
                    "current_timer": 0,
                })

            active_road = _select_green_road(bucket_rows, controller_state, time_index)
            active_row = next(row for row in bucket_rows if row["road_id"] == active_road)
            current_timer = _compute_green_duration(active_row)

            for row in bucket_rows:
                if row["road_id"] == active_road:
                    row["signal_status"] = "GREEN"
                    row["remaining_time"] = current_timer
                    row["current_green_road"] = active_road
                    row["current_timer"] = current_timer
                else:
                    row["signal_status"] = "RED"
                    row["remaining_time"] = 0
                    row["current_green_road"] = active_road
                    row["current_timer"] = 0

            for road_id in roads:
                if road_id == active_road:
                    controller_state[road_id]["wait"] = 0
                    controller_state[road_id]["last_green_index"] = time_index
                else:
                    controller_state[road_id]["wait"] += 1

            rows.extend(bucket_rows)
            time_index += 1

    return rows


def write_dataset_csv(rows: Iterable[dict[str, Any]], output_path: str | Path) -> Path:
    """Write rows to a CSV file using the existing schema columns."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCHEMA_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def main() -> None:
    rows = generate_historical_dataset()
    output_path = Path(__file__).resolve().parent.parent / "uploads" / "historical_traffic_dataset.csv"
    write_dataset_csv(rows, output_path)
    print(f"Generated {len(rows)} rows")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
