import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prediction.data_loader import load_traffic_history
from prediction.evaluation import calculate_regression_metrics, evaluate_model
from prediction.preprocessing import prepare_training_data
from prediction.utils import validate_history_frame, format_prediction_output


class PredictionPipelineTests(unittest.TestCase):
    def test_load_traffic_history_returns_dataframe(self):
        df = load_traffic_history()
        self.assertIsInstance(df, pd.DataFrame)

    def test_prepare_training_data_requires_enough_rows(self):
        sample_df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "vehicle_count": [10, 12, 15],
            "waiting_time": [5, 6, 7],
            "recommended_green_time": [30, 35, 40],
            "density_level": ["LOW", "MEDIUM", "HIGH"],
        })

        with self.assertRaises(ValueError):
            prepare_training_data(sample_df, sequence_length=4)

    def test_validate_history_frame(self):
        valid_df = pd.DataFrame({"timestamp": [1], "vehicle_count": [2]})
        self.assertTrue(validate_history_frame(valid_df))

    def test_format_prediction_output(self):
        payload = format_prediction_output({"road_id": 1, "predicted_vehicle_count": 37, "status": "success"})
        self.assertEqual(payload["road_id"], 1)
        self.assertEqual(payload["predicted_vehicle_count"], 37)

    def test_evaluate_model_returns_metrics(self):
        metrics = evaluate_model([1, 2, 3], [1, 2, 4])
        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertGreaterEqual(metrics["mae"], 0)

    def test_calculate_regression_metrics(self):
        metrics = calculate_regression_metrics([1, 2, 3], [1, 2, 4])
        self.assertAlmostEqual(metrics["mae"], 0.3333333333, places=6)
        self.assertAlmostEqual(metrics["rmse"], 0.5773502692, places=6)


if __name__ == "__main__":
    unittest.main()
