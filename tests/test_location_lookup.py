import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from location_lookup import (
    load_city_database,
    find_city_coordinates,
    LocationNotFoundError,
)


class TestLocationLookup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.city_database = load_city_database()

    def test_known_cities(self):
        cities = [
            ("New York", "US"),
            ("Tokyo", "JP"),
            ("Mumbai", "IN"),
            ("Pune", "IN"),
            ("London", "GB"),
        ]

        for city, country_code in cities:
            with self.subTest(city=city):
                latitude, longitude = find_city_coordinates(
                    city, country_code, self.city_database
                )
                self.assertGreaterEqual(latitude, -90)
                self.assertLessEqual(latitude, 90)
                self.assertGreaterEqual(longitude, -180)
                self.assertLessEqual(longitude, 180)

    def test_unknown_city(self):
        with self.assertRaises(LocationNotFoundError):
            find_city_coordinates(
                "DefinitelyNotARealCity", "US", self.city_database
            )


if __name__ == "__main__":
    unittest.main()
