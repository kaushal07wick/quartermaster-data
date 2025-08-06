import os
import csv
from datetime import datetime

def convert_unix_to_date(timestamp):
    try:
        # Convert UNIX timestamp (assumed to be in seconds) to YYYY-MM-DD
        return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
    except:
        return timestamp  # if conversion fails (e.g., empty cell), return original

def convert_dates_in_csv(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            full_path = os.path.join(folder_path, filename)

            with open(full_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                rows = list(reader)
                fieldnames = reader.fieldnames

            if 'date' not in fieldnames:
                continue  # skip files without a 'date' column

            for row in rows:
                if row.get('date'):
                    row['date'] = convert_unix_to_date(row['date'])

            # Overwrite the original file
            with open(full_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"✅ Updated: {filename}")

# Run script
if __name__ == "__main__":
    convert_dates_in_csv("csv_output")
