"""Generate Phase 1C-A report details from the current dataset and model.

This helper uses the existing prediction pipeline and does not modify it.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import csv
import logging
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prediction.data_loader import load_traffic_history
from prediction.preprocessing import prepare_training_data
from prediction.dataset import train_test_split_sequences
from prediction.lstm_model import build_lstm_model
from prediction.evaluation import calculate_regression_metrics


def main() -> None:
    df = load_traffic_history()
    X, y, scaler = prepare_training_data(df, sequence_length=12)
    X_train, X_val, y_train, y_val = train_test_split_sequences(X, y, validation_split=0.2)

    model = build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=10,
        batch_size=16,
        verbose=0,
    )

    predictions = model.predict(X_val, verbose=0).reshape(-1)
    eval_metrics = calculate_regression_metrics(y_val.reshape(-1).tolist(), predictions.tolist())

    pred_vals = scaler.inverse_transform(
        np.concatenate([predictions.reshape(-1, 1), np.zeros((len(predictions), X.shape[2] - 1))], axis=1)
    )[:, 0]
    act_vals = scaler.inverse_transform(
        np.concatenate([y_val.reshape(-1, 1), np.zeros((len(y_val), X.shape[2] - 1))], axis=1)
    )[:, 0]

    sample_rows = [
        {"index": int(i), "actual_vehicle_count": float(act), "predicted_vehicle_count": float(pred)}
        for i, (act, pred) in enumerate(zip(act_vals[:10], pred_vals[:10]))
    ]

    output = {
        "training_history": {
            "loss": float(history.history["loss"][-1]),
            "val_loss": float(history.history["val_loss"][-1]),
            "mae": float(history.history["mae"][-1]),
            "val_mae": float(history.history["val_mae"][-1]),
        },
        "evaluation_metrics": {
            "mae": eval_metrics["mae"],
            "rmse": eval_metrics["rmse"],
        },
        "sample_actual_vs_predicted": sample_rows,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
