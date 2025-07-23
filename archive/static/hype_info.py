import requests
import csv

# API endpoint and payload
url = "https://api.hyperliquid.xyz/info"
payload = {
    "type": "tokenDetails",
    "tokenId": "0x0d01dc56dcaaca66ad901c959b4011ec"
}
headers = {
    "Content-Type": "application/json"
}

# Make POST request
response = requests.post(url, json=payload, headers=headers)
response.raise_for_status()

# Parse the response
data = response.json()

# Extract relevant fields
output = {
    "name": data.get("name"),
    "maxSupply": data.get("maxSupply"),
    "totalSupply": data.get("totalSupply"),
    "circulatingSupply": data.get("circulatingSupply"),
    "markPx": data.get("markPx")
}

# CSV file path
csv_filename = "hype_token_details.csv"

# Write to CSV
with open(csv_filename, mode="w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=output.keys())
    writer.writeheader()
    writer.writerow(output)

print(f"CSV saved: {csv_filename}")

