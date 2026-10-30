
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add the project's src folder to Python's import path.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from detector import (
    load_successful_logins,
    detect_impossible_travel,
)
from location_lookup import load_city_database


class TestImpossibleTravelDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the sample login data once for all tests."""
        cls.city_database = load_city_database()
        cls.logins = load_successful_logins(
            ROOT / "data" / "sample_logins.csv",
            cls.city_database,
        )

    def test_failed_login_event_is_excluded(self):
        """Failed login attempts should not be included."""
        charlie_logins = self.logins.get("charlie", [])

        self.assertEqual(len(charlie_logins), 1)
        self.assertEqual(charlie_logins[0]["city"], "Tokyo")
        self.assertEqual(charlie_logins[0]["status"], "success")

    def test_alice_triggers_impossible_travel_alert(self):
        """Alice's rapid New York-to-Tokyo travel should trigger an alert."""
        alerts = detect_impossible_travel(self.logins)

        alice_alerts = [
            alert for alert in alerts
            if alert["user"] == "alice"
        ]

        self.assertEqual(len(alice_alerts), 1)
        self.assertEqual(alice_alerts[0]["from_city"], "New York")
        self.assertEqual(alice_alerts[0]["to_city"], "Tokyo")
        self.assertGreater(alice_alerts[0]["speed_kmh"], 900)

    def test_bob_does_not_trigger_alert(self):
        """Bob's logins should not trigger an impossible-travel alert."""
        alerts = detect_impossible_travel(self.logins)

        bob_alerts = [
            alert for alert in alerts
            if alert["user"] == "bob"
        ]

        self.assertEqual(bob_alerts, [])

    def test_same_timestamp_does_not_trigger_alert(self):
        """Logins with identical timestamps should not trigger an alert."""
        same_time = datetime(
            2026, 10, 30, 10, 0, tzinfo=timezone.utc
        )

        logins = {
            "test_user": [
                {
                    "datetime": same_time,
                    "city": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                {
                    "datetime": same_time,
                    "city": "Tokyo",
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                },
            ]
        }

        alerts = detect_impossible_travel(logins)

        self.assertEqual(alerts, [])

    def test_negative_min_distance_is_rejected(self):
        """A negative minimum distance should be rejected."""
        with self.assertRaises(SystemExit):
            detect_impossible_travel(
                self.logins,
                min_distance_km=-10,
            )

    def test_zero_max_speed_is_rejected(self):
        """A zero maximum travel speed should be rejected."""
        with self.assertRaises(SystemExit):
            detect_impossible_travel(
                self.logins,
                max_travel_speed_kmh=0,
            )


if __name__ == "__main__":
    unittest.main()
