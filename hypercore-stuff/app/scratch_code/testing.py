import aiohttp
import asyncio
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ---- Config ----
WALLETS = ["0x5b5d51203a0f9079f8aeb098a6523a13f298c060"]
RPC_URL = "https://rpc.hyperliquid.xyz/explorer"
OUTPUT_CSV = "wallet_transactions.csv"

# ---- Time formatting ----
def time_ago(ts: datetime) -> str:
    now = datetime.utcnow()
    diff = now - ts
    days = diff.days
    seconds = diff.seconds

    if days == 0:
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            return f"{seconds // 60} min ago"
        else:
            return f"{seconds // 3600} hours ago"
    elif days == 1:
        return "1 day ago"
    else:
        return f"{days} days ago"

# ---- Fetch from RPC ----
async def fetch_user_details(session: aiohttp.ClientSession, address: str):
    payload = {"type": "userDetails", "user": address}
    async with session.post(RPC_URL, json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return address, data

# ---- Extract transaction fields ----
def extract(tx: Dict[str, Any], wallet: str) -> Dict[str, Any]:
    a = tx.get("action", {})
    ttype = a.get("type", "unknown")
    to = ""
    tok = ""
    amount = 0.0

    try:
        if ttype == "spotSend":
            to = a.get("destination", "")
            amount = float(a.get("amount", 0))
            tok = a.get("token", "")
        elif ttype == "cWithdraw":
            to = "External"
            amount = float(a.get("wei", 0))
            tok = a.get("token", "")
        elif ttype == "order":
            orders = a.get("orders", [])
            if orders:
                order = orders[0]
                amount = float(order.get("s", 0))
                tok = order.get("t", "")
                to = "Market (Buy)" if order.get("b", True) else "Market (Sell)"
        elif ttype in {"deposit", "genesis"}:
            to = "Self"
            amount = float(a.get("wei", 0))
            tok = a.get("token", "")
        elif ttype == "VoteGlobalAction":
            spot_deploy = a.get("spotDeploy", {})
            genesis = spot_deploy.get("genesis", [])
            if isinstance(genesis, list) and len(genesis) == 2:
                amount = float(genesis[1]) / 1e18
                tok = f"TOKEN_{genesis[0]}"
                to = "Genesis Init"
        elif ttype == "spotDeploy":
            genesis = a.get("genesis", {})
            if isinstance(genesis, dict):
                amount = float(genesis.get("maxSupply", 0)) / 1e18
                tok = f"TOKEN_{genesis.get('token')}"
                to = "Genesis Deploy"
        else:
            amt = a.get("amount") or a.get("wei") or 0
            amount = float(amt)
            tok = a.get("token", "")
            to = a.get("destination", "")

        # Normalize token name
        if ":" in tok:
            tok = tok.split(":")[0].strip()

        if to and to.lower() == wallet.lower():
            to = "Self"

    except Exception as e:
        print(f"⚠️ Error parsing tx for {wallet}: {e}")
        amount = 0.0

    tx_time = datetime.fromtimestamp(tx.get("time", 0) / 1000)

    return {
        "wallet": wallet,
        "time": time_ago(tx_time),
        "action_type": ttype,
        "from": tx.get("user", ""),
        "to": to,
        "token": tok,
        "amount": round(amount, 8),
        "hash": tx.get("hash", "")
    }

# ---- Fetch & Export ----
async def main():
    print("🚀 Fetching wallet transactions...")
    results: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user_details(session, wallet) for wallet in WALLETS]
        responses = await asyncio.gather(*tasks)

        for wallet, data in responses:
            txs = data.get("txs", [])
            extracted = [extract(tx, wallet) for tx in txs]
            results.extend(extracted)

    if not results:
        print("⚠️ No transactions found.")
        return

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Exported {len(results)} transactions to {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
