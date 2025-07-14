# phase1.py

import csv
import time
import argparse
import os

from balance import get_token_balances, read_wallets
from stake_rewards import get_staking_info
from perp_balance import get_perp_usd_value
from config import OUTPUT_CSV, MAIN_TOKENS, MEMECOIN_PRICES, WALLET_ALIAS_MAP


def reset_cache_files():
    cache_files = [
        "balance_cache.json",                  # balance.py
        "staking_cache.json",                  # stake_rewards.py
        "perp_balances.json"             # perp_balance.py
    ]
    for path in cache_files:
        try:
            os.remove(path)
            print(f"🧹 Removed {path}")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Error removing {path}: {e}")


def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0


# Combine token and meme prices
PRICES = {**MAIN_TOKENS, **MEMECOIN_PRICES}
MEMECOINS = set(MEMECOIN_PRICES.keys())


def process_wallet(wallet, refresh_balances=False):
    balances = get_token_balances(wallet, refresh=refresh_balances)
    token_map = {b.get("coin", "").upper(): safe_float(b.get("total", 0)) for b in balances}

    token_usd_values = {
        coin: amt * PRICES.get(coin, 0.0)
        for coin, amt in token_map.items()
    }

    hype_balance = token_map.get("HYPE", 0.0) * PRICES.get('HYPE', 0)
    usdc_balance = token_map.get("USDC", 0.0) * PRICES.get('USDC', 0)
    meme_value = sum(token_usd_values.get(c, 0.0) for c in MEMECOINS)

    stake_info = get_staking_info(wallet, refresh=refresh_balances)
    staked_hype = safe_float(stake_info.get("net_staked", 0.0))
    staked_value_usd = staked_hype * PRICES.get("HYPE", 0.0)
    rewards_usd = safe_float(stake_info.get("delegation_rewards", 0.0))

    perp_value_usd = get_perp_usd_value(wallet, refresh=refresh_balances)

    total_aum = sum(token_usd_values.values()) + staked_value_usd + rewards_usd + perp_value_usd

    return {
        "Wallet_address": wallet,
        "$HYPE": round(hype_balance, 4),
        "$USDC": round(usdc_balance, 4),
        "$HYPE Staked": round(staked_value_usd, 2),
        "Staking Rewards": round(rewards_usd, 2),
        "Total AUM": round(total_aum, 2),
        "$HYPE Staked/Total AUM (%)": round((staked_value_usd / total_aum * 100) if total_aum else 0.0, 2),
        "Memecoins": round(meme_value, 2),
        "Memes/Total AUM (%)": round((meme_value / total_aum * 100) if total_aum else 0.0, 2)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Force refresh of API data")
    parser.add_argument("--reset", action="store_true", help="Delete all local cache files")
    args = parser.parse_args()

    if args.reset:
        print("♻️  Resetting all caches...")
        reset_cache_files()

    wallets = read_wallets("wallets.txt")
    results = []

    print(f"📊 Processing {len(wallets)} wallets...\n")

    for i, wallet in enumerate(wallets, 1):
        print(f"🔍 [{i}/{len(wallets)}] {wallet}")
        try:
            row = process_wallet(wallet, refresh_balances=args.refresh)
            results.append(row)
        except Exception as e:
            print(f"⚠️ Error processing {wallet}: {e}")
        time.sleep(0.2)

    # Sort by Total AUM descending
    results.sort(key=lambda x: x["Total AUM"], reverse=True)

    for i, row in enumerate(results, 1):
        row["Rank"] = i
        row["Alias"] = WALLET_ALIAS_MAP.get(row["Wallet_address"].lower(), "")

    fieldnames = [
        "Rank",
        "Alias",
        "Wallet_address",
        "Total AUM",
        "$HYPE",
        "$USDC",
        "Memecoins",
        "$HYPE Staked",
        "$HYPE Staked/Total AUM (%)",
        "Memes/Total AUM (%)",
        "Staking Rewards"
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done. Saved summary to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
