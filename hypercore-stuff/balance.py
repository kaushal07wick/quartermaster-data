# balance.py

import requests
import json
import os

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}
CACHE_FILE = "balance_cache.json"

# Global cache for efficiency
cache = None

def read_wallets(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip().startswith("0x") and len(line.strip()) == 42]

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read balance cache: {e}")
    return {}

def save_cache(cache_data):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to write balance cache: {e}")

def fetch_balances(wallet_address):
    payload = {
        "type": "spotClearinghouseState",
        "user": wallet_address
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json().get("balances", [])
    except Exception as e:
        print(f"⚠️ Error fetching data for {wallet_address}: {e}")
        return []

def init_cache():
    global cache
    if cache is None:
        cache = load_cache()

def get_token_balances(wallet_address, refresh=False):
    global cache
    init_cache()

    wallet_address = wallet_address.lower()
    if not refresh and wallet_address in cache:
        return cache[wallet_address]

    balances = fetch_balances(wallet_address)
    cache[wallet_address] = balances
    save_cache(cache)
    return balances
