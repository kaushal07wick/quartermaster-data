import csv
import os
import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from stake_rewards import get_staking_info
from config import PRICES, MEMECOINS, WALLET_ALIAS_MAP, OUTPUT_CSV
import argparse

PROCESSED_LOG = "processed_files.txt"
REVERSE_ALIAS_MAP = {alias.lower(): addr.lower() for addr, alias in WALLET_ALIAS_MAP.items()}
HLP_ADDR = REVERSE_ALIAS_MAP.get('hlp')
HYPEREVM_ADDR = REVERSE_ALIAS_MAP.get('hyperevm')
HIP2_ADDR = REVERSE_ALIAS_MAP.get('hip-2') or REVERSE_ALIAS_MAP.get('hip2')

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

def calc_txn_freq(timestamps):
    if len(timestamps) < 2:
        return "N/A"
    timestamps.sort()
    intervals = [(t2 - t1).total_seconds() for t1, t2 in zip(timestamps, timestamps[1:])]
    avg = sum(intervals) / len(intervals)
    if avg < 60:
        return f"Every {int(avg)} sec"
    if avg < 3600:
        return f"{round(avg / 60)}x/hour"
    if avg < 86400:
        return f"{round(avg / 3600)}x/day"
    return f"{round(avg / 86400)}x/week"

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

    staking = get_staking_info(addr)
    net_staked = staking.get('net_staked', 0.0)
    rewards = staking.get('delegation_rewards', 0.0)

    totals = defaultdict(float)
    inflow = outflow = max_tx = fee_total = 0.0
    times = []
    category_times = {
        'hlp': [], 'hyperevm': [], 'hip2': [],
        'withdraw_arb': [], 'deposit_arb': []
    }

    for tx in txs:
        usd = safe_float(tx.get('USDAmount'))
        amount = safe_float(tx.get('amount'))
        token = tx.get('token', '').upper()
        ts = datetime.fromtimestamp(int(tx.get('time', 0)) / 1000)
        times.append(ts)

        if amount > 0:
            inflow += usd
        else:
            outflow += abs(usd)
        max_tx = max(max_tx, abs(usd))
        fee_total += safe_float(tx.get('fee'))
        totals[token] += abs(usd)

        to_addr = tx.get('to', '').lower()
        from_addr = tx.get('from', '').lower()
        role = tx.get('class', '').upper()

        if HLP_ADDR and to_addr == HLP_ADDR:
            category_times['hlp'].append(ts)
        if HYPEREVM_ADDR and to_addr == HYPEREVM_ADDR:
            category_times['hyperevm'].append(ts)
        if HIP2_ADDR and to_addr == HIP2_ADDR:
            category_times['hip2'].append(ts)
        if role == 'WITHDRAW' and 'arbitrum' in to_addr:
            category_times['withdraw_arb'].append(ts)
        if role == 'DEPOSIT' and 'arbitrum' in from_addr:
            category_times['deposit_arb'].append(ts)

    total_tx = len(txs)
    avg_tx_val = round((sum(totals.values()) / total_tx) if total_tx else 0.0, 2)
    total_aum = round(
        sum(
            safe_float(totals.get(token, 0)) * PRICES.get(token, 1)
            for token in totals
        )
        + net_staked * PRICES.get('HYPE', 0)
        + rewards,
        2
    )
    top_token = max(totals, key=totals.get, default='N/A')
    staking_pct = round((net_staked * PRICES.get('HYPE', 0)) / total_aum * 100, 2) if total_aum else 0.0
    meme_qty = sum(safe_float(tx.get('amount')) for tx in txs if tx.get('token', '').upper() in MEMECOINS)
    meme_pct = round(meme_qty * PRICES.get('HYPE', 0) / total_aum * 100, 2) if total_aum else 0.0

    outflows = Counter()
    for tx in txs:
        if tx.get('to', '').lower() != addr:
            outflows[tx['to'].lower()] += abs(safe_float(tx.get('USDAmount')))
    top_out = [alias(w) for w, _ in outflows.most_common(5)]

    return {
        'Alias': name,
        'Wallet_address': addr,
        'Total AUM': total_aum,
        '$HYPE': round(totals.get('HYPE', 0), 2),
        '$USDC': round(totals.get('USDC', 0), 2),
        'Memecoins': round(meme_qty, 2),
        '$HYPE Staked': round(net_staked, 2),
        '$HYPE Staked/Total AUM (%)': staking_pct,
        'Memes/Total AUM (%)': meme_pct,
        'Txn Frequency': calc_txn_freq(times),
        'HLP Frequency': calc_txn_freq(category_times['hlp']),
        'HyperEVM Frequency': calc_txn_freq(category_times['hyperevm']),
        'HIP-2 Frequency': calc_txn_freq(category_times['hip2']),
        'General Capital Flow': 'Positive' if inflow > outflow else 'Negative' if outflow > inflow else 'Neutral',
        'Max Value Transferred in 1 Txn ($)': round(max_tx, 2),
        'Total Inflow Volume': round(inflow, 2),
        'Total Outflow Volume': round(outflow, 2),
        'Average Transaction Volume (in $)': avg_tx_val,
        'Token with the most amount of USD value transfer': top_token,
        'Evidence of Staking/Liquidity Cycles': 'Yes' if staking_pct > 0 else 'Not clear',
        'Total Fee Spend ($)': round(fee_total, 2),
        'Top 1st Outflow Wallet': top_out[0] if len(top_out) > 0 else 'N/A',
        'Top 2nd Outflow Wallet': top_out[1] if len(top_out) > 1 else 'N/A',
        'Top 3rd Outflow Wallet': top_out[2] if len(top_out) > 2 else 'N/A',
        'Top 4th Outflow Wallet': top_out[3] if len(top_out) > 3 else 'N/A',
        'Top 5th Outflow Wallet': top_out[4] if len(top_out) > 4 else 'N/A',
        'Staking Rewards': round(rewards, 2),
        'Arbitrum Withdrawals': calc_txn_freq(category_times['withdraw_arb']),
        'Arbitrum Deposits': calc_txn_freq(category_times['deposit_arb']),
    }

