\# Impossible Travel Detector



A Python-based cybersecurity project that identifies potentially suspicious login activity by analysing successful authentication events, geographic distance, and elapsed time.



\## Project Objective



Detect consecutive successful logins for the same account when the implied travel speed exceeds a configurable threshold.



\## Features



\- Reads authentication events from a CSV file

\- Filters successful logins

\- Groups events by user and sorts them chronologically

\- Calculates geographic distance using the Haversine formula

\- Calculates elapsed time and implied travel speed

\- Generates alerts for suspicious login patterns



\## Technology



\- Python 3

\- CSV processing

\- datetime

\- Haversine formula

\- Git and GitHub



\## Run the Project



From the project root, run:



```bash

python src/detector.py

```



\## Configuration



The prototype uses these initial thresholds:



\- Minimum distance: 500 km

\- Maximum implied travel speed: 900 km/h



These are configurable demonstration values, not universal security rules.



\## Sample Detection



The synthetic dataset includes a successful login from New York followed by one from Tokyo 30 minutes later.



The detector flags this pair because the implied travel speed exceeds the configured threshold.



\## Limitations



\- Uses synthetic login records

\- Assumes the supplied geographic coordinates are accurate

\- Does not establish whether an account is actually compromised

\- Does not account for VPNs, proxies, or all legitimate travel scenarios

\- Uses simple threshold-based detection rather than a production SIEM



\## Future Improvements



\- Automated unit tests

\- Input validation and error handling

\- Structured alert reports

\- More realistic authentication datasets

\- Detection tuning and false-positive analysis

\- SIEM integration



\## Disclaimer



This project is for educational purposes and defensive security analysis.



