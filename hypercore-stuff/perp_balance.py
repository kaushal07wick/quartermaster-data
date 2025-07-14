# perp_balance.py

import requests
import json
import os
import time

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}
CACHE_FILE = "cache/perp_balances.json"
CACHE_TTL = 300  # seconds (5 minutes)

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        CACHE = json.load(f)
else:
    CACHE = {}

def save_cache():
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(CACHE, f)

def get_perp_usd_value(wallet: str, refresh: bool = False) -> float:
    now = time.time()

    # Check cache
    if not refresh:
        entry = CACHE.get(wallet)
        if entry and (now - entry["timestamp"] < CACHE_TTL):
            return entry["value"]

    # Fetch fresh value
    payload = {
        "type": "clearinghouseState",
        "user": wallet
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        account_value = float(data.get("marginSummary", {}).get("accountValue", 0.0))

        # Save to cache
        CACHE[wallet] = {"value": account_value, "timestamp": now}
        save_cache()

        return account_value

    except Exception as e:
        print(f"❌ Error fetching perps for {wallet}: {e}")
        return 0.0
