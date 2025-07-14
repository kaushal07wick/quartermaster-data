import csv
import os
import re
import argparse
from collections import defaultdict
from stake_rewards import get_staking_info
from config import PRICES, WALLET_ALIAS_MAP, OUTPUT_CSV

PROCESSED_LOG = "processed_files.txt"
REVERSE_ALIAS_MAP = {alias.lower(): addr.lower() for addr, alias in WALLET_ALIAS_MAP.items()}


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def extract_wallet_address(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.search(r"(0x[a-fA-F0-9]{40})", base, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    hex_match = re.search(r"[a-fA-F0-9]{40}", base)
    return f"0x{hex_match.group(0).lower()}" if hex_match else ""


def alias(addr):
    return WALLET_ALIAS_MAP.get(addr.lower(), addr)


def load_wallet_transactions(path):
    data = {}
    for fname in os.listdir(path):
        if fname.endswith('.csv'):
            with open(os.path.join(path, fname), newline='') as f:
                data[fname] = list(csv.DictReader(f))
    return data


def get_processed_files(log_path, output_csv, fieldname="wallet_address"):
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    elif os.path.exists(output_csv):
        try:
            with open(output_csv, "r") as f:
                reader = csv.DictReader(f)
                return set(row[fieldname] for row in reader if row.get(fieldname))
        except Exception as e:
            print(f"⚠️ Failed to read processed info from CSV: {e}")
    return set()


def calculate_holdings(txs):
    holdings = defaultdict(float)
    for tx in txs:
        token = tx.get('token', '').upper()
        tx_type = tx.get('type', '').lower()
        amount = safe_float(tx.get('amount'))

        if tx_type in ["deposit", "genesis", "buy"]:
            holdings[token] += amount
        elif tx_type in ["withdraw", "send"]:
            holdings[token] -= amount
        # Other tx types can be handled as needed
    return holdings


def process_wallet(fname, txs, refresh_staking=False):
    addr = extract_wallet_address(fname)
    name = alias(addr)

    staking_data = get_staking_info(addr, refresh=refresh_staking)
    net_staked = safe_float(staking_data.get('net_staked', 0.0))
    rewards = safe_float(staking_data.get('delegation_rewards', 0.0))

    hype_price = PRICES.get('HYPE', 0)
    staked_usd = net_staked * hype_price
    rewards_usd = rewards  # Already in USD

    token_holdings = calculate_holdings(txs)

    # HYPE from buys is now included in holdings, exclude it from Spot calculation
    spot_tokens = {token: amount for token, amount in token_holdings.items() if token != 'HYPE'}
    spot_usd = sum(amount * PRICES.get(token, 0) for token, amount in spot_tokens.items())

    overview = round(staked_usd + rewards_usd + spot_usd, 2)

    return {
        "rank": None,
        "alias": name,
        "wallet_address": addr,
        "Overview": overview,
        "Perps": 0.00,
        "Spot": round(spot_usd, 2),
        "Vault": 0.00,
        "Staked": round(staked_usd, 2),
        "Rewards": round(rewards_usd, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Wallet data processor")
    parser.add_argument("folder", nargs="?", default="Master_Data", help="Folder containing CSV files")
    parser.add_argument("--reset", action="store_true", help="Reset processed log and output CSV")
    parser.add_argument("--force", action="store_true", help="Force processing of all files, ignoring logs")
    parser.add_argument("--refresh-staking", action="store_true", help="Force refresh of staking info from API")
    args = parser.parse_args()

    if args.reset:
        if os.path.exists(PROCESSED_LOG):
            print("🗑️ Resetting log...")
            os.remove(PROCESSED_LOG)
        if os.path.exists(OUTPUT_CSV):
            print("🗑️ Resetting CSV output...")
            os.remove(OUTPUT_CSV)

    processed_files = set() if args.force else get_processed_files(PROCESSED_LOG, OUTPUT_CSV)
    wallets = load_wallet_transactions(args.folder)
    seen = set()
    new_results = []
    new_files = []

    for fname, txs in wallets.items():
        if fname in processed_files:
            print(f"⏭️ Skipping already processed: {fname}")
            continue

        addr = extract_wallet_address(fname)
        if not addr or addr in seen:
            continue

        seen.add(addr)
        try:
            result = process_wallet(fname, txs, refresh_staking=args.refresh_staking)
            new_results.append(result)
            new_files.append(fname)
            print(f"✅ Processed: {fname}")
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")

    if not new_results:
        print("🚫 No new data processed.")
        return

    fieldnames = [
        "rank",
        "alias",
        "wallet_address",
        "Overview",
        "Perps",
        "Spot",
        "Vault",
        "Staked",
        "Rewards"
    ]

    all_results = []
    if os.path.exists(OUTPUT_CSV) and not args.reset:
        with open(OUTPUT_CSV, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['Overview'] = safe_float(row.get('Overview'))
                all_results.append(row)

    all_results.extend(new_results)
    all_results.sort(key=lambda x: x['Overview'], reverse=True)

    for i, row in enumerate(all_results, 1):
        row['rank'] = i

    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    with open(PROCESSED_LOG, 'a') as f:
        for fname in new_files:
            f.write(fname + '\n')

    print(f"📦 {len(new_results)} new wallet(s) processed. ✅ Output written to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
