import requests
import csv
from datetime import datetime

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {"Content-Type": "application/json"}

def fetch_staking_summary(user):
    payload = {"type": "delegatorSummary", "user": user}
    response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_staking_history(user):
    payload = {"type": "delegatorHistory", "user": user}
    response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_staking_rewards(user):
    payload = {"type": "delegatorRewards", "user": user}
    response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()

def consolidate_staking_data(user):
    print("Fetching staking summary...")
    summary = fetch_staking_summary(user)

    print("Fetching staking history...")
    history = fetch_staking_history(user)

    print("Fetching staking rewards...")
    rewards = fetch_staking_rewards(user)

    consolidated = []
    
    # Include staking summary as a row
    consolidated.append({
        "RecordType": "Summary",
        "Timestamp": "",
        "TransactionHash": "",
        "Validator": "",
        "Action": "",
        "Amount": "",
        "RewardSource": "",
        "RewardAmount": "",
        "DelegatedAmount": summary.get("delegated"),
        "UndelegatedAmount": summary.get("undelegated"),
        "PendingWithdrawalAmount": summary.get("totalPendingWithdrawal"),
        "NumberOfPendingWithdrawals": summary.get("nPendingWithdrawals")
    })

    # Include staking history transactions
    for tx in history:
        delta = tx.get("delta", {}).get("delegate", {})
        consolidated.append({
            "RecordType": "History",
            "Timestamp": datetime.fromtimestamp(tx.get("time") / 1000).isoformat(),
            "TransactionHash": tx.get("hash"),
            "Validator": delta.get("validator"),
            "Action": "Undelegate" if delta.get("isUndelegate") else "Delegate",
            "Amount": delta.get("amount"),
            "RewardSource": "",
            "RewardAmount": "",
            "DelegatedAmount": "",
            "UndelegatedAmount": "",
            "PendingWithdrawalAmount": "",
            "NumberOfPendingWithdrawals": ""
        })

    # Include staking rewards transactions
    for reward in rewards:
        consolidated.append({
            "RecordType": "Reward",
            "Timestamp": datetime.fromtimestamp(reward.get("time") / 1000).isoformat(),
            "TransactionHash": "",
            "Validator": "",
            "Action": "",
            "Amount": "",
            "RewardSource": reward.get("source"),
            "RewardAmount": reward.get("totalAmount"),
            "DelegatedAmount": "",
            "UndelegatedAmount": "",
            "PendingWithdrawalAmount": "",
            "NumberOfPendingWithdrawals": ""
        })

    return consolidated

def save_to_csv(data, user):
    filename = f"{user}_staking_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    keys = [
        "RecordType", "Timestamp", "TransactionHash", "Validator", "Action", "Amount",
        "RewardSource", "RewardAmount", "DelegatedAmount", "UndelegatedAmount",
        "PendingWithdrawalAmount", "NumberOfPendingWithdrawals"
    ]

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"✅ Consolidated staking data saved to {filename}")

if __name__ == "__main__":
    wallet_address = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45"
    staking_data = consolidate_staking_data(wallet_address)
    save_to_csv(staking_data, wallet_address)
