import requests
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import datetime

# SQLite setup
conn = sqlite3.connect('quartermaster.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_address TEXT,
        total_aum REAL,
        hype REAL,
        usdc REAL,
        memecoins REAL,
        hype_staked REAL,
        hype_staked_pct REAL,
        memes_pct REAL,
        txn_frequency TEXT,
        capital_flow TEXT,
        max_txn_value REAL,
        total_inflow REAL,
        total_outflow REAL,
        avg_txn_value REAL,
        most_transferred_token TEXT,
        staking_cycles TEXT,
        total_fee_spend REAL,
        outflow_wallet_1 TEXT,
        outflow_wallet_2 TEXT,
        outflow_wallet_3 TEXT,
        outflow_wallet_4 TEXT,
        outflow_wallet_5 TEXT
        -- trading TEXT,
        -- staking_rewards REAL,
        -- withdrawals_arbitrum_freq TEXT,
        -- deposits_arbitrum_freq TEXT,
        -- total_trades INTEGER,
        -- most_traded_coin TEXT,
        -- max_profit REAL,
        -- max_loss REAL
    )
''')
conn.commit()

# Example wallet addresses
wallet_addresses = [
    "0x77c3ea550d2da44b120e55071f57a108f8dd5e45",
    "0x716bd8d3337972db99995dda5c4b34d954a61d95"
]

url = "https://api.hyperliquid.xyz/info"
headers = {"Content-Type": "application/json"}

# Define your memecoin tokens
memecoin_tokens = ["MEME1", "MEME2", "MEME3"]  # Replace with actual token names

def fetch_wallet_data(address):
    payload = {
        "type": "userNonFundingLedgerUpdates",
        "user": address
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        hype = 0.0
        usdc = 0.0
        memecoins = 0.0
        hype_staked = 0.0
        total_inflow = 0.0
        total_outflow = 0.0
        max_txn_value = 0.0
        txn_amounts = []
        txn_timestamps = []
        token_volumes = {}
        outflow_wallets = []
        total_fee_spend = 0.0
        staking_detected = False

        for entry in data:
            token = entry.get('token')
            amount = float(entry.get('amount', 0.0))
            is_deposit = entry.get('isDeposit', True)
            usdc_value = float(entry.get('usdcValue', 0.0))
            txn_value = abs(usdc_value)
            fee = float(entry.get('fee', 0.0))
            timestamp = entry.get('timestamp')
            destination = entry.get('destination')

            # Track fees
            total_fee_spend += fee

            # Max transaction
            if txn_value > max_txn_value:
                max_txn_value = txn_value

            # Inflow / Outflow
            if is_deposit:
                total_inflow += usdc_value
            else:
                total_outflow += abs(usdc_value)
                if destination:
                    outflow_wallets.append(destination)

            # Asset breakdown
            if token == "HYPE":
                hype += amount
                if entry.get('type') == "cStakingTransfer" and is_deposit:
                    hype_staked += amount
                    staking_detected = True
            elif token == "USDC":
                usdc += amount
            elif token in memecoin_tokens:
                memecoins += amount

            # Token volumes
            if token:
                token_volumes[token] = token_volumes.get(token, 0) + txn_value

            # For frequency calculation
            if timestamp:
                txn_timestamps.append(datetime.fromisoformat(timestamp))

            # Track all transaction sizes
            txn_amounts.append(txn_value)

        # Derived calculations
        total_aum = total_inflow - total_outflow
        hype_staked_pct = (hype_staked / total_aum) * 100 if total_aum > 0 else 0
        memes_pct = (memecoins / total_aum) * 100 if total_aum > 0 else 0
        avg_txn_value = sum(txn_amounts) / len(txn_amounts) if txn_amounts else 0

        most_transferred_token = max(token_volumes.items(), key=lambda x: x[1])[0] if token_volumes else None

        # Capital flow direction
        if total_inflow > total_outflow:
            capital_flow = "Positive"
        elif total_outflow > total_inflow:
            capital_flow = "Negative"
        else:
            capital_flow = "Neutral"

        # Calculate transaction frequency
        txn_frequency = "Not enough data"
        if len(txn_timestamps) > 1:
            txn_timestamps.sort()
            intervals = [(txn_timestamps[i + 1] - txn_timestamps[i]).days for i in range(len(txn_timestamps) - 1)]
            avg_days = sum(intervals) / len(intervals) if intervals else 0
            if avg_days > 30:
                txn_frequency = "Rarely"
            elif avg_days > 7:
                txn_frequency = "Monthly"
            elif avg_days > 1:
                txn_frequency = "Weekly"
            else:
                txn_frequency = "Daily"

        # Outflow wallet rankings
        top_outflows = Counter(outflow_wallets).most_common(5)
        top_outflow_wallets = [wallet for wallet, _ in top_outflows]
        while len(top_outflow_wallets) < 5:
            top_outflow_wallets.append(None)

        return (
            address, total_aum, hype, usdc, memecoins, hype_staked, hype_staked_pct,
            memes_pct, txn_frequency, capital_flow, max_txn_value, total_inflow,
            total_outflow, avg_txn_value, most_transferred_token,
            "Yes" if staking_detected else "No", total_fee_spend,
            top_outflow_wallets[0], top_outflow_wallets[1], top_outflow_wallets[2],
            top_outflow_wallets[3], top_outflow_wallets[4]
        )

    except Exception as e:
        print(f"Error fetching data for {address}: {e}")
        return None

def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_wallet_data, wallet_addresses))

    for result in results:
        if result:
            cursor.execute('''
                INSERT INTO wallet_analysis (
                    wallet_address, total_aum, hype, usdc, memecoins, hype_staked, hype_staked_pct,
                    memes_pct, txn_frequency, capital_flow, max_txn_value, total_inflow,
                    total_outflow, avg_txn_value, most_transferred_token,
                    staking_cycles, total_fee_spend,
                    outflow_wallet_1, outflow_wallet_2, outflow_wallet_3,
                    outflow_wallet_4, outflow_wallet_5
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', result)

    conn.commit()
    conn.close()
    print("Data fetch and storage complete.")

if __name__ == "__main__":
    main()
