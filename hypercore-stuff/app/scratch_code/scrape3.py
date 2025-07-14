import requests
import csv
from datetime import datetime

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}

def fetch_historical_orders(address):
    payload = {
        "type": "historicalOrders",
        "user": address
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("✅ Successfully fetched historical orders.")
        return data
    except Exception as e:
        print(f"❌ Error fetching historical orders: {e}")
        return []

def print_schema(data):
    if not data:
        print("No data returned.")
        return

    sample = data[0]
    print("\n📦 Response Schema:")
    for key in sample.keys():
        print(f"- {key}: {type(sample[key]).__name__}")
    for key in sample['order'].keys():
        print(f"- order.{key}: {type(sample['order'][key]).__name__}")

def save_to_csv(wallet_address, data):
    if not data:
        print("⚠️ No data to save.")
        return

    filename = f"{wallet_address}_historical_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    keys = [
        'coin', 'side', 'limitPx', 'sz', 'oid', 'timestamp',
        'triggerCondition', 'isTrigger', 'triggerPx', 'isPositionTpsl',
        'reduceOnly', 'orderType', 'origSz', 'tif', 'cloid',
        'status', 'statusTimestamp'
    ]

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()

        for entry in data:
            order = entry.get('order', {})
            writer.writerow({
                'coin': order.get('coin'),
                'side': order.get('side'),
                'limitPx': order.get('limitPx'),
                'sz': order.get('sz'),
                'oid': order.get('oid'),
                'timestamp': order.get('timestamp'),
                'triggerCondition': order.get('triggerCondition'),
                'isTrigger': order.get('isTrigger'),
                'triggerPx': order.get('triggerPx'),
                'isPositionTpsl': order.get('isPositionTpsl'),
                'reduceOnly': order.get('reduceOnly'),
                'orderType': order.get('orderType'),
                'origSz': order.get('origSz'),
                'tif': order.get('tif'),
                'cloid': order.get('cloid'),
                'status': entry.get('status'),
                'statusTimestamp': entry.get('statusTimestamp')
            })

    print(f"✅ Historical orders saved to {filename}")

if __name__ == "__main__":
    test_wallet = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45"
    result = fetch_historical_orders(test_wallet)

    if result:
        print_schema(result)
        save_to_csv(test_wallet, result)
    else:
        print("No historical orders returned.")
