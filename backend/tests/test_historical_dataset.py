import csv
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.generate_historical_dataset import generate_historical_dataset, write_dataset_csv
from tools.import_historical_dataset import load_csv_rows


class HistoricalDatasetTests(unittest.TestCase):
    def test_generate_historical_dataset_returns_expected_rows(self):
        rows = generate_historical_dataset(days=2, interval_minutes=60, roads=["road1", "road2"])
        self.assertGreater(len(rows), 0)
        self.assertEqual(rows[0]["road_id"], "road1")
        self.assertIn("timestamp", rows[0])
        self.assertIn("vehicle_count", rows[0])

    def test_write_dataset_csv_creates_file(self):
        rows = generate_historical_dataset(days=1, interval_minutes=60, roads=["road1"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "sample.csv"
            write_dataset_csv(rows, output_path)
            self.assertTrue(output_path.exists())
            with output_path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                saved_rows = list(reader)
            self.assertEqual(len(saved_rows), len(rows))

    def test_generated_rows_include_live_schema_fields(self):
        rows = generate_historical_dataset(days=1, interval_minutes=60, roads=["road1"])
        self.assertIn("current_green_road", rows[0])
        self.assertIn("current_timer", rows[0])
        self.assertIsInstance(rows[0]["prediction"], str)
        self.assertIn("traffic expected", rows[0]["prediction"].lower())

    def test_load_csv_rows_preserves_live_schema_fields(self):
        rows = generate_historical_dataset(days=1, interval_minutes=60, roads=["road1"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "schema.csv"
            write_dataset_csv(rows, output_path)
            loaded_rows = load_csv_rows(output_path)
            self.assertIn("current_green_road", loaded_rows[0])
            self.assertIn("current_timer", loaded_rows[0])

    def test_generated_rows_assign_exactly_one_green_road_per_timestamp(self):
        rows = generate_historical_dataset(days=1, interval_minutes=60, roads=["road1", "road2", "road3"])
        buckets: dict[str, list[dict]] = {}
        for row in rows:
            buckets.setdefault(row["timestamp"], []).append(row)

        for bucket in buckets.values():
            green_rows = [row for row in bucket if row["signal_status"] == "GREEN"]
            self.assertEqual(len(green_rows), 1)
            active_row = green_rows[0]
            self.assertEqual(active_row["current_green_road"], active_row["road_id"])
            self.assertGreater(active_row["current_timer"], 0)
            for row in bucket:
                if row is not active_row:
                    self.assertEqual(row["signal_status"], "RED")
                    self.assertEqual(row["current_green_road"], active_row["road_id"])
                    self.assertEqual(row["current_timer"], 0)


if __name__ == "__main__":
    unittest.main()
