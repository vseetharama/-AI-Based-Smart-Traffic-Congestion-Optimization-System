import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
