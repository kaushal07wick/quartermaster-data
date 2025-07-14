import requests
import json
from datetime import datetime, timedelta

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}

def fetch_user_ledger(user_address, query_type="userFunding", start_time=None, end_time=None):
    if query_type not in ["userFunding", "userNonFundingLedgerUpdates"]:
        raise ValueError("query_type must be 'userFunding' or 'userNonFundingLedgerUpdates'")

    # If start_time not provided, default to 30 days ago
    if not start_time:
        start_time = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)
    if not end_time:
        end_time = int(datetime.utcnow().timestamp() * 1000)

    payload = {
        "type": query_type,
        "user": user_address,
        "startTime": start_time,
        "endTime": end_time
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Successfully fetched {query_type} data.")
        return data
    except Exception as e:
        print(f"❌ Error fetching {query_type} data: {e}")
        return []

def save_to_json(data, user_address, query_type):
    filename = f"{user_address}_{query_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    wallet_address = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45"

    # Fetch funding history
    funding_data = fetch_user_ledger(wallet_address, query_type="userFunding")
    if funding_data:
        save_to_json(funding_data, wallet_address, "userFunding")
        print(json.dumps(funding_data, indent=4))
    else:
        print("No funding data returned.")

    # Fetch non-funding ledger updates
    non_funding_data = fetch_user_ledger(wallet_address, query_type="userNonFundingLedgerUpdates")
    if non_funding_data:
        save_to_json(non_funding_data, wallet_address, "userNonFundingLedgerUpdates")
        print(json.dumps(non_funding_data, indent=4))
    else:
        print("No non-funding ledger data returned.")
