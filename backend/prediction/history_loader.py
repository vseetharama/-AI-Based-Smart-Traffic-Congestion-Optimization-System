"""Load recent historical traffic records for prediction inference.

Purpose:
Provide a reusable helper that fetches the latest traffic records for a
specific road from the existing MongoDB collection and returns them as a
pandas DataFrame ready for prediction preprocessing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from backend.database import get_database
except ModuleNotFoundError:
    from database import get_database


def get_recent_history(road_id: str, sequence_length: int = 12) -> pd.DataFrame:
    """Load the most recent historical traffic records for a specific road.

    Parameters:
        road_id: Identifier of the road to filter by.
        sequence_length: Maximum number of recent records to return.

    Returns:
        DataFrame sorted by timestamp in ascending order containing the latest
        records for the requested road.
    """
    if sequence_length is None or sequence_length <= 0:
        sequence_length = 12

    projection = {
        "_id": 0,
        "timestamp": 1,
        "road_id": 1,
        "road_name": 1,
        "vehicle_count": 1,
        "density_level": 1,
        "waiting_time": 1,
        "recommended_green_time": 1,
        "signal_status": 1,
    }

    try:
        db = get_database()
        collection = db["traffic_logs"]
        cursor = (
            collection.find({"road_id": road_id}, projection)
            .sort("timestamp", -1)
            .limit(sequence_length)
        )
        records = list(cursor)
    except Exception:
        records = []

    df = pd.DataFrame(records)

    expected_columns = [
        "timestamp",
        "road_id",
        "road_name",
        "vehicle_count",
        "density_level",
        "waiting_time",
        "recommended_green_time",
        "signal_status",
    ]

    for column in expected_columns:
        if column not in df.columns:
            df[column] = pd.NA

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp").reset_index(drop=True)

    return df[expected_columns]
