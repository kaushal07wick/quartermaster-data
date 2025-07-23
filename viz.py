import json
import csv
import os

def save_csv(data, filename, nested_field=None):
    """Save list of dictionaries to CSV"""
    if not data:
        return
    if nested_field:
        # Flatten the nested dicts inside 'tokens'
        rows = []
        for item in data:
            base = {"date": item.get("date")}
            nested = item.get(nested_field, {})
            if isinstance(nested, dict):
                base.update(nested)
            rows.append(base)
        fieldnames = rows[0].keys()
    else:
        rows = data
        fieldnames = rows[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def process_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs("csv_output", exist_ok=True)

    # Write top-level arrays
    save_csv(data.get("tvl", []), "csv_output/tvl.csv")
    save_csv(data.get("tokensInUsd", []), "csv_output/tokensInUsd.csv", nested_field="tokens")
    save_csv(data.get("tokens", []), "csv_output/tokens.csv", nested_field="tokens")

    # Process chainTvls → Hyperliquid L1
    hl1 = data.get("chainTvls", {}).get("Hyperliquid L1", {})

    if "tvl" in hl1:
        save_csv(hl1["tvl"], "csv_output/chainTvls_Hyperliquid_L1_tvl.csv")
    if "tokensInUsd" in hl1:
        save_csv(hl1["tokensInUsd"], "csv_output/chainTvls_Hyperliquid_L1_tokensInUsd.csv", nested_field="tokens")
    if "tokens" in hl1:
        save_csv(hl1["tokens"], "csv_output/chainTvls_Hyperliquid_L1_tokens.csv", nested_field="tokens")

    print("✅ All relevant CSVs have been written to the 'csv_output/' directory.")

# Run script
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python json_to_csvs.py <path_to_json_file>")
    else:
        process_json(sys.argv[1])
