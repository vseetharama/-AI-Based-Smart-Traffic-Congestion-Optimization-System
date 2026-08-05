import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "../")

import analytics
from analytics import _format_period_label


class FakeCursor:
    def __init__(self, docs):
        self.docs = docs
        self.sort_calls = []
        self.limit_value = None
        self.hint_value = None

    def sort(self, field, direction):
        self.sort_calls.append((field, direction))
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def hint(self, value):
        self.hint_value = value
        return self

    def __iter__(self):
        return iter(self.docs)


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = docs or []
        self.aggregate_calls = []
        self.find_calls = []
        self.find_result = FakeCursor(self.docs)

    def aggregate(self, pipeline, **kwargs):
        self.aggregate_calls.append(kwargs)
        return [{}]

    def find(self, query, **kwargs):
        self.find_calls.append((query, kwargs))
        return self.find_result


class AnalyticsPeriodLabelTests(unittest.TestCase):
    def test_missing_month_is_rendered_safely(self):
        self.assertEqual(_format_period_label({"year": 2024, "month": None}, "month"), "2024-00")

    def test_missing_week_is_rendered_safely(self):
        self.assertEqual(_format_period_label({"year": 2024, "week": None}, "week"), "W00")


class AnalyticsQueryBehaviorTests(unittest.TestCase):
    def test_today_summary_uses_recent_window_and_disk_aggregation(self):
        collection = FakeCollection([{"timestamp": datetime.now(timezone.utc), "vehicle_count": 3, "density_level": "LOW"}])
        original_get_collection = analytics._get_collection
        analytics._get_collection = lambda: collection
        try:
            analytics.get_today_summary()
        finally:
            analytics._get_collection = original_get_collection

        self.assertTrue(collection.aggregate_calls[0].get("allowDiskUse"))
        # Summary now requests full history (no default 2000 limit)
        self.assertIsNone(collection.find_result.limit_value)

    def test_weekly_and_monthly_summary_use_recent_windows(self):
        collection = FakeCollection([{"timestamp": datetime.now(timezone.utc), "vehicle_count": 3, "density_level": "LOW"}])
        original_get_collection = analytics._get_collection
        analytics._get_collection = lambda: collection
        try:
            analytics.get_weekly_summary()
            analytics.get_monthly_summary()
        finally:
            analytics._get_collection = original_get_collection

        self.assertTrue(collection.aggregate_calls[0].get("allowDiskUse"))
        self.assertTrue(collection.aggregate_calls[1].get("allowDiskUse"))

    def test_history_uses_recent_window_and_indexes_sorting(self):
        collection = FakeCollection([{"timestamp": datetime.now(timezone.utc), "vehicle_count": 3, "density_level": "LOW"}])
        original_get_collection = analytics._get_collection
        analytics._get_collection = lambda: collection
        try:
            analytics.get_history()
        finally:
            analytics._get_collection = original_get_collection

        self.assertEqual(collection.find_result.sort_calls[0], ("timestamp", 1))
        self.assertEqual(collection.find_result.limit_value, 2000)


if __name__ == "__main__":
    unittest.main()
