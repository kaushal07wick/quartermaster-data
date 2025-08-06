import csv
import sys
import os
from datetime import datetime

def convert_unix_to_date(input_path, output_dir="converted_csv"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(input_path))

        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                if not row:
                    continue
                try:
                    unix_ts = int(row[0])
                    date_str = datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%d')
                    writer.writerow([date_str] + row[1:])
                except Exception as e:
                    print(f"⚠️ Skipping row {row}: {e}")

        print(f"✅ Converted CSV saved: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_unix_csv.py <path_to_csv>")
    else:
        convert_unix_to_date(sys.argv[1])
