import json
import sys
import yaml

def infer_schema(data):
    if isinstance(data, dict):
        return {key:infer_schema(value) for key, value in data.items()}
    elif isinstance(data, list):
        if data:
            return [infer_schema(data[0])]
        else:
            return ["emptyList"]
    else:
        return type(data).__name__
    
def load_and_print_yaml_schema(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    schema = infer_schema(data)
    print("Inferred json shcema: ")
    print(yaml.dump(schema, sort_keys=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage : python3 schema.py <path_to_json_file>")
    else:
        load_and_print_yaml_schema(sys.argv[1])