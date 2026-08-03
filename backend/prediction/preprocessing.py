"""Preprocessing utilities for LSTM traffic prediction.

Purpose:
Prepare the historical traffic data into model-ready sequences for LSTM training
and inference.

The code is written to be modular so that future phases can easily extend the
feature set to density, waiting time, or congestion.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def _prepare_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Create a cleaned feature table from raw traffic records.

    Purpose:
    Keep only the fields needed for the initial vehicle-count prediction model.
    Missing values are filled with safe defaults so training is resilient.

    Parameters:
    df : DataFrame with traffic history.

    Returns:
    A cleaned DataFrame with numeric features only.
    """
    feature_frame = df.copy()

    if feature_frame.empty:
        return feature_frame

    # Keep the original timestamp as a reference but use numeric time features
    # so the model can learn temporal patterns.
    feature_frame["hour"] = feature_frame["timestamp"].dt.hour.fillna(0)
    feature_frame["day_of_week"] = feature_frame["timestamp"].dt.dayofweek.fillna(0)
    feature_frame["day"] = feature_frame["timestamp"].dt.day.fillna(0)

    # Fill missing values so the model does not fail on incomplete records.
    numeric_columns = ["vehicle_count", "waiting_time", "recommended_green_time"]
    for column in numeric_columns:
        feature_frame[column] = pd.to_numeric(feature_frame[column], errors="coerce").fillna(0)

    # Density is encoded into numeric values to make the model easier to train.
    density_mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    feature_frame["density_code"] = feature_frame["density_level"].str.upper().map(density_mapping).fillna(1)

    # Keep only the features useful for the first LSTM iteration.
    selected_features = ["vehicle_count", "waiting_time", "recommended_green_time", "density_code", "hour", "day_of_week", "day"]
    feature_frame = feature_frame[selected_features].astype(float)
    return feature_frame


def create_sequences(data: np.ndarray, sequence_length: int = 12) -> Tuple[np.ndarray, np.ndarray]:
    """Convert time-series data into supervised learning sequences.

    Purpose:
    LSTM models learn from sequences, not isolated rows. This function creates
    sliding windows of historical values so the model can learn from patterns.

    Parameters:
    data : numeric time-series values.
    sequence_length : number of past steps included in each input window.

    Returns:
    X : sequence inputs with shape (samples, sequence_length, features)
    y : next-step target values
    """
    if len(data) <= sequence_length:
        raise ValueError("Not enough data to create LSTM sequences.")

    X, y = [], []
    for index in range(len(data) - sequence_length):
        X.append(data[index:index + sequence_length])
        y.append(data[index + sequence_length, 0])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def prepare_training_data(df: pd.DataFrame, sequence_length: int = 12) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """Prepare the training dataset for LSTM model training.

    Purpose:
    Normalize features and convert them into LSTM-ready sequences.

    Parameters:
    df : DataFrame containing historical traffic features.
    sequence_length : number of time steps in one sequence.

    Returns:
    X_train : training sequences
    y_train : training targets
    scaler : fitted scaler used for future inference
    """
    feature_frame = _prepare_feature_frame(df)
    if feature_frame.empty:
        raise ValueError("Input DataFrame is empty.")

    # Normalization is important because neural networks learn more effectively
    # when features share a similar numeric scale.
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(feature_frame)

    X, y = create_sequences(scaled_features, sequence_length=sequence_length)
    return X, y, scaler
