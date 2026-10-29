from datetime import timedelta

distance_km = 10852
time_difference = timedelta(minutes=30)

hours = time_difference.total_seconds() / 3600

if hours > 0:
    speed_kmh = distance_km / hours
    print(f"Implied travel speed: {speed_kmh:,.0f} km/h")
else:
    print("Cannot calculate speed: elapsed time must be positive.")
