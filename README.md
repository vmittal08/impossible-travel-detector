# Impossible Travel Detector

A Python-based cybersecurity tool that detects potentially suspicious login activity by analyzing successful authentication events, geographic distance, and elapsed time.

## Features

- **Automatic city geolocation:** Resolves city and country names into coordinates using a local GeoNames dataset.
- **Distance calculation:** Calculates distance between consecutive login locations using the Haversine formula.
- **Impossible-travel detection:** Flags login sequences whose implied travel speed exceeds a configurable threshold.
- **Login filtering:** Excludes failed login events from the travel calculation.
- **CSV alert reports:** Exports detection results to `reports/alerts.csv`.
- **Automated tests:** Uses Python's built-in `unittest` framework.

## How It Works

1. Reads login events from a CSV file.
2. Filters for successful logins and sorts them chronologically per user.
3. Resolves each city and country using the GeoNames database.
4. Calculates distance, elapsed time, and implied travel speed between consecutive logins.
5. Generates alerts when the configured distance and speed thresholds are exceeded.
6. Saves alerts to a CSV report.

## Requirements

- Python 3.10 or newer
- Internet access to download the GeoNames dataset during setup

No third-party Python packages are required.

## Setup

Clone the repository:

```bash
git clone https://github.com/vmittal08/impossible-travel-detector.git
cd impossible-travel-detector
```

Download the GeoNames `cities15000` dataset from:

https://download.geonames.org/export/dump/cities15000.zip

Extract `cities15000.txt` into:

```text
data/geonames/cities15000.txt
```

The dataset is intentionally excluded from Git because of its size.

## Run the Detector

From the project root:

```bash
python src/detector.py
```

The program resolves login locations, evaluates consecutive successful logins, prints suspicious patterns, and writes a CSV report to `reports/alerts.csv`.

## Run Tests

Run all automated tests:

```bash
python -m unittest discover -s tests -v
```

The tests cover location lookup, impossible-travel detection, failed-login filtering, and CSV report generation.

## Configuration

The detector currently uses these thresholds in `src/detector.py`:

- `MIN_DISTANCE_KM = 500`
- `MAX_TRAVEL_SPEED_KMH = 900`

These values are initial heuristics and should be tuned for the environment being monitored.

## Sample Alert

The synthetic sample dataset includes a successful login from New York followed by a login from Tokyo 30 minutes later.

The detector flags the sequence because the calculated distance is approximately 10,849 km and the implied speed is far above the configured threshold.

## Limitations

- The included login data is synthetic and uses documentation-only IP addresses.
- City-level geolocation is approximate and does not establish a user's exact physical location.
- VPNs, proxies, mobile networks, and inaccurate location data can produce false positives.
- The current prototype uses city and country fields; it does not yet perform IP geolocation.
- An alert indicates suspicious activity for investigation, not confirmed account compromise.

## Dataset Attribution

Geographic data is provided by GeoNames:

https://www.geonames.org/

GeoNames data is available under the Creative Commons Attribution 4.0 License (CC BY 4.0). See the GeoNames website for dataset details and attribution requirements.

## Disclaimer

This project is intended for educational and authorized defensive cybersecurity use.
