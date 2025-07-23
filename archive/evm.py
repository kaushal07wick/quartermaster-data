import requests
import json

url = "https://rpc.hyperliquid.xyz/evm"

# JSON-RPC request payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))

except Exception as e:
    print(f"Error: {e}")
