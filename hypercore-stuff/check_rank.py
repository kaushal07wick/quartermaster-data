import csv

def read_ranked_wallets(filepath):
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)[:100]
        wallet_list = [(int(row["Rank"]), row["Wallet_address"].lower()) for row in rows]
        wallet_set = set(w.lower() for _, w in wallet_list)
        return wallet_list, wallet_set

def read_hype_rank_csv(filepath):
    with open(filepath, newline='') as f:
        reader = list(csv.DictReader(f))
        reader.reverse()  # Make index 0 = rank 1
        return [row["address"].lower() for row in reader]

def compare_wallets(truth_file, hype_file):
    truth_ranked_wallets, wallet_set = read_ranked_wallets(truth_file)
    hype_wallets_by_rank = read_hype_rank_csv(hype_file)

    mismatches = []

    for truth_rank, wallet in truth_ranked_wallets:
        expected_wallet = hype_wallets_by_rank[truth_rank - 1]
        if wallet != expected_wallet:
            mismatches.append({
                "rank": truth_rank,
                "wallet_sorted": wallet,
                "wallet_hype_rank": expected_wallet,
                "present_in_sorted_csv": expected_wallet in wallet_set
            })

    return mismatches

# File paths
truth_file = "100_wallets.csv"
hype_file = "HYPE_rank.csv"

# Run comparison
mismatches = compare_wallets(truth_file, hype_file)

# Output
if not mismatches:
    print("✅ Top 100 ranks match HYPE_rank.csv truth.")
else:
    print(f"❌ {len(mismatches)} mismatches found:\n")
    for m in mismatches:
        presence = "✅" if m["present_in_sorted_csv"] else "❌"
        print(
            f"Rank {m['rank']:3}: Got ...{m['wallet_sorted'][-5:]}, "
            f"Expected ...{m['wallet_hype_rank'][-5:]} → In Sorted CSV: {presence}"
        )
