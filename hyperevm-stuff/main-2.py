import requests
import csv
from io import StringIO

# Input token list (only names are used now)
tokens_csv = """
name,contract
USD₮0,0xB8CE59FC3717ada4C02eaDF9682A9e934F625ebb
Wrapped HYPE WHYPE,0x5555555555555555555555555555555555555555
Staked HYPE (stHYPE),0xfFaa4a3D97fE9107Cef8a3F48c069F577Ff76cC1
Purr (PURR),0x9b498C3c8A0b8CD8BA1D9851d40D186F1872b44E
feUSD (feUSD),0x02c6a2fA58cC01A18B8D9E00eA48d65E4dF26c70
Looped HYPE (LHYPE),0x5748ae796AE46A4F1348a1693de4b50560485562
LiquidLaunch (LIQD),0x1Ecd15865D7F8019D546f76d095d9c93cc34eDFa
HFUN (HFUN),0xa320D9f65ec992EfF38622c63627856382Db726c
alright buddy (BUDDY),0x47bb061C0204Af921F43DC73C7D7768d2672DdEE
PiP (PiP),0x1bEe6762F0B522c606DC2Ffb106C0BB391b2E309
Relend Network USDC (rUSDC),0x9ab96A4668456896d45c301Bc3A15Cee76AA7B8D
USDeOFT (USDe),0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34
hwHLP (hwHLP),0x9FD7466f987Fd4C45a5BBDe22ED8aba5BC8D72d1
Wrapped HLP (WHLP),0x1359b05241cA5076c9F59605214f4F84114c0dE8
Unit Bitcoin (UBTC),0x9FDBdA0A5e284c32744D2f17Ee5c74B284993463
Kittenswap (KITTEN),0x618275F8EFE54c2afa87bfB9F210A52F0fF89364
Last USD (USDXL),0xca79db4B49f608eF54a5CB813FbEd3a6387bC645
Holy Liquid (HL),0x738dD55C272b0B686382F62DD4a590056839F4F6
XAUt0 (XAUt0),0xf4D9235269a96aaDaFc9aDAe454a0618eBE37949
Hyperstable (USH),0x8fF0dd9f9C40a0d76eF1BcFAF5f98c1610c74Bd8
Unit Ethereum (UETH),0xBe6727B535545C67d5cAa73dEa54865B92CF7907
KEI Stablecoin (KEI),0xB5fE77d323d69eB352A02006eA8ecC38D882620C
Wild Goat Coin (WGC),0xc53ac24320E3A54C7211e4993c8095078a0Cb3Cf
LICKO (LICKO),
"""

# Parse CSV input
tokens = []
reader = csv.DictReader(StringIO(tokens_csv.strip()))
for row in reader:
    name = row["name"].strip()
    if name:
        tokens.append(name.lower())  # Normalize to lowercase for matching

# API call
url = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": "CG-MuT4vFRY5gHNQ9ykZFjZRpKp"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
coins = response.json()

# Match by name, check hyperevm
results = []
for token_name in tokens:
    found = False
    for coin in coins:
        if coin.get("name", "").lower() == token_name:
            platforms = coin.get("platforms", {})
            if "hyperevm" in platforms:
                results.append({
                    "token_name": coin["name"],
                    "listed_on_hyperevm": "Yes",
                    "coingecko_id": coin.get("id"),
                    "symbol": coin.get("symbol"),
                    "hyperevm_address": platforms["hyperevm"]
                })
                found = True
                break
    if not found:
        results.append({
            "token_name": token_name,
            "listed_on_hyperevm": "No",
            "coingecko_id": "",
            "symbol": "",
            "hyperevm_address": ""
        })

# Write to CSV
output_file = "hyperevm_check_results.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Results saved to '{output_file}'")
