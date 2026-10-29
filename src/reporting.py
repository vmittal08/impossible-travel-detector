
import csv
from pathlib import Path


REPORT_FIELDS = [
    "user",
    "from_city",
    "to_city",
    "distance_km",
    "elapsed_minutes",
    "speed_kmh",
    "reason",
]


def export_alerts(alerts, output_path):
    """Export detection alerts to a CSV report."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=REPORT_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(alerts)

    return output_path
