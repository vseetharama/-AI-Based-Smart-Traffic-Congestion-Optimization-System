"""Training entry-point for the Phase 1 LSTM prediction model.

Purpose:
Load traffic data, preprocess it, train the model, and save the trained model
for later prediction.

The script is intentionally isolated from the existing application so the
Version 1.5 workflow remains intact.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from prediction.data_loader import load_traffic_history
from prediction.dataset import train_test_split_sequences
from prediction.evaluation import calculate_regression_metrics
from prediction.lstm_model import build_lstm_model
from prediction.preprocessing import prepare_training_data


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "traffic_predictor.keras"
SCALER_PATH = MODEL_DIR / "scaler.pkl"


def train_model(sequence_length: int = 12, epochs: int = 10, batch_size: int = 16) -> dict:
    """Train the LSTM traffic prediction model.

    Purpose:
    Run the full training pipeline and save the model and scaler.

    Parameters:
    sequence_length : number of historical steps used for each input window.
    epochs : number of training iterations.
    batch_size : size of each training batch.

    Returns:
    Dictionary with training metrics and file paths.
    """
    df = load_traffic_history()
    if df.empty or "timestamp" not in df.columns:
        return {
            "status": "error",
            "message": "No usable traffic history found in MongoDB.",
        }

    try:
        X, y, scaler = prepare_training_data(df, sequence_length=sequence_length)
        X_train, X_val, y_train, y_val = train_test_split_sequences(X, y, validation_split=0.2)

        # The train/validation split helps us verify whether the model is learning
        # general patterns rather than memorizing the training data.
        model = build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )

        model.save(MODEL_PATH)
        with open(SCALER_PATH, "wb") as handle:
            pickle.dump(scaler, handle)

        predictions = model.predict(X_val, verbose=0).reshape(-1)
        evaluation_metrics = calculate_regression_metrics(y_val.reshape(-1).tolist(), predictions.tolist())

        return {
            "status": "success",
            "message": "Model trained successfully.",
            "model_path": str(MODEL_PATH),
            "scaler_path": str(SCALER_PATH),
            "training_history": {
                "loss": float(history.history.get("loss", [0])[-1]),
                "val_loss": float(history.history.get("val_loss", [0])[-1]),
                "mae": float(history.history.get("mae", [0])[-1]),
                "val_mae": float(history.history.get("val_mae", [0])[-1]),
            },
            "evaluation_metrics": {
                "mae": evaluation_metrics["mae"],
                "rmse": evaluation_metrics["rmse"],
            },
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Training failed: {exc}",
        }
