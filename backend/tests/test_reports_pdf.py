import base64
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reports import build_pdf_report


class ReportPDFTests(unittest.TestCase):
    @patch("reports._get_range_records")
    @patch("reports._build_summary_payload")
    def test_build_pdf_report_generates_am_pm_timestamp(self, mock_summary, mock_get_records):
        mock_summary.return_value = {"status": "success", "summary": {}, "charts": {}}
        mock_get_records.return_value = [
            {"timestamp": "2026-08-04T09:26:05+00:00", "road_name": "Road 1", "vehicle_count": 3, "density_level": "LOW", "signal_status": "GREEN", "waiting_time": 0, "recommended_green_time": 40, "prediction": "low"},
        ]

        pdf_content = build_pdf_report("today")
        pdf_bytes = base64.b64decode(pdf_content)
        pdf_text = pdf_bytes.decode("latin-1", errors="ignore")

        self.assertIn("Generated Date:", pdf_text)
        self.assertRegex(pdf_text, r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2} (AM|PM)")


if __name__ == "__main__":
    unittest.main()
