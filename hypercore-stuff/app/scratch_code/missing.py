import csv

def load_wallets_from_txt(txt_path):
    with open(txt_path, 'r') as f:
        return set(line.strip().lower() for line in f if line.strip())

def load_wallets_from_csv(csv_path):
    wallets = set()
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) > 1:
                wallets.add(row[0].strip().lower())  # second column (index 1)
    return wallets

def find_missing_wallets(txt_file, csv_file):
    txt_wallets = load_wallets_from_txt(txt_file)
    csv_wallets = load_wallets_from_csv(csv_file)
    missing = txt_wallets - csv_wallets
    return missing

if __name__ == '__main__':
    txt_file = 'miss_Wall.txt'      # your input .txt file
    csv_file = 'wallet_analysis_100.csv'       # your output .csv file
    missing = find_missing_wallets(txt_file, csv_file)

    if missing:
        print(f"❌ {len(missing)} wallet(s) not found in CSV:")
        for wallet in sorted(missing):
            print(wallet)
    else:
        print("✅ All wallets found in the CSV.")