def main():
    parser = argparse.ArgumentParser(description="Wallet data processor")
    parser.add_argument("folder", nargs="?", default="Master_Data", help="Folder containing CSV files")
    parser.add_argument("--reset", action="store_true", help="Reset processed log and output CSV")
    parser.add_argument("--force", action="store_true", help="Force processing of all files, ignoring logs")
    args = parser.parse_args()

    if args.reset and os.path.exists(PROCESSED_LOG):
        print("🗑️ Resetting log...")
        os.remove(PROCESSED_LOG)

    if args.reset and os.path.exists(OUTPUT_CSV):
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
            new_results.append(process_wallet(fname, txs))
            new_files.append(fname)
            print(f"✅ Processed: {fname}")
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")

    if not new_results:
        print("🚫 No new data processed.")
        return

    fieldnames = [
        'Rank', 'Alias', 'Wallet_address', 'Total AUM', '$HYPE', '$USDC', 'Memecoins',
        '$HYPE Staked', '$HYPE Staked/Total AUM (%)', 'Memes/Total AUM (%)', 'Txn Frequency',
        'HLP Frequency', 'HyperEVM Frequency', 'HIP-2 Frequency',
        'General Capital Flow', 'Max Value Transferred in 1 Txn ($)', 'Total Inflow Volume',
        'Total Outflow Volume', 'Average Transaction Volume (in $)',
        'Token with the most amount of USD value transfer', 'Evidence of Staking/Liquidity Cycles',
        'Total Fee Spend ($)', 'Top 1st Outflow Wallet', 'Top 2nd Outflow Wallet',
        'Top 3rd Outflow Wallet', 'Top 4th Outflow Wallet', 'Top 5th Outflow Wallet',
        'Staking Rewards', 'Arbitrum Withdrawals', 'Arbitrum Deposits',
    ]

    # Load old results if not reset
    all_results = []
    if os.path.exists(OUTPUT_CSV) and not args.reset:
        with open(OUTPUT_CSV, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['Total AUM'] = safe_float(row.get('Total AUM'))
                all_results.append(row)

    all_results.extend(new_results)

    # Sort all by Total AUM and re-assign ranks
    all_results.sort(key=lambda x: x['Total AUM'], reverse=True)
    for i, row in enumerate(all_results, 1):
        row['Rank'] = i

    # Overwrite full CSV with re-ranked data
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    # Update processed log
    with open(PROCESSED_LOG, 'a') as f:
        for fname in new_files:
            f.write(fname + '\n')

    print(f"📦 {len(new_results)} new wallet(s) processed. ✅ Output written to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
