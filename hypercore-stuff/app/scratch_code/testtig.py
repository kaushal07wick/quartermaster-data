import csv

# Replace this with your actual file path
csv_file = "0x77c3ea550d2da44b120e55071f57a108f8dd5e45_staking_data_20250708_052241.csv"

delegate_total = 0.0
undelegate_total = 0.0
delegation_rewards_total = 0.0

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['RecordType'] == 'History':
            if row['Action'] == 'Delegate' and row['Amount']:
                delegate_total += float(row['Amount'])
            elif row['Action'] == 'Undelegate' and row['Amount']:
                undelegate_total += float(row['Amount'])

        elif row['RecordType'] == 'Reward':
            if row['RewardSource'] == 'delegation' and row['RewardAmount']:
                delegation_rewards_total += float(row['RewardAmount'])

net_delegation = delegate_total - undelegate_total

print(f"🧮 Net Delegation Amount: {net_delegation}")
print(f"💰 Total Delegation Rewards: {delegation_rewards_total}")
