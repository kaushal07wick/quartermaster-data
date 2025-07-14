import requests
import csv
import time

def fetch_all_user_transactions(address):
    url = "https://rpc.hyperliquid.xyz/explorer"
    all_transactions = []
    cursor = None

    while True:
        payload = {
            "type": "userDetails",
            "user": address
        }
        if cursor:
            payload["cursor"] = cursor

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Skip transactions of type 'evmRawTx'
            transactions = [
                tx for tx in data.get('txs', [])
                if tx.get('action', {}).get('type') != 'evmRawTx'
            ]
            all_transactions.extend(transactions)

            cursor = data.get('cursor')
            if not cursor:
                break

            time.sleep(0.2)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching user details: {e}")
            break

    print(f"✅ Collected {len(all_transactions)} transactions")
    return all_transactions


def flatten_transaction(tx):
    action = tx.get("action", {})
    return {
        "time": tx.get("time"),
        "user": tx.get("user"),
        "type": action.get("type"),
        "token": action.get("token"),
        "amount": action.get("amount"),
        "destination": action.get("destination"),
        "signatureChainId": action.get("signatureChainId"),
        "hyperliquidChain": action.get("hyperliquidChain"),
        "block": tx.get("block"),
        "hash": tx.get("hash"),
        "error": tx.get("error")
    }


def write_csv(transactions, address):
    csv_file = f"{address}_hyperliquid_transactions.csv"
    fieldnames = [
        "time", "user", "type", "token", "amount", "destination",
        "signatureChainId", "hyperliquidChain", "block", "hash", "error"
    ]

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tx in transactions:
            writer.writerow(flatten_transaction(tx))

    print(f"📁 Saved to {csv_file}")


if __name__ == "__main__":
    wallet_address = "0x716bd8d3337972db99995dda5c4b34d954a61d95"
    txs = fetch_all_user_transactions(wallet_address)
    write_csv(txs, wallet_address)
