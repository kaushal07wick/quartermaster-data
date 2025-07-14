import requests
import csv
import json
from datetime import datetime

# Load aliases
with open('globalAliases.json', 'r') as f:
    aliases = json.load(f)

def clean_token(token):
    """Remove unique ID from token like 'HYPE:0xabc123'."""
    return token.split(':')[0] if ':' in token else token

def format_time(timestamp_ms):
    """Convert timestamp to human-readable format."""
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

def fetch_user_details(address):
    url = "https://rpc.hyperliquid.xyz/explorer"
    payload = {"type": "userDetails", "user": address}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Successfully fetched userDetails for {address}")
        return data
    except Exception as e:
        print(f"❌ Error fetching userDetails for {address}: {e}")
        return {}

def filter_actions(actions):
    filtered = []
    for action in actions:
        action_type = action.get("action", {}).get("type")
        if action_type in ["spotSend", "cWithdraw", "order", "deposit"]:
            filtered.append(action)
    return filtered

def extract_action_fields(action, wallet_address):
    action_data = action.get("action", {})
    action_type = action_data.get("type")

    to_address = ""
    amount = ""
    token = ""

    if action_type == "spotSend":
        to_address = action_data.get("destination", "")
        amount = action_data.get("amount", "")
        token = clean_token(action_data.get("token", ""))

    elif action_type == "cWithdraw":
        amount = str(action_data.get("wei", ""))
        to_address = " "

    elif action_type == "order":
        order_details = action_data.get("orders", [])[0] if action_data.get("orders") else {}
        side = "Buy" if order_details.get("b", True) else "Sell"
        price = order_details.get("p", "")
        size = order_details.get("s", "")
        token = f"Price: {price} Size: {size} Side: {side}"
        amount = ""
        to_address = "Market"

    elif action_type == "deposit":
        amount = str(action_data.get("wei", ""))
        to_address = "Self"
        token = clean_token(action_data.get("token", ""))

    if to_address.lower() == wallet_address.lower():
        to_address = "Self"

    if to_address in aliases:
        to_address = aliases[to_address]

    return to_address, amount, token

def save_to_csv(all_actions, filename):
    if not all_actions:
        print("❌ No actions to save.")
        return

    with open(filename, mode='w', newline='') as file:
        fieldnames = ["time", "action_type", "from", "to", "token", "amount", "hash"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for action in all_actions:
            writer.writerow(action)

    print(f"✅ Saved {len(all_actions)} total actions to {filename}")

if __name__ == "__main__":
    with open('wallets.txt', 'r') as f:
        wallet_addresses = [line.strip() for line in f if line.strip()]

    all_actions = []

    for wallet_address in wallet_addresses:
        print(f"\n🔍 Processing wallet: {wallet_address}")
        result = fetch_user_details(wallet_address)
        actions = filter_actions(result.get("txs", []))

        if not actions:
            print(f"❌ No actions found for {wallet_address}")
            continue

        for action in actions:
            to_address, amount, token = extract_action_fields(action, wallet_address)
            action_entry = {
                "time": format_time(action.get("time")),
                "action_type": action.get("action", {}).get("type"),
                "from": action.get("user"),
                "to": to_address,
                "token": token,
                "amount": amount,
                "hash": action.get("hash")
            }
            all_actions.append(action_entry)

    save_to_csv(all_actions, "filtered_wallet_data.csv")
