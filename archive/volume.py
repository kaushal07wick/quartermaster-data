import os
import csv
from collections import defaultdict
from datetime import datetime

DATA_FOLDER = "Data"
OUTPUT_FILE = "cumulative_volume_chart.csv"

def load_csv_volumes(file_path):
    daily = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip timezone info and normalize date
            date = row["snapped_at"].split(" ")[0]
            volume = float(row["volume"])
            daily[date] = daily.get(date, 0) + volume
    return daily

def is_cex(filename):
    return filename.endswith("_CEX.csv") and not filename.endswith("_f_CEX.csv")

def is_dex(filename):
    return filename.endswith("_DEX.csv")

def main():
    cex_totals = defaultdict(float)
    dex_totals = defaultdict(float)

    for file in os.listdir(DATA_FOLDER):
        path = os.path.join(DATA_FOLDER, file)

        if is_cex(file):
            volumes = load_csv_volumes(path)
            for date, vol in volumes.items():
                cex_totals[date] += vol

        elif is_dex(file):
            volumes = load_csv_volumes(path)
            for date, vol in volumes.items():
                dex_totals[date] += vol

    # Union of all dates from both categories
    all_dates = sorted(set(cex_totals.keys()) | set(dex_totals.keys()))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "CEX", "DEX"])
        for date in all_dates:
            writer.writerow([
                date,
                round(cex_totals.get(date, 0), 2),
                round(dex_totals.get(date, 0), 2)
            ])

    print(f"✅ Cumulative chart saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
