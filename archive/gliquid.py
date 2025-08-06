import json
import csv
import os
import sys
from pathlib import Path

def flatten_dict(d, parent_key='', sep='.'):
    """Recursively flattens a nested dictionary."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def export_array_to_csv(key, array_data, output_dir):
    if not array_data or not isinstance(array_data, list):
        return

    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{key}.csv")

    # If list of dicts, flatten and export
    if all(isinstance(item, dict) for item in array_data):
        flattened = [flatten_dict(item) for item in array_data]
        headers = sorted(set().union(*(d.keys() for d in flattened)))
    else:
        # If list of primitives, store as single column
        flattened = [{key: item} for item in array_data]
        headers = [key]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flattened)

    print(f"✅ Exported: {output_file}")

def process_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        output_dir = "csv_data"
        base_name = Path(filepath).stem

        def scan_and_export(obj, parent_key=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    full_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, list):
                        export_array_to_csv(f"{base_name}__{full_key}", v, output_dir)
                    elif isinstance(v, dict):
                        scan_and_export(v, full_key)

        scan_and_export(data)

    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_historical_arrays.py <path_to_json_file>")
    else:
        process_json(sys.argv[1])
