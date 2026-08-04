"""Training entry-point for the Phase 1 LSTM prediction model.

Purpose:
Load traffic data, preprocess it, train the model, and save the trained model
for later prediction.

The script is intentionally isolated from the existing application so the
Version 1.5 workflow remains intact.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pickle
import csv
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from tensorflow.keras.callbacks import Callback

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from prediction.data_loader import load_traffic_history
from prediction.dataset import train_test_split_sequences
from prediction.evaluation import calculate_regression_metrics
from prediction.lstm_model import build_lstm_model
from prediction.preprocessing import prepare_training_data


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "traffic_predictor.keras"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "uploads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class TrainingProgressLogger(Callback):
    def on_train_begin(self, logs=None):
        logger.info("Training started with %s epochs", self.params.get("epochs", "unknown"))

    def on_epoch_end(self, epoch, logs=None):
        if not logs:
            return
        logger.info(
            "Epoch %d/%d | loss=%.6f | val_loss=%.6f | mae=%.6f | val_mae=%.6f",
            epoch + 1,
            self.params.get("epochs", 0),
            logs.get("loss", 0.0),
            logs.get("val_loss", 0.0),
            logs.get("mae", 0.0),
            logs.get("val_mae", 0.0),
        )


def _build_actual_vs_predicted_samples(
    y_val: np.ndarray,
    predictions: np.ndarray,
    scaler: Any,
    feature_count: int,
    limit: int = 10,
) -> list[dict[str, float]]:
    pred_vals = scaler.inverse_transform(
        np.concatenate([predictions.reshape(-1, 1), np.zeros((len(predictions), feature_count - 1))], axis=1)
    )[:, 0]
    act_vals = scaler.inverse_transform(
        np.concatenate([y_val.reshape(-1, 1), np.zeros((len(y_val), feature_count - 1))], axis=1)
    )[:, 0]

    rows = []
    for i, (actual, predicted) in enumerate(zip(act_vals[:limit], pred_vals[:limit])):
        rows.append({
            "index": int(i),
            "actual_vehicle_count": float(actual),
            "predicted_vehicle_count": float(predicted),
            "error": float(actual) - float(predicted),
        })
    return rows


def _save_json(path: Path, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def _save_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def train_model(
    sequence_length: int = 12,
    epochs: int = 10,
    batch_size: int = 16,
    output_dir: Path | str | None = None,
) -> dict:
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
        progress_logger = TrainingProgressLogger()
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
            callbacks=[progress_logger],
        )

        model.save(MODEL_PATH)
        with open(SCALER_PATH, "wb") as handle:
            pickle.dump(scaler, handle)

        predictions = model.predict(X_val, verbose=0).reshape(-1)
        evaluation_metrics = calculate_regression_metrics(y_val.reshape(-1).tolist(), predictions.tolist())

        output_dir = Path(output_dir or OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = output_dir / "prediction_evaluation_metrics.json"
        comparison_path = output_dir / "prediction_actual_vs_predicted.csv"

        result = {
            "status": "success",
            "message": "Model trained successfully.",
            "model_path": str(MODEL_PATH),
            "scaler_path": str(SCALER_PATH),
            "metrics_path": str(metrics_path),
            "comparison_path": str(comparison_path),
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

        actual_vs_predicted_rows = _build_actual_vs_predicted_samples(
            y_val=y_val,
            predictions=predictions,
            scaler=scaler,
            feature_count=X.shape[2],
            limit=10,
        )

        _save_json(metrics_path, result)
        _save_csv(comparison_path, actual_vs_predicted_rows)

        logger.info("Evaluation metrics saved to %s", metrics_path)
        logger.info("Actual vs predicted comparison saved to %s", comparison_path)

        return result
    except Exception as exc:
        logger.exception("Training failed")
        return {
            "status": "error",
            "message": f"Training failed: {exc}",
        }


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Train the Phase 1 traffic prediction model.")
    parser.add_argument("--sequence-length", type=int, default=12)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    logger.info("Starting training pipeline")
    result = train_model(
        sequence_length=args.sequence_length,
        epochs=args.epochs,
        batch_size=args.batch_size,
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
