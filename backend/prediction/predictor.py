"""Prediction service for the trained LSTM traffic model.

Purpose:
Load the saved model once and use it to predict the next vehicle count from a
recent traffic history window.

The service is designed so that it can be extended later for density,
waiting time, and congestion prediction without changing the interface.
"""

from __future__ import annotations

import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

try:
    from tensorflow.keras.models import load_model
except Exception:  # pragma: no cover - fallback for environments without TensorFlow
    load_model = None

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from prediction.preprocessing import _prepare_feature_frame


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "traffic_predictor.keras"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

_MODEL = None
_SCALER = None


def _load_model_and_scaler() -> tuple[Any, Any]:
    """Load the trained model and scaler once for reuse.

    Purpose:
    Avoid reloading the model on every prediction request, which keeps the
    service efficient in the backend.

    Returns:
    Loaded model and scaler.
    """
    global _MODEL, _SCALER
    if _MODEL is not None and _SCALER is not None:
        return _MODEL, _SCALER

    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("Trained model or scaler not found. Run training first.")

    if load_model is None:
        raise ImportError("TensorFlow is required to load the prediction model.")

    _MODEL = load_model(MODEL_PATH)
    with open(SCALER_PATH, "rb") as handle:
        _SCALER = pickle.load(handle)
    return _MODEL, _SCALER


def predict_next_vehicle_count(history_df: pd.DataFrame, road_id: Optional[Any] = None) -> dict[str, Any]:
    """Predict the next vehicle count for a given road.

    Purpose:
    Accept the latest traffic history for one road, transform it into the
    expected sequence format, and return a structured prediction payload.

    Parameters:
    history_df : DataFrame containing recent traffic records for a single road.
    road_id : optional road identifier for the returned payload.

    Returns:
    Dictionary containing the predicted vehicle count and metadata.
    """
    if history_df is None or history_df.empty:
        return {
            "road_id": road_id,
            "predicted_vehicle_count": None,
            "prediction_time": datetime.now(timezone.utc).isoformat(),
            "model_version": "v2.0",
            "status": "error",
            "message": "No history supplied for prediction.",
        }

    try:
        model, scaler = _load_model_and_scaler()
        feature_frame = _prepare_feature_frame(history_df)
        if feature_frame.shape[0] < 2:
            raise ValueError("Not enough historical points for prediction.")

        scaled_features = scaler.transform(feature_frame)
        last_sequence = scaled_features[-12:]
        if last_sequence.shape[0] < 12:
            last_sequence = np.pad(last_sequence, ((12 - last_sequence.shape[0], 0), (0, 0)), mode="edge")

        prediction = model.predict(last_sequence[np.newaxis, ...], verbose=0)[0][0]
        inverse_prediction = float(scaler.inverse_transform(np.array([[prediction, 0, 0, 0, 0, 0, 0]]))[0][0])

        return {
            "road_id": road_id,
            "predicted_vehicle_count": round(inverse_prediction, 2),
            "prediction_time": datetime.now(timezone.utc).isoformat(),
            "model_version": "v2.0",
            "status": "success",
        }
    except Exception as exc:
        return {
            "road_id": road_id,
            "predicted_vehicle_count": None,
            "prediction_time": datetime.now(timezone.utc).isoformat(),
            "model_version": "v2.0",
            "status": "error",
            "message": str(exc),
        }
