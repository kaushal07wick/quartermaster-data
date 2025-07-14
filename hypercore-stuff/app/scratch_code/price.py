import aiohttp
import asyncio
import json

RPC_URL = "https://rpc.hyperliquid.xyz/explorer"
OUTPUT_FILE = "wallet_data.json"

async def fetch_wallet_data(wallets):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for wallet in wallets:
            payload = {"type": "userDetails", "user": wallet}
            tasks.append(session.post(RPC_URL, json=payload))
        responses = await asyncio.gather(*tasks)
        results = {}
        for i, resp in enumerate(responses):
            data = await resp.json()
            results[wallets[i]] = data.get("txs", [])
        return results

async def main(wallets):
    data = await fetch_wallet_data(wallets)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved data for {len(wallets)} wallet(s) to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    wallets = ["0x5b5d51203a0f9079f8aeb098a6523a13f298c060"]  # Add more if needed
    asyncio.run(main(wallets))
