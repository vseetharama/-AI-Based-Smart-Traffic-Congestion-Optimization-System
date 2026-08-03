"""Dataset helpers for training and validation splits.

Purpose:
Split the prepared LSTM sequences into training and validation sets while
keeping the workflow simple and reusable.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np


def train_test_split_sequences(X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split the LSTM sequences into train/validation sets.

    Purpose:
    Reserve a portion of the data for validation so that overfitting can be
    detected during model training.

    Parameters:
    X : LSTM input sequences.
    y : target values.
    validation_split : fraction of data used for validation.

    Returns:
    X_train, X_val, y_train, y_val
    """
    if X.shape[0] < 2:
        raise ValueError("Not enough sequences to split into train and validation sets.")

    split_index = int(len(X) * (1 - validation_split))
    split_index = max(1, min(split_index, len(X) - 1))

    X_train, X_val = X[:split_index], X[split_index:]
    y_train, y_val = y[:split_index], y[split_index:]
    return X_train, X_val, y_train, y_val
