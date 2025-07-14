import csv
import requests
import time

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}
HYPE_PRICE = 39.61  # change if needed

def fetch_data(payload):
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error during API call: {e}")
        return None

def get_staking_info(wallet: str) -> dict:
    summary = fetch_data({"type": "delegatorSummary", "user": wallet})
    time.sleep(0.1)
    rewards = fetch_data({"type": "delegatorRewards", "user": wallet})

    if not summary or not rewards:
        return {"net_staked": 0.0, "delegation_rewards": 0.0}

    delegation_rewards_total = sum(
        float(r.get("totalAmount", 0)) for r in rewards if r.get("source") == "delegation"
    )

    return {
        "net_staked": round(float(summary.get("delegated", 0.0)), 6),
        "delegation_rewards": round(delegation_rewards_total, 6)
    }

def process_wallet_csv(wallet_address: str, csv_file: str) -> dict:
    wallet = wallet_address.lower()
    hype_amount = 0.0
    usdc_amount = 0.0

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            token = row['token'].split(':')[0].upper()  # e.g., "HYPE" from "HYPE:0x..."
            amt = float(row.get('amount', 0))
            to = row['destination'].lower()
            from_ = row['user'].lower()

            if to == wallet:
                # Deposit
                if token == 'HYPE':
                    hype_amount += amt
                elif token == 'USDC':
                    usdc_amount += amt
            elif from_ == wallet:
                # Withdrawal
                if token == 'HYPE':
                    hype_amount -= amt
                elif token == 'USDC':
                    usdc_amount -= amt

    hype_usd = hype_amount * HYPE_PRICE
    return {
        "hype": round(hype_amount, 2),
        "hype_usd": round(hype_usd, 2),
        "usdc": round(usdc_amount, 2)
    }

def compute_total_aum(wallet: str, csv_file: str):
    staking = get_staking_info(wallet)
    wallet_balances = process_wallet_csv(wallet, csv_file)

    total_aum = (
        wallet_balances["hype_usd"]
        + wallet_balances["usdc"]
        + staking["net_staked"] * HYPE_PRICE
        + staking["delegation_rewards"]
    )

    print(f"\n📊 AUM Summary for {wallet}")
    print(f"💰 HYPE Amount: {wallet_balances['hype']} (~${wallet_balances['hype_usd']})")
    print(f"💵 USDC Amount: {wallet_balances['usdc']}")
    print(f"🧱 Staked HYPE: {staking['net_staked']}")
    print(f"🎁 Delegation Rewards: {staking['delegation_rewards']}")
    print(f"🧮 Total AUM: ${round(total_aum, 2)}")

# Example usage
if __name__ == "__main__":
    wallet_address = "0x716bd8d3337972db99995dda5c4b34d954a61d95"  # Replace with target
    csv_path = "0x716bd8d3337972db99995dda5c4b34d954a61d95_hyperliquid_transactions.csv"  # Replace with your CSV file path
    compute_total_aum(wallet_address, csv_path)
