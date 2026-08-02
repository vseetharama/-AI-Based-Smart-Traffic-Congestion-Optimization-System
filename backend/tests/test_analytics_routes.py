import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "../")

import app as flask_app


class AnalyticsRouteContractTests(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.app.test_client()

    def test_weekly_route_returns_summary_payload_directly(self):
        payload = {"status": "success", "summary": {"totalVehicles": 10}, "charts": {"trafficTrend": []}}

        with patch("app.get_weekly_summary", return_value=payload):
            response = self.client.get("/analytics/weekly")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), payload)

    def test_monthly_route_returns_summary_payload_directly(self):
        payload = {"status": "success", "summary": {"totalVehicles": 10}, "charts": {"trafficTrend": []}}

        with patch("app.get_monthly_summary", return_value=payload):
            response = self.client.get("/analytics/monthly")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), payload)


if __name__ == "__main__":
    unittest.main()
