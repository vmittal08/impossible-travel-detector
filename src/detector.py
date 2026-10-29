import csv
from collections import defaultdict
from datetime import datetime, timezone

from distance import calculate_distance_km


MIN_DISTANCE_KM = 500
MAX_TRAVEL_SPEED_KMH = 900


def load_successful_logins(file_path):
    logins_by_user = defaultdict(list)

    with open(file_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for login in reader:
            if login["status"].strip().lower() != "success":
                continue

            login["datetime"] = datetime.fromisoformat(
                login["timestamp"].replace("Z", "+00:00")
            ).astimezone(timezone.utc)

            login["latitude"] = float(login["latitude"])
            login["longitude"] = float(login["longitude"])

            logins_by_user[login["user"]].append(login)

    for logins in logins_by_user.values():
        logins.sort(key=lambda login: login["datetime"])

    return logins_by_user


def detect_impossible_travel(logins_by_user):
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
    logins_by_user = load_successful_logins(file_path)
    alerts = detect_impossible_travel(logins_by_user)

    print("IMPOSSIBLE TRAVEL DETECTOR")
    print("=" * 35)

    if not alerts:
        print("No suspicious travel detected.")
        return

    for alert in alerts:
        print("\nSUSPICIOUS LOGIN PATTERN")
        for field, value in alert.items():
            print(f"{field}: {value}")


if __name__ == "__main__":
    main()
