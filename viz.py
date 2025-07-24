import json
import csv
import os
import sys

def save_csv(data, filename, nested_field=None):
    """Save list of dictionaries to CSV, flattening nested fields and handling variable keys."""
    if not data:
        return

    rows = []
    all_keys = set()

    if nested_field:
        for item in data:
            base = {"date": item.get("date")}
            nested = item.get(nested_field, {})
            if isinstance(nested, dict):
                base.update(nested)
            rows.append(base)
            all_keys.update(base.keys())
    else:
        rows = data
        for row in rows:
            all_keys.update(row.keys())

    fieldnames = ["date"] + sorted(k for k in all_keys if k != "date")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

def process_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs("csv_output", exist_ok=True)

    # Save top-level arrays
    save_csv(data.get("tvl", []), "csv_output/tvl.csv")
    save_csv(data.get("tokens", []), "csv_output/tokens.csv", nested_field="tokens")
    save_csv(data.get("tokensInUsd", []), "csv_output/tokensInUsd.csv", nested_field="tokens")

    # Save nested chainTvls → Hyperliquid L1
    hl1 = data.get("chainTvls", {}).get("Hyperliquid L1", {})
    if "tvl" in hl1:
        save_csv(hl1["tvl"], "csv_output/chainTvls_Hyperliquid_L1_tvl.csv")
    if "tokens" in hl1:
        save_csv(hl1["tokens"], "csv_output/chainTvls_Hyperliquid_L1_tokens.csv", nested_field="tokens")
    if "tokensInUsd" in hl1:
        save_csv(hl1["tokensInUsd"], "csv_output/chainTvls_Hyperliquid_L1_tokensInUsd.csv", nested_field="tokens")

    print("✅ All CSVs written to ./csv_output/")

# Run the script
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_csvs.py <path_to_json_file>")
    else:
        process_json(sys.argv[1])
