"""Import a generated historical traffic dataset into MongoDB.

Purpose:
Read the CSV produced by generate_historical_dataset.py, validate it, convert the
timestamps to real DateTime values, and import the rows into the existing
traffic_logs collection without changing the current application workflow.
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pymongo import ReplaceOne

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database import get_database


REQUIRED_COLUMNS = [
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


def _parse_timestamp(value: str) -> datetime:
    value = str(value).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def load_csv_rows(csv_path: str | Path) -> list[dict[str, Any]]:
    """Load rows from the CSV and validate the schema."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {missing_columns}")

        rows: list[dict[str, Any]] = []
        for row in reader:
            normalized = {
                "timestamp": _parse_timestamp(row["timestamp"]),
                "road_id": str(row["road_id"]),
                "road_name": str(row["road_name"]),
                "vehicle_count": int(float(row["vehicle_count"])),
                "density_level": str(row["density_level"]).upper(),
                "signal_status": str(row["signal_status"]).upper(),
                "remaining_time": int(float(row["remaining_time"])),
                "waiting_time": int(float(row["waiting_time"])),
                "recommended_green_time": int(float(row["recommended_green_time"])),
                "prediction": str(row["prediction"]),
                "current_green_road": str(row.get("current_green_road") or "") or None,
                "current_timer": int(float(row.get("current_timer") or 0)),
            }
            rows.append(normalized)
        return rows


def import_historical_dataset(csv_path: str | Path, collection_name: str = "traffic_logs") -> dict[str, Any]:
    """Import historical records into MongoDB while skipping duplicates.

    Purpose:
    Load the generated traffic rows into the existing traffic_logs collection in a
    way that is reliable for large CSVs without changing the live schema.

    Inputs:
    csv_path : path to the generated historical traffic CSV.
    collection_name : MongoDB collection that should receive the rows.

    Outputs:
    A summary showing how many rows were inserted or skipped.
    """
    rows = load_csv_rows(csv_path)
    db = get_database()
    collection = db[collection_name]

    try:
        collection.create_index([("timestamp", 1), ("road_id", 1)], name="timestamp_road_id_idx")
    except Exception:
        pass

    inserted = 0
    skipped = 0
    batch_size = 1000
    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]
        operations = [
            ReplaceOne(
                {"timestamp": row["timestamp"], "road_id": row["road_id"]},
                row,
                upsert=True,
            )
            for row in batch
        ]
        result = collection.bulk_write(operations, ordered=False)
        inserted += int(result.upserted_count or 0)
        skipped += int(result.matched_count or 0)

    return {
        "inserted": inserted,
        "skipped": skipped,
        "collection": collection_name,
    }


def main() -> None:
    csv_path = Path(__file__).resolve().parent.parent / "uploads" / "historical_traffic_dataset.csv"
    result = import_historical_dataset(csv_path)
    print(result)


if __name__ == "__main__":
    main()
