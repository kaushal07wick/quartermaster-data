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
data = response.json()

# Extract basic token details
token_details = {
    "name": data.get("name"),
    "maxSupply": data.get("maxSupply"),
    "totalSupply": data.get("totalSupply"),
    "circulatingSupply": data.get("circulatingSupply"),
    "markPx": data.get("markPx")
}

# Write token details to CSV
with open("hype_token_details.csv", mode="w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=token_details.keys())
    writer.writeheader()
    writer.writerow(token_details)

print("✅ Token details saved to 'hype_token_details.csv'")

# Extract and process genesis user balances
user_balances = data.get("genesis", {}).get("userBalances", [])
# Each entry should be a list like: ["0xAddress", "balance"]
# Sort descending by balance (as float)
sorted_balances = sorted(
    user_balances,
    key=lambda x: float(x[1]),
    reverse=True
)

# Write user balances to CSV
with open("genesis_user_balances.csv", mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["rank", "address", "balance"])
    for rank, (address, balance) in enumerate(sorted_balances, start=1):
        writer.writerow([rank, address, balance])

print("✅ Genesis user balances saved to 'genesis_user_balances.csv'")
