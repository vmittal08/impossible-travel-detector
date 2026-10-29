import csv
from reporting import export_alerts
from collections import defaultdict
from datetime import datetime, timezone

from distance import calculate_distance_km
from location_lookup import (
    load_city_database,
    find_city_coordinates,
    LocationNotFoundError,
    AmbiguousLocationError,
)


MIN_DISTANCE_KM = 500
MAX_TRAVEL_SPEED_KMH = 900

COUNTRY_CODES = {
    "usa": "US",
    "united states": "US",
    "japan": "JP",
    "india": "IN",
    "uk": "GB",
    "united kingdom": "GB",
}


def get_country_code(country):
    """Convert common country names to ISO country codes."""
    normalized = country.strip().casefold()

    if normalized in COUNTRY_CODES:
        return COUNTRY_CODES[normalized]

    if len(normalized) == 2 and normalized.isalpha():
        return normalized.upper()

    raise ValueError(f"Unsupported country name: {country}")


def load_successful_logins(file_path, city_database):
    """Load successful logins and resolve their coordinates."""
    logins_by_user = defaultdict(list)

    with open(file_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "timestamp", "user", "city", "country", "status"
        }
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must contain these columns: {sorted(required_columns)}"
            )

        for row in reader:
            if row["status"].strip().casefold() != "success":
                continue

            try:
                timestamp = datetime.fromisoformat(
                    row["timestamp"].strip().replace("Z", "+00:00")
                )

                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)

                country_code = get_country_code(row["country"])

                latitude, longitude = find_city_coordinates(
                    row["city"], country_code, city_database
                )

                row["datetime"] = timestamp.astimezone(timezone.utc)
                row["latitude"] = latitude
                row["longitude"] = longitude

                logins_by_user[row["user"].strip()].append(row)

            except (
                ValueError,
                LocationNotFoundError,
                AmbiguousLocationError,
            ) as error:
                print(
                    f"WARNING: Skipping login for "
                    f"{row.get('user', 'unknown user')}: {error}"
                )

    for logins in logins_by_user.values():
        logins.sort(key=lambda login: login["datetime"])

    return logins_by_user


def detect_impossible_travel(logins_by_user):
    """Flag consecutive successful logins with implausible travel speeds."""
    alerts = []

    for user, logins in logins_by_user.items():
        for index in range(1, len(logins)):
            previous = logins[index - 1]
            current = logins[index]

            elapsed_seconds = (
                current["datetime"] - previous["datetime"]
            ).total_seconds()

            if elapsed_seconds <= 0:
                continue

            distance_km = calculate_distance_km(
                previous["latitude"],
                previous["longitude"],
                current["latitude"],
                current["longitude"],
            )

            if distance_km < MIN_DISTANCE_KM:
                continue

            elapsed_hours = elapsed_seconds / 3600
            speed_kmh = distance_km / elapsed_hours

            if speed_kmh > MAX_TRAVEL_SPEED_KMH:
                alerts.append({
                    "user": user,
                    "from_city": previous["city"],
                    "to_city": current["city"],
                    "distance_km": round(distance_km, 2),
                    "elapsed_minutes": round(elapsed_seconds / 60, 2),
                    "speed_kmh": round(speed_kmh, 2),
                    "reason": "Implied travel speed exceeds threshold",
                })

    return alerts



def main():
    file_path = "data/sample_logins.csv"
    report_path = "reports/alerts.csv"

    print("Loading geographic database...")
    city_database = load_city_database()

    print("Resolving login locations...")
    logins_by_user = load_successful_logins(
        file_path, city_database
    )

    alerts = detect_impossible_travel(logins_by_user)

    # Save a report even when no alerts are found.
    saved_report = export_alerts(alerts, report_path)

    print("\nIMPOSSIBLE TRAVEL DETECTOR")
    print("=" * 35)

    if not alerts:
        print("No suspicious travel detected.")
    else:
        for alert in alerts:
            print("\nSUSPICIOUS LOGIN PATTERN")
            for field, value in alert.items():
                print(f"{field}: {value}")

    print(f"\nAlerts found: {len(alerts)}")
    print(f"Report saved to: {saved_report}")


if __name__ == "__main__":
    main()
