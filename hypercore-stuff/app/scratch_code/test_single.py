import requests
import csv
import argparse
import os

# RPC endpoint
HYPERLIQUID_RPC_URL = "https://rpc.hyperliquid.xyz/explorer"

# Output CSV
OUTPUT_CSV = "hyperliquid_wallet_data.csv"

def fetch_wallet_data(wallet_address):
    payload = {
        "method": "getUserState",
        "params": {
            "user": wallet_address
        }
    }

    try:
        response = requests.post(HYPERLIQUID_RPC_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {})
    except Exception as e:
        print(f"❌ Failed to fetch data for {wallet_address}: {e}")
        return {}

def save_to_csv(data, wallet_address, filename=OUTPUT_CSV):
    if not data:
        print("🚫 No data to write.")
        return

    # Flatten relevant values
    balances = data.get("assetPositions", [])
    if not balances:
        print("ℹ️ No asset positions found.")
        return

    fieldnames = ["wallet", "coin", "position", "entry_price", "realized_pnl", "unrealized_pnl"]
    rows = []

    for item in balances:
        coin = item.get("coin")
        position = item.get("position", 0)
        entry_price = item.get("entryPx", 0)
        realized_pnl = item.get("realizedPnl", 0)
        unrealized_pnl = item.get("unrealizedPnl", 0)

        rows.append({
            "wallet": wallet_address,
            "coin": coin,
            "position": position,
            "entry_price": entry_price,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl
        })

    write_header = not os.path.exists(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Data written to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Fetch wallet data from Hyperliquid RPC API")
    parser.add_argument("wallet", help="Wallet address (e.g., 0xabc123...)")
    parser.add_argument("--out", default=OUTPUT_CSV, help="Output CSV file")
    args = parser.parse_args()

    print(f"🔍 Fetching data for: {args.wallet}")
    data = fetch_wallet_data(args.wallet)
    save_to_csv(data, args.wallet, args.out)

if __name__ == "__main__":
    main()
