"""Evaluation helpers for the traffic prediction pipeline.

Purpose:
Provide simple, beginner-friendly metrics so the trained model can be assessed
without introducing extra complexity.

Inputs:
actual_values : list-like of true target values
predicted_values : list-like of model predictions

Outputs:
Dictionary containing MAE and RMSE values.
"""

from __future__ import annotations

import math
from typing import Sequence


def calculate_regression_metrics(actual_values: Sequence[float], predicted_values: Sequence[float]) -> dict[str, float]:
    """Calculate MAE and RMSE for regression predictions.

    Purpose:
    These metrics are simple and widely used in machine learning. They help us
    understand how far the model predictions are from the true values.

    Example:
        calculate_regression_metrics([10, 20], [12, 18])
    """
    if len(actual_values) != len(predicted_values):
        raise ValueError("Actual and predicted values must be the same length.")

    if not actual_values:
        raise ValueError("No values were provided for evaluation.")

    errors = [float(actual) - float(predicted) for actual, predicted in zip(actual_values, predicted_values)]
    absolute_errors = [abs(error) for error in errors]
    squared_errors = [error * error for error in errors]

    mae = sum(absolute_errors) / len(absolute_errors)
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))

    return {"mae": mae, "rmse": rmse}


def evaluate_model(actual_values: Sequence[float], predicted_values: Sequence[float]) -> dict[str, float]:
    """Compatibility wrapper for model evaluation.

    Purpose:
    Keep the training, testing, and reporting code easy to read by exposing a
    simple helper name that can be reused across the package.
    """
    return calculate_regression_metrics(actual_values, predicted_values)
