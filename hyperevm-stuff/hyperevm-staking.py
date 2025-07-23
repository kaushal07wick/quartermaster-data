import csv
from datetime import datetime

# File path to your CSV
csv_file_path = 'Master_Data/0x2222222222222222222222222222222222222222_2025-07-16T10_14_40.975Z.csv'

# Target "to" wallet
target_to_wallet = '0x393d0b87ed38fc779fd9611144ae649ba6082109'.lower()

# Track earliest and latest tx
first_tx = {'time': float('inf'), 'hash': None}
last_tx = {'time': float('-inf'), 'hash': None}

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        to_addr = row['to'].lower()

        if to_addr != target_to_wallet:
            continue

        try:
            timestamp = int(row['time'])
        except ValueError:
            print(f"Skipping invalid timestamp: {row['time']}")
            continue

        # Update first and last tx for this wallet
        if timestamp < first_tx['time']:
            first_tx['time'] = timestamp
            first_tx['hash'] = row['hash']
        if timestamp > last_tx['time']:
            last_tx['time'] = timestamp
            last_tx['hash'] = row['hash']

# Convert timestamps
def format_ts(ts_ms):
    return datetime.utcfromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d %H:%M:%S UTC')

# Output results
if first_tx['hash'] and last_tx['hash']:
    print(f"📥 First tx to {target_to_wallet}:")
    print(f"   Time: {format_ts(first_tx['time'])}")
    print(f"   Hash: {first_tx['hash']}")
    print()
    print(f"📤 Last tx to {target_to_wallet}:")
    print(f"   Time: {format_ts(last_tx['time'])}")
    print(f"   Hash: {last_tx['hash']}")
else:
    print(f"No transactions found where `to` is {target_to_wallet}")
