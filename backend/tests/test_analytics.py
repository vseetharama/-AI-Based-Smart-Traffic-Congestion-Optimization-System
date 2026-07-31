import sys
import unittest

sys.path.insert(0, "../")

from analytics import _format_period_label


class AnalyticsPeriodLabelTests(unittest.TestCase):
    def test_missing_month_is_rendered_safely(self):
        self.assertEqual(_format_period_label({"year": 2024, "month": None}, "month"), "2024-00")

    def test_missing_week_is_rendered_safely(self):
        self.assertEqual(_format_period_label({"year": 2024, "week": None}, "week"), "W00")


if __name__ == "__main__":
    unittest.main()
