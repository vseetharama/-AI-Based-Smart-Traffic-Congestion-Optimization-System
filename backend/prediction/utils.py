"""Utility helpers for the traffic prediction package.

Purpose:
Provide simple reusable helpers for validation, formatting, and logging so the
prediction pipeline remains easy to understand and extend.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def validate_history_frame(df: Optional[pd.DataFrame]) -> bool:
    """Check whether a DataFrame is suitable for prediction.

    Purpose:
    Prevent invalid or empty input from reaching the model.

    Parameters:
    df : candidate DataFrame.

    Returns:
    True if the frame can be used, otherwise False.
    """
    if df is None or df.empty:
        return False

    required_columns = {"timestamp", "vehicle_count"}
    return required_columns.issubset(set(df.columns))


def format_prediction_output(prediction: dict) -> dict:
    """Normalize the prediction payload into a simple dictionary.

    Purpose:
    Keep API responses consistent even when the model fails.

    Parameters:
    prediction : raw prediction dictionary.

    Returns:
    Clean dictionary with a predictable structure.
    """
    return {
        "road_id": prediction.get("road_id"),
        "predicted_vehicle_count": prediction.get("predicted_vehicle_count"),
        "prediction_time": prediction.get("prediction_time"),
        "model_version": prediction.get("model_version", "v2.0"),
        "status": prediction.get("status", "error"),
        "message": prediction.get("message"),
    }
