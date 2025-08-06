import json
import sys
import yaml
import os

def infer_schema(data):
    if isinstance(data, dict):
        return {key: infer_schema(value) for key, value in data.items()}
    elif isinstance(data, list):
        if data:
            return [infer_schema(data[0])]
        else:
            return ["emptyList"]
    else:
        return type(data).__name__

def load_and_save_yaml_schema(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    schema = infer_schema(data)

    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    output_file = f"{base_name}_schema.yaml"

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(schema, f, sort_keys=False)

    print(f"Inferred JSON schema saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 schema.py <path_to_json_file>")
    else:
        load_and_save_yaml_schema(sys.argv[1])
