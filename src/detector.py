import argparse
import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from distance import calculate_distance_km
from location_lookup import (
    load_city_database,
    find_city_coordinates,
    LocationNotFoundError,
    AmbiguousLocationError,
)
from reporting import export_alerts


# Default detection thresholds
MIN_DISTANCE_KM = 500
MAX_TRAVEL_SPEED_KMH = 900


# Common country names and their ISO country codes
COUNTRY_CODES = {
    "usa": "US",
    "united states": "US",
    "united states of america": "US",
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
    """Load successful login events and resolve city coordinates."""
    logins_by_user = defaultdict(list)

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "timestamp",
            "user",
            "city",
            "country",
            "status",
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "CSV must contain these columns: "
                f"{sorted(required_columns)}"
            )

        for row in reader:
            if (row.get("status") or "").strip().casefold() != "success":
                continue

            try:
                timestamp_text = (row.get("timestamp") or "").strip()

                timestamp = datetime.fromisoformat(
                    timestamp_text.replace("Z", "+00:00")
                )

                # Treat timestamps without a timezone as UTC.
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)

                user = (row.get("user") or "").strip()
                city = (row.get("city") or "").strip()
                country = (row.get("country") or "").strip()

                if not user or not city or not country:
                    raise ValueError(
                        "User, city, and country must not be empty"
                    )

                country_code = get_country_code(country)

                latitude, longitude = find_city_coordinates(
                    city,
                    country_code,
                    city_database,
                )

                row["user"] = user
                row["city"] = city
                row["datetime"] = timestamp.astimezone(timezone.utc)
                row["latitude"] = latitude
                row["longitude"] = longitude

                logins_by_user[user].append(row)

            except (
                ValueError,
                LocationNotFoundError,
                AmbiguousLocationError,
            ) as error:
                print(
                    "WARNING: Skipping login for "
                    f"{row.get('user') or 'unknown user'}: {error}"
                )

    # Ensure each user's login events are chronological.
    for logins in logins_by_user.values():
        logins.sort(key=lambda login: login["datetime"])

    return logins_by_user


def detect_impossible_travel(
    logins_by_user,
    min_distance_km=MIN_DISTANCE_KM,
    max_travel_speed_kmh=MAX_TRAVEL_SPEED_KMH,
):
    """Flag consecutive successful logins with implausible travel speeds."""
    alerts = []

    for user, logins in logins_by_user.items():
        for index in range(1, len(logins)):
            previous = logins[index - 1]
            current = logins[index]

            elapsed_seconds = (
                current["datetime"] - previous["datetime"]
            ).total_seconds()

            # Ignore duplicate or out-of-order timestamps.
            if elapsed_seconds <= 0:
                continue

            distance_km = calculate_distance_km(
                previous["latitude"],
                previous["longitude"],
                current["latitude"],
                current["longitude"],
            )

            if distance_km < min_distance_km:
                continue

            elapsed_hours = elapsed_seconds / 3600
            speed_kmh = distance_km / elapsed_hours

            if speed_kmh > max_travel_speed_kmh:
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


def build_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Detect suspicious login travel patterns."
    )

    parser.add_argument(
        "--input",
        default="data/sample_logins.csv",
        help="Path to the login events CSV file.",
    )

    parser.add_argument(
        "--output",
        default="reports/alerts.csv",
        help="Path where the alert report will be saved.",
    )

    parser.add_argument(
        "--min-distance",
        type=float,
        default=MIN_DISTANCE_KM,
        help="Minimum distance in km to evaluate (default: 500).",
    )

    parser.add_argument(
        "--max-speed",
        type=float,
        default=MAX_TRAVEL_SPEED_KMH,
        help="Maximum plausible travel speed in km/h (default: 900).",
    )

    return parser


def main():
    """Run the detector using command-line configuration."""
    parser = build_parser()
    args = parser.parse_args()

    # Validate threshold values.
    if args.min_distance < 0:
        parser.error("--min-distance must be non-negative.")

    if args.max_speed <= 0:
        parser.error("--max-speed must be greater than zero.")

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate the input before loading the geographic database.
    if not input_path.is_file():
        parser.error(f"Input CSV file not found: {input_path}")

    print("Loading geographic database...")

    try:
        city_database = load_city_database()
    except (FileNotFoundError, OSError) as error:
        parser.error(f"Could not load geographic database: {error}")

    print("Resolving login locations...")

    try:
        logins_by_user = load_successful_logins(
            input_path,
            city_database,
        )
    except (OSError, csv.Error, ValueError) as error:
        parser.error(f"Could not process input CSV: {error}")

    alerts = detect_impossible_travel(
        logins_by_user,
        min_distance_km=args.min_distance,
        max_travel_speed_kmh=args.max_speed,
    )

    try:
        saved_report = export_alerts(alerts, output_path)
    except (OSError, csv.Error) as error:
        parser.error(f"Could not save alert report: {error}")

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
