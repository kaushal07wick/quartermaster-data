import os
import json
import argparse
import logging
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Wallets missing USDAmount, compute using amount × token price
WALLETS_MISSING_USD = {
    "0xe06a3c8d7eedc8c907a0bba434804288a6f7cd24",
    "0xee5c571813227fe7bbeef6fdd9f3e0592aca4799",
    "0x89453000afe81a8843ae2d1c5df0f340f8800779",
    "0xa23190045c4aebeb724844ce622465475e539bae",
    "0x7be1cba648ebe1ab8084244d23f28d68a86480d8",
    "0xa87a233e8a7d8951ff790a2e39738086cb5f71b7"
}

# --- Config ---
DATA_DIR = "Master_Data"
CACHE_FILE = "wallet_analysis_cache.json"
OUTPUT_FILE = "100_transactional_summary.csv"

# --- Import Price and Token Data ---
try:
    from config import MAIN_TOKENS, MEMECOIN_PRICES
except ImportError:
    logging.error("❌ Could not import MAIN_TOKENS or MEMECOIN_PRICES from config.py")
    MAIN_TOKENS, MEMECOIN_PRICES = {}, {}

# --- Load Aliases ---
ALIASES = {}
if os.path.exists("globalAliases.json"):
    with open("globalAliases.json") as f:
        ALIASES = json.load(f)

# --- Utilities ---
def get_alias(address):
    return ALIASES.get(address.lower(), address)

