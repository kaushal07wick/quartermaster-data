import requests
import csv
from datetime import datetime

url = "https://api.hybridge.xyz/charts.getData"
payload = {"timeframe": "all"}

try:
    response = requests.post(url, json=payload)
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        labels = data.get("labels", [])
        accumulated_user_hl = data.get("accumulatedTransferredUserHL", [])

        if not labels or not accumulated_user_hl:
            print("Received empty data.")
        else:
            # Prepare rows: convert time strings to full datetime format
            rows = zip(labels, accumulated_user_hl)
            output_file = "hybridge_data.csv"

            with open(output_file, mode="w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["timestamp", "accumulated_user_HL"])
                writer.writerows(rows)

            print(f"✅ CSV saved to: {output_file}")
    else:
        print("Failed to retrieve data.")
        print(response.text)

except Exception as e:
    print(f"Error occurred: {e}")
