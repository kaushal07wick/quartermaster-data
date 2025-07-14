#!/usr/bin/env python3

import os
import argparse
import csv

def extract_top_wallets(csv_path, top_n=100):
    top_wallets = set()
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    rank = int(row["rank"])
                    if 1 <= rank <= top_n:
                        address = row["address"].strip().lower()
                        if address.startswith("0x"):
                            top_wallets.add(address)
                except:
                    continue
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
    return top_wallets

def extract_wallets_from_files(folder_path):
    file_wallets = set()
    for _, _, files in os.walk(folder_path):
        for file in files:
            if "_" in file:
                wallet = file.split("_")[0].strip().lower()
                if wallet.startswith("0x"):
                    file_wallets.add(wallet)
    return file_wallets

def compare_wallets(top_wallets, file_wallets):
    present = sorted(top_wallets & file_wallets)
    missing = sorted(top_wallets - file_wallets)

    print(f"\n📊 Wallet File Check (Top {len(top_wallets)} wallets):")
    print(f"✅ Present: {len(present)}")
    print(f"❌ Missing: {len(missing)}\n")

    if present:
        print("✅ Wallets Found in Folder:")
        for addr in present:
            print(f"  - {addr}")

    if missing:
        print("\n❌ Wallets Missing From Folder:")
        for addr in missing:
            print(f"  - {addr}")

    # Optionally write to CSV
    with open("wallet_check_summary.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["wallet_address", "status"])
        for wallet in sorted(top_wallets):
            status = "present" if wallet in file_wallets else "missing"
            writer.writerow([wallet, status])
    print("\n📝 CSV written: wallet_check_summary.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if top N wallet files exist in folder.")
    parser.add_argument("folder", help="Path to the folder to check")
    parser.add_argument("--csv", help="CSV file with ranked wallets", required=True)
    parser.add_argument("--top", type=int, default=100, help="Top N ranks to check (default: 100)")

    args = parser.parse_args()

    top_wallets = extract_top_wallets(args.csv, args.top)
    file_wallets = extract_wallets_from_files(args.folder)
    compare_wallets(top_wallets, file_wallets)
