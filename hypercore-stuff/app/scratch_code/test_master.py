import csv
import os
import re
from collections import defaultdict
from config import PRICES, WALLET_ALIAS_MAP, OUTPUT_CSV
from stake_rewards import get_staking_info  
import argparse

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def extract_wallet_address(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.search(r"(0x[a-fA-F0-9]{40})", base)
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

def process_wallet(fname, txs):
    addr = extract_wallet_address(fname)
    name = alias(addr)

    totals = defaultdict(float)  # Net token amounts (incoming - outgoing)

    for tx in txs:
        token = tx.get('token', '').upper()
        amount = safe_float(tx.get('amount'))
        from_addr = tx.get('from', '').strip().lower()
        to_addr = tx.get('to', '').strip().lower()
        tx_class = tx.get('class', '').strip().lower()


        if 'fail' in tx_class:
            continue

        if to_addr == addr:
            totals[token] += amount
        elif from_addr == addr:
            totals[token] -= amount

    staking_info = get_staking_info(addr)
    staked_amount = staking_info.get('net_staked', 0.0)
    rewards = staking_info.get('delegation_rewards', 0.0)

    hype_price = PRICES.get('HYPE', 1.0)

    net_hype = totals.get('HYPE', 0.0)
    net_usdc = totals.get('USDC', 0.0)

    total_aum = round((staked_amount + net_hype) * hype_price + rewards, 2)

    return {
        'Alias': name,
        'Wallet_address': addr,
        'StakedAmount': round(staked_amount, 2),
        'Rewards': round(rewards, 2),
        'Total AUM': total_aum,
        '$HYPE': round(net_hype, 2),
        '$USDC': round(net_usdc, 2),
    }

def main():
    parser = argparse.ArgumentParser(description="Minimal wallet processor with rank and staking integration")
    parser.add_argument("folder", nargs="?", default="Master_Data", help="Folder with CSVs")
    parser.add_argument("--reset", action="store_true", help="Reset output")
    args = parser.parse_args()

    if args.reset and os.path.exists(OUTPUT_CSV):
        print("🗑️ Resetting CSV output...")
        os.remove(OUTPUT_CSV)

    wallets = load_wallet_transactions(args.folder)
    results = []

    for fname, txs in wallets.items():
        try:
            results.append(process_wallet(fname, txs))
            print(f"✅ Processed: {fname}")
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")

    if not results:
        print("🚫 No wallets processed.")
        return

    # Sort and rank
    results.sort(key=lambda x: x['Total AUM'], reverse=True)
    for i, row in enumerate(results, 1):
        row['Rank'] = i

    fieldnames = ['Rank', 'Alias', 'Wallet_address', 'StakedAmount', 'Rewards', 'Total AUM', '$HYPE', '$USDC']
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"🏅 Ranked output written to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
