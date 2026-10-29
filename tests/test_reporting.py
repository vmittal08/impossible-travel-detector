import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reporting import export_alerts


class TestReporting(unittest.TestCase):

    def test_export_alerts_to_csv(self):
        alerts = [
            {
                "user": "alice",
                "from_city": "New York",
                "to_city": "Tokyo",
                "distance_km": 10848.66,
                "elapsed_minutes": 30.0,
                "speed_kmh": 21697.33,
                "reason": "Implied travel speed exceeds threshold",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "alerts.csv"
            saved_path = export_alerts(alerts, report_path)

            self.assertTrue(saved_path.exists())

            with saved_path.open(
                newline="", encoding="utf-8-sig"
            ) as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["user"], "alice")
            self.assertEqual(rows[0]["to_city"], "Tokyo")

    def test_empty_alerts_still_create_header(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "alerts.csv"
            export_alerts([], report_path)

            with report_path.open(
                newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = list(reader)

            self.assertIn("user", header)
            self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
