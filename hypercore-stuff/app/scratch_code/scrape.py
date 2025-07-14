import requests
import csv
from datetime import datetime

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}

def fetch_open_orders(address):
    payload = {
        "type": "userFills",
        "user": address,
        "aggregateByTime": True
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("✅ Successfully fetched open orders.")
        return data
    except Exception as e:
        print(f"❌ Error fetching open orders: {e}")
        return []

def print_schema(data):
    if not data:
        print("No data returned.")
        return

    print("\n📦 Response Schema:")
    sample = data[0]
    for key in sample.keys():
        print(f"- {key}: {type(sample[key]).__name__}")

def save_to_csv(wallet_address, data):
    if not data:
        print("⚠️ No data to save.")
        return

    filename = f"{wallet_address}_open_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    keys = list(data[0].keys())  # Dynamically use all keys from the response

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()

        for row in data[:5]:  # Save top 5 only
            writer.writerow(row)

    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    test_wallet = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45"
    result = fetch_open_orders(test_wallet)

    if result:
        print_schema(result)
        save_to_csv(test_wallet, result)
        print("\n📊 Top 5 open orders:")
        for order in result[:5]:
            print(order)
    else:
        print("No open orders found.")
