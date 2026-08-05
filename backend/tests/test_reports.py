import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "../")

from reports import build_report_range, build_csv_report


class ReportGenerationTests(unittest.TestCase):
    def test_build_report_range_today_returns_start_and_end_of_day(self):
        start, end = build_report_range("today")
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertLessEqual(start, end)

    def test_build_csv_report_includes_expected_headers(self):
        csv_content = build_csv_report("today", records=[])
        self.assertIn("Timestamp,Road,Vehicle Count,Density,Signal Status,Waiting Time,Recommended Green Time,Prediction", csv_content)

    def test_build_csv_report_formats_timestamps_am_pm(self):
        records = [
            {"timestamp": "2026-08-04T09:26:05+00:00", "road_name": "Road 1", "vehicle_count": 3, "density_level": "LOW", "signal_status": "GREEN", "waiting_time": 0, "recommended_green_time": 40, "prediction": "low"},
        ]
        csv_content = build_csv_report("today", records=records)
        # UTC 09:26:05 converts to Asia/Kolkata (+5:30) -> 14:56:05 (02:56:05 PM)
        self.assertIn("04-08-2026 02:56:05 PM", csv_content)

    @patch("reports._get_range_records")
    def test_build_csv_report_loads_weekly_range_records(self, mock_get_range_records):
        mock_get_range_records.return_value = [
            {"timestamp": "2026-08-03T12:00:00+00:00", "road_name": "Road 1", "vehicle_count": 5, "density_level": "LOW", "signal_status": "GREEN", "waiting_time": 0, "recommended_green_time": 40, "prediction": "low"},
            {"timestamp": "2026-08-02T10:15:00+00:00", "road_name": "Road 2", "vehicle_count": 8, "density_level": "MEDIUM", "signal_status": "RED", "waiting_time": 12, "recommended_green_time": 60, "prediction": "medium"},
        ]
        csv_content = build_csv_report("weekly")
        self.assertIn("Road 1", csv_content)
        self.assertIn("Road 2", csv_content)


if __name__ == "__main__":
    unittest.main()
