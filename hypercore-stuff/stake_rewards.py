import requests
import time
import json
import os
import argparse

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}
CACHE_FILE = "staking_cache.json"


def fetch_data(payload, retries=5, backoff_factor=1.5):
    for i in range(retries):
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            if status == 429:
                wait = backoff_factor ** i
                print(f"⏳ Rate limited. Retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            else:
                print(f"❌ HTTP error: {e}")
                break

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

    return None


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read cache: {e}")
    return {}


def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to write cache: {e}")


def get_staking_info(wallet: str, refresh: bool = False) -> dict:
    wallet = wallet.lower()
    cache = load_cache()

    if not refresh and wallet in cache:
        return cache[wallet]

    try:
        summary = fetch_data({"type": "delegatorSummary", "user": wallet})
        time.sleep(0.1)
        rewards_data = fetch_data({"type": "delegatorRewards", "user": wallet})

        # Fallback if any fetch fails
        if not isinstance(summary, dict) or not isinstance(rewards_data, list):
            data = {"net_staked": 0.0, "delegation_rewards": 0.0}
        else:
            delegated = float(summary.get("delegated", 0.0))

            # Include pending withdrawals
            pending_withdrawals = sum(
                float(item.get("amount", 0.0)) for item in summary.get("pendingWithdrawals", [])
            )
            net_staked_including_pending = delegated + pending_withdrawals

            # Sum delegation rewards
            delegation_rewards_total = sum(
                float(r.get("totalAmount", 0.0)) for r in rewards_data if r.get("source") == "delegation"
            )

            data = {
                "net_staked": round(net_staked_including_pending, 6),
                "delegation_rewards": round(delegation_rewards_total, 6),
            }

        # Cache and return
        cache[wallet] = data
        save_cache(cache)
        return data

    except Exception as e:
        print(f"❌ Error fetching staking info for {wallet}: {e}")
        return {"net_staked": 0.0, "delegation_rewards": 0.0}


def main():
    parser = argparse.ArgumentParser(description="Fetch Hyperliquid staking summary and rewards.")
    parser.add_argument("wallet", type=str, help="Ethereum wallet address")
    parser.add_argument("--refresh-staking", action="store_true", help="Force refresh from API")
    args = parser.parse_args()

    result = get_staking_info(args.wallet, refresh=args.refresh_staking)
    print(f"📊 Net Staked: {result['net_staked']}")
    print(f"💰 Delegation Rewards: {result['delegation_rewards']}")


if __name__ == "__main__":
    main()