def parse_wallet_from_filename(filename):
    return filename.split("_")[0].lower()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def make_json_serializable(obj):
    if isinstance(obj, (np.integer, np.int64)): return int(obj)
    if isinstance(obj, (np.floating, np.float64)): return float(obj)
    if isinstance(obj, (np.ndarray, list, tuple)):
        return [make_json_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    return obj

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(make_json_serializable(data), f, indent=2)

def clean_and_load(filepath):
    df = pd.read_csv(filepath)
    df.drop_duplicates(inplace=True)
    return df

# --- Core Analysis ---
def analyze_wallet(file_path, df):
    wallet_address = parse_wallet_from_filename(os.path.basename(file_path)).lower()

    df["from"] = df["from"].astype(str).str.lower()
    df["to"] = df["to"].astype(str).str.lower()

    if "token" not in df.columns:
        df["token"] = ""
    df["token"] = df["token"].astype(str).str.upper()

    # --- Handle missing USDAmount ---
    if wallet_address in WALLETS_MISSING_USD and "USDAmount" not in df.columns and "amount" in df.columns:
        logging.warning(f"🔄 Estimating USDAmount for {wallet_address} using token price * amount.")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["USDAmount"] = df.apply(
            lambda row: row["amount"] * MEMECOIN_PRICES.get(row["token"], 0),
            axis=1
        )
    else:
        if "USDAmount" not in df.columns:
            logging.warning(f"⚠️ No USDAmount or amount column in {wallet_address}, skipping.")
            return None

    df = df.dropna(subset=["USDAmount"])
    df["usd_value"] = pd.to_numeric(df["USDAmount"], errors="coerce").fillna(0.0)

    inflow_df = df[(df["to"] == wallet_address) & (df["from"] != wallet_address)]
    outflow_df = df[(df["from"] == wallet_address) & (df["to"] != wallet_address)]

    inflow_volume = inflow_df["usd_value"].sum()
    outflow_volume = outflow_df["usd_value"].sum()

    capital_flow = "Positive" if inflow_volume > outflow_volume else "Negative"
    max_txn_value = df["usd_value"].max()
    avg_txn = df["usd_value"].mean()

    token_totals = df.groupby("token")["usd_value"].sum()
    top_token = token_totals.idxmax() if not token_totals.empty else "N/A"

    fee_col = pd.to_numeric(df.get("fee", pd.Series([0] * len(df))), errors="coerce").fillna(0.0)
    total_fee = fee_col.sum()

    outflows_only = outflow_df[outflow_df["to"] != wallet_address]
    top_outflows = outflows_only["to"].value_counts().head(5)
    top_outflows_named = [get_alias(addr) for addr in top_outflows.index]

    arb_withdraw_freq = df["to"].str.contains("arbitrum", case=False, na=False).sum()
    arb_deposit_freq = df["from"].str.contains("arbitrum", case=False, na=False).sum()
    hyperevm_freq = df["to"].str.contains("hyperevm", case=False, na=False).sum()
    hlp_freq = df["to"].str.contains("hlp", case=False, na=False).sum()
    hip2_freq = df["to"].str.contains("hip-2", case=False, na=False).sum()

    return {
        "Wallet": wallet_address,
        "Txn Frequency": int(len(df)),
        "General Capital Flow": capital_flow,
        "Max Value Transferred in 1 txn ($)": round(max_txn_value, 6),
        "Total Inflow Volume": round(inflow_volume, 6),
        "Total Outflow Volume": round(outflow_volume, 6),
        "Average Transaction Volume (in $)": round(avg_txn, 6),
        "Token with the most amount of USD value transfer": top_token,
        "Total Fee Spend ($)": round(total_fee, 6),
        "Top 1st Outflow Wallet": top_outflows_named[0] if len(top_outflows_named) > 0 else "N/A",
        "Top 2nd Outflow Wallet": top_outflows_named[1] if len(top_outflows_named) > 1 else "N/A",
        "Top 3rd Outflow Wallet": top_outflows_named[2] if len(top_outflows_named) > 2 else "N/A",
        "Top 4th Outflow Wallet": top_outflows_named[3] if len(top_outflows_named) > 3 else "N/A",
        "Top 5th Outflow Wallet": top_outflows_named[4] if len(top_outflows_named) > 4 else "N/A",
        "Withdrawals to Arbitrum Frequency": int(arb_withdraw_freq),
        "Deposits from Arbitrum Frequency": int(arb_deposit_freq),
        "Frequency Hyperevm": int(hyperevm_freq),
        "Frequency HLP": int(hlp_freq),
        "Frequency HIP-2": int(hip2_freq),
    }

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Force refresh for all wallets")
    parser.add_argument("--reset", action="store_true", help="Clear cache before running")
    args = parser.parse_args()

    if args.reset and os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        logging.info("🧹 Cache reset complete.")

    cache = {} if args.reset else load_cache()
    results = []
    unprocessed = []

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") and f.startswith("0x")]

    seen_wallets = set()
    unique_files = []
    for f in files:
        wallet = parse_wallet_from_filename(f)
        if wallet not in seen_wallets:
            unique_files.append(f)
            seen_wallets.add(wallet)
        else:
            logging.warning(f"⚠️ Duplicate wallet file skipped: {wallet}")
    files = unique_files

    for i, filename in enumerate(files, 1):
        wallet = parse_wallet_from_filename(filename)
        path = os.path.join(DATA_DIR, filename)

        logging.info(f"[{i}/{len(files)}] 🔍 Processing: {wallet}")

        if not args.refresh and wallet in cache:
            logging.info(f"[{i}/{len(files)}] ✅ Cached: {wallet}")
            results.append(cache[wallet])
            continue

        try:
            df = clean_and_load(path)
            if len(df) == 0:
                logging.warning(f"⚠️ Skipping empty file: {filename}")
                continue
            summary = analyze_wallet(path, df)
            if summary:
                cache[wallet] = summary
                results.append(summary)
        except Exception as e:
            logging.error(f"❌ Error processing {wallet}: {e}")
            unprocessed.append(wallet)

    save_cache(cache)

    if results:
        try:
            rank_df = pd.read_csv("HYPE_rank.csv")
            rank_df["address"] = rank_df["address"].str.lower()
            rank_df = rank_df[["address", "rank"]].rename(columns={"address": "Wallet", "rank": "Rank"})
        except Exception as e:
            logging.error(f"❌ Failed to load HYPE_rank.csv: {e}")
            rank_df = pd.DataFrame(columns=["Wallet", "Rank"])

        top_100_ranks = rank_df.sort_values("Rank", ascending=True).head(100).copy()

        results_df = pd.DataFrame(results)
        results_df["Wallet"] = results_df["Wallet"].str.lower()

        merged_df = top_100_ranks.merge(results_df, on="Wallet", how="left")
        merged_df["Alias"] = merged_df["Wallet"].apply(get_alias)

        front_cols = ["Rank", "Alias", "Wallet", "Total Inflow Volume", "Total Outflow Volume",
                      "General Capital Flow", "Token with the most amount of USD value transfer"]
        all_cols = front_cols + [col for col in merged_df.columns if col not in front_cols and col != "address"]
        final_df = merged_df[all_cols]

        final_df.to_csv(OUTPUT_FILE, index=False)
        logging.info(f"✅ Top 100 ranks saved to {OUTPUT_FILE}")

    if unprocessed:
        logging.warning("⚠️ Unprocessed wallets:")
        for w in unprocessed:
            logging.warning(f" - {w}")

if __name__ == "__main__":
    main()
