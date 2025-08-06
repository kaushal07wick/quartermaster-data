import requests
import json
import csv
from datetime import datetime

# CoinGecko API URL for liqdlaunch
url = "https://api.coingecko.com/api/v3/coins/felix-feusd"

def fetch_token_data():
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_important_fields(data):
    md = data.get("market_data", {})

    # Find LIQD/USDC ticker
    bid_ask_spread_pct = None
    for ticker in data.get("tickers", []):
        if ticker.get("base") == "FEUSD" and ticker.get("target") == "USDC":
            bid_ask_spread_pct = ticker.get("bid_ask_spread_percentage")
            break

    # Build a dict of relevant fields
    extracted = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "price_usd": md.get("current_price", {}).get("usd"),
        "volume_usd": md.get("total_volume", {}).get("usd"),
        "total_volume_usd": md.get("total_volume", {}).get("usd"),
        "fully_diluted_valuation_usd": md.get("fully_diluted_valuation", {}).get("usd"),
        "market_cap_change_24h": md.get("market_cap_change_24h"),
        "price_change_24h": md.get("price_change_24h"),
        "circulating_supply": md.get("circulating_supply"),
        "total_supply": md.get("total_supply"),
        "max_supply": md.get("max_supply"),
        "bid_ask_spread_pct_usdc": bid_ask_spread_pct
    }

    return extracted

def save_to_json(data, filename="liqdlaunch_metrics.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def save_to_csv(data, filename="feusd.csv"):
    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    try:
        raw_data = fetch_token_data()
        important_data = extract_important_fields(raw_data)

        # Save to both JSON and CSV
        save_to_json(important_data)
        save_to_csv(important_data)

        print("✅ Data saved successfully:")
        print(json.dumps(important_data, indent=2))

    except Exception as e:
        print(f"❌ Error fetching or saving data: {e}")
