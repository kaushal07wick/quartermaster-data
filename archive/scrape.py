import requests
import json
import csv
from datetime import datetime

url = "https://api.hyperliquid.xyz/info"
user_address = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45"

payload = {
    "type": "userNonFundingLedgerUpdates",
    "user": user_address
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()

    # Save raw response to JSON file
    with open('ledger_updates.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("Saved response to ledger_updates.json")

    # Prepare CSV data
    csv_data = []
    for entry in data:
        delta = entry['delta']

        # Extract common fields
        row = {
            'timestamp': datetime.fromtimestamp(entry['time'] / 1000).isoformat(),
            'hash': entry['hash'],
            'type': delta.get('type', ''),
            'token': delta.get('token', ''),
            'amount': delta.get('amount', ''),
            'isDeposit': delta.get('isDeposit', ''),
            'usdcValue': delta.get('usdcValue', ''),
            'user': delta.get('user', ''),
            'destination': delta.get('destination', ''),
            'fee': delta.get('fee', ''),
            'nativeTokenFee': delta.get('nativeTokenFee', ''),
            'nonce': delta.get('nonce', '')
        }
        csv_data.append(row)

    # Write to CSV file
    with open('ledger_updates.csv', 'w', newline='') as csv_file:
        fieldnames = ['timestamp', 'hash', 'type', 'token', 'amount', 'isDeposit', 'usdcValue', 'user', 'destination', 'fee', 'nativeTokenFee', 'nonce']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)

    print("Saved formatted data to ledger_updates.csv")

else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)

