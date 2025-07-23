import csv
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# Config
input_csv = "unstaking_queue.csv"
output_csv = "weekly_aggregation_formatted.csv"
HYPE_PRICE = 46.39  # USD per token
WEI_DECIMALS = 8    # 1 HYPE = 10^8 wei

# Convert timestamp (ms) to week start (Monday)
def get_week_start(ms):
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    week_start = dt - timedelta(days=dt.weekday())
    return week_start.strftime("%Y-%m-%d")

# Aggregate wei by week
weekly_aggregates = defaultdict(float)

with open(input_csv, mode="r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            time_ms = int(row["time"])
            wei = float(row["wei"])
            week = get_week_start(time_ms)
            weekly_aggregates[week] += wei
        except (KeyError, ValueError):
            continue  # Skip malformed rows

# Write results with token and USD values
with open(output_csv, mode="w", newline="") as csvfile:
    fieldnames = ["week_start", "total_wei", "total_tokens", "usd_amount", "usd_amount_formatted"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for week, total_wei in sorted(weekly_aggregates.items()):
        total_tokens = total_wei / (10 ** WEI_DECIMALS)
        usd_amount = total_tokens * HYPE_PRICE
        usd_formatted = f"${usd_amount:,.2f}"

        writer.writerow({
            "week_start": week,
            "total_wei": f"{total_wei:.0f}",
            "total_tokens": f"{total_tokens:.8f}",
            "usd_amount": f"{usd_amount:.2f}",
            "usd_amount_formatted": usd_formatted
        })

print(f"✅ Corrected weekly aggregation saved to '{output_csv}'")
