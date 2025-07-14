import csv

HYPE_PRICE = 41.684
HYPE_RANK_CSV = "HYPE_rank.csv"
WALLET_DATA_CSV = "100_wallets.csv"

def format_usd(value):
    return f"${value:,.2f}"

def read_wallets_aum():
    with open(WALLET_DATA_CSV, newline='') as f:
        reader = csv.DictReader(f)
        return sorted(reader, key=lambda row: int(row["Rank"]))

def read_hype_amounts():
    with open(HYPE_RANK_CSV, newline='') as f:
        reader = list(csv.DictReader(f))
        return list(reversed(reader))  # Reverse to align rank 1 at index 0

def main():
    wallet_rows = read_wallets_aum()
    hype_rows = read_hype_amounts()


    print(f"{'Rank':<5} {'Wallet':<42} {'HYPE Amt':>12} {'HYPE x Price':>16} {'Total AUM':>16}")
    print("-" * 95)

    for i, (wallet, hype) in enumerate(zip(wallet_rows, hype_rows), 1):
        wallet_addr = wallet["Wallet_address"]
        hype_amt = float(hype["amount"])
        hype_val = hype_amt * HYPE_PRICE
        total_aum = float(wallet["Total AUM"])

        print(f"{i:<5} {wallet_addr:<42} {hype_amt:>12,.2f} {format_usd(hype_val):>16} {format_usd(total_aum):>16}")

if __name__ == "__main__":
    main()
