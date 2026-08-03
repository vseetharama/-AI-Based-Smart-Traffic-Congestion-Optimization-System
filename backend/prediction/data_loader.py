"""MongoDB data loading utilities for traffic prediction.

Purpose:
Load historical traffic data from the existing MongoDB collection and return
it as a pandas DataFrame that can be used by the preprocessing and training
pipeline.

Inputs:
collection_name : MongoDB collection name (defaults to traffic_logs)

Outputs:
Pandas DataFrame sorted by timestamp and grouped road-wise where helpful.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from pymongo import MongoClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from backend.database import get_database
except ModuleNotFoundError:
    from database import get_database


def load_traffic_history(collection_name: str = "traffic_logs") -> pd.DataFrame:
    """Load traffic history from MongoDB as a pandas DataFrame.

    Purpose:
    Retrieve the existing traffic_logs data without creating any new database or
    collection. The records are converted into a DataFrame and sorted by
    timestamp so that forecasting can be done in chronological order.

    Parameters:
    collection_name : name of the MongoDB collection to read.

    Returns:
    A pandas DataFrame containing the traffic history.
    """
    try:
        db = get_database()
        collection = db[collection_name]
        documents = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    except Exception:
        return pd.DataFrame(columns=[
            "timestamp",
            "road_id",
            "road_name",
            "vehicle_count",
            "density_level",
            "waiting_time",
            "recommended_green_time",
            "signal_status",
        ])

    if not documents:
        return pd.DataFrame(columns=[
            "timestamp",
            "road_id",
            "road_name",
            "vehicle_count",
            "density_level",
            "waiting_time",
            "recommended_green_time",
            "signal_status",
        ])

    df = pd.DataFrame(documents)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def group_by_road(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Group traffic history by road.

    Purpose:
    Prepare road-wise data so that each road can be modeled independently.

    Parameters:
    df : DataFrame containing traffic history.

    Returns:
    A dictionary mapping road IDs to road-specific DataFrames.
    """
    if df.empty:
        return {}

    grouped = {}
    for road_id, road_df in df.groupby("road_id", dropna=False):
        grouped[str(road_id)] = road_df.sort_values("timestamp").reset_index(drop=True)
    return grouped
