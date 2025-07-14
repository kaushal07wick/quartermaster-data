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
        print(f"Error reading CSV: {e}")
    return top_wallets

def clean_folder_keep_latest_top_wallets_only(folder_path, top_wallets):
    wallet_files = {}  # wallet -> (file_path, modified_time)
    removed = 0

    # First pass: identify latest file per wallet
    for root, _, files in os.walk(folder_path):
        for file in files:
            if "_" not in file:
                continue
            wallet = file.split("_")[0].strip().lower()
            if wallet not in top_wallets:
                continue

            full_path = os.path.join(root, file)
            mtime = os.path.getmtime(full_path)

            if wallet not in wallet_files or mtime > wallet_files[wallet][1]:
                wallet_files[wallet] = (full_path, mtime)

    # Second pass: delete everything not in the "keep" list
    keep_paths = set(path for path, _ in wallet_files.values())

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path not in keep_paths:
                os.remove(full_path)
                removed += 1

    print(f"\n✅ Cleanup complete: Kept {len(wallet_files)} latest wallet files, removed {removed} others.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keep only the latest file per top N wallet address.")
    parser.add_argument("folder", help="Path to the folder to clean")
    parser.add_argument("--csv", help="CSV file with ranked wallets", required=True)
    parser.add_argument("--top", type=int, default=100, help="Top N ranks to retain (default: 100)")

    args = parser.parse_args()

    top_wallets = extract_top_wallets(args.csv, args.top)
    clean_folder_keep_latest_top_wallets_only(args.folder, top_wallets)
