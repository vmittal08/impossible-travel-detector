
import csv
from collections import defaultdict
from datetime import datetime, timezone

file_path = "data/sample_logins.csv"

logins_by_user = defaultdict(list)

with open(file_path, mode="r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for login in reader:
        if login["status"] == "success":
            login["datetime"] = datetime.fromisoformat(
                login["timestamp"].replace("Z", "+00:00")
            ).astimezone(timezone.utc)

            logins_by_user[login["user"]].append(login)

for user, logins in logins_by_user.items():
    logins.sort(key=lambda login: login["datetime"])

    print(f"\nUser: {user}")

    for login in logins:
        print(f"  {login['datetime']} | {login['city']}")

    if len(logins) >= 2:
        previous = logins[0]
        current = logins[1]

        time_difference = (
            current["datetime"] - previous["datetime"]
        )

        print(f"  Time between first two logins: {time_difference}")
