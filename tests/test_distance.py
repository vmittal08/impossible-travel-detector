import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from distance import calculate_distance_km

distance = calculate_distance_km(
    40.7128, -74.0060,   # New York
    35.6762, 139.6503    # Tokyo
)

print(f"Distance from New York to Tokyo: {distance:,.0f} km")
