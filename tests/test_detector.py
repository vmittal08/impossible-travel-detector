import sys
import unittest
from pathlib import Path

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
        cls.city_database = load_city_database()
        cls.logins = load_successful_logins(
            ROOT / "data" / "sample_logins.csv",
            cls.city_database,
        )

    def test_failed_login_event_is_excluded(self):
        charlie_logins = self.logins.get("charlie", [])

        self.assertEqual(len(charlie_logins), 1)
        self.assertEqual(charlie_logins[0]["city"], "Tokyo")
        self.assertEqual(charlie_logins[0]["status"], "success")

    def test_alice_triggers_impossible_travel_alert(self):
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
        alerts = detect_impossible_travel(self.logins)

        bob_alerts = [
            alert for alert in alerts
            if alert["user"] == "bob"
        ]

        self.assertEqual(bob_alerts, [])


if __name__ == "__main__":
    unittest.main()
