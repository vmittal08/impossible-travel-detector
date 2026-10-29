
import csv
from pathlib import Path


DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "geonames"
    / "cities15000.txt"
)


class LocationNotFoundError(Exception):
    """Raised when a city and country cannot be found."""


class AmbiguousLocationError(Exception):
    """Raised when a city and country match multiple locations."""


def normalize_name(name):
    """Normalize a name for case-insensitive matching."""
    return " ".join(name.strip().casefold().split())


def load_city_database(file_path=DATASET_PATH):
    """Index GeoNames cities by country and known names."""
    cities = {}

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")

        for row in reader:
            if len(row) < 19:
                continue

            try:
                latitude = float(row[4])
                longitude = float(row[5])
            except ValueError:
                continue

            country_code = row[8].strip().upper()
            geoname_id = row[0]
            official_name = row[1].strip()

            record = (latitude, longitude, geoname_id, official_name)

            names = {
                normalize_name(row[1]),
                normalize_name(row[2]),
            }

            # GeoNames alternate names are in column 3.
            names.update(
                normalize_name(name)
                for name in row[3].split(",")
                if name.strip()
            )

            for name in names:
                if name:
                    cities.setdefault((name, country_code), {})[
                        geoname_id
                    ] = record

    return cities


def find_city_coordinates(city, country_code, city_database):
    """Return coordinates for an exact city name and country code."""
    key = (normalize_name(city), country_code.strip().upper())
    matches = list(city_database.get(key, {}).values())

    if not matches:
        raise LocationNotFoundError(
            f"City not found: {city}, {country_code}"
        )

    if len(matches) > 1:
        options = [
            {
                "latitude": latitude,
                "longitude": longitude,
                "geoname_id": geoname_id,
                "official_name": official_name,
            }
            for latitude, longitude, geoname_id, official_name in matches
        ]
        raise AmbiguousLocationError(
            f"Multiple matches for {city}, {country_code}: {options}"
        )

    latitude, longitude, _, _ = matches[0]
    return latitude, longitude
