import requests
import csv
from datetime import datetime, timezone

# API endpoint
url = "https://api.hypurrscan.io/unstakingQueue"

# Make GET request
response = requests.get(url)
response.raise_for_status()

# Parse the response
data = response.json()

# Output file
csv_filename = "unstaking_queue.csv"

# Convert and write to CSV
with open(csv_filename, mode="w", newline="") as csvfile:
    if data:
        fieldnames = list(data[0].keys()) + ['convertedTimestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            timestamp_ms = row.get("time", 0)
            if isinstance(timestamp_ms, (int, float)) and timestamp_ms > 1e10:
                dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                human_date = dt.strftime("%d %B %Y %H:%M:%S UTC")
            else:
                human_date = "Invalid timestamp"
            row["convertedTimestamp"] = human_date
            writer.writerow(row)

        print(f"✅ Data with human-readable timestamps saved to '{csv_filename}'")
    else:
        print("⚠️ No data received from API.")
