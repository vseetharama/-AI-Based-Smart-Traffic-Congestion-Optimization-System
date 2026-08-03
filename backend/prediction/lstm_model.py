"""LSTM model definition for traffic prediction.

Purpose:
Define a simple but reusable LSTM-based regression model that predicts the next
vehicle count from a sequence of recent traffic features.

The structure is intentionally minimal so it can be extended later for density,
waiting time, or congestion prediction in future phases.
"""

from __future__ import annotations

from typing import Optional

try:
    from tensorflow.keras import layers, models
except Exception:  # pragma: no cover - fallback for environments without TensorFlow
    layers = None
    models = None


def build_lstm_model(input_shape: tuple[int, int], learning_rate: float = 0.001):
    """Create a simple LSTM regression model.

    Purpose:
    Build a compact neural network that learns temporal traffic patterns.

    Parameters:
    input_shape : shape of each input sequence (timesteps, features)
    learning_rate : optimizer learning rate

    Returns:
    Compiled Keras model.
    """
    if models is None or layers is None:
        raise ImportError("TensorFlow is required to build the LSTM model.")

    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.LSTM(64, return_sequences=False),
        layers.Dense(32, activation="relu"),
        layers.Dense(1),
    ])

    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model
