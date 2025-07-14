# wallet_processor.py
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm
from aiohttp import ClientConnectionError, ClientResponseError, ServerDisconnectedError, ClientPayloadError
import csv

from config import RPC_URLS, PRICES, MEMECOINS, WALLET_FILE, OUTPUT_CSV
from stake_rewards import get_staking_info 

# === FETCH ===

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
async def fetch_user_details(session: aiohttp.ClientSession, address: str):
    try:
        payload = {"type": "userDetails", "user": address}
        async with session.post(RPC_URLS["HYPERLIQUID"], json=payload) as resp:
            if resp.status != 200:
                raise ClientResponseError(
                    request_info=resp.request_info,
                    history=resp.history,
                    status=resp.status,
                    message=f"Non-200 response: {resp.status}",
                    headers=resp.headers
                )
            data = await resp.json()
            return address, data
    except (ClientConnectionError, ServerDisconnectedError, ClientPayloadError, ClientResponseError) as e:
        print(f"⚠️ Connection error for {address}: {e}")
        raise

def extract(tx: Dict[str, Any], wallet: str) -> Dict[str, Any]:
    a = tx.get("action", {})
    ttype = a.get("type", "unknown")
    to = amt = tok = ""

    if ttype == "spotSend":
        to = a.get("destination", "")
        amt = a.get("amount", "")
        tok = a.get("token", "")
    elif ttype == "cWithdraw":
        to = "External"
        amt = str(a.get("wei", ""))
    elif ttype == "order":
        orders = a.get("orders", [])
        if orders:
            order = orders[0]
            side = "Buy" if order.get("b", True) else "Sell"
            amt = str(order.get("s", ""))
            tok = order.get("t", "")
            to = f"Market ({side})"
    elif ttype == "deposit":
        to = "Self"
        amt = str(a.get("wei", ""))
        tok = a.get("token", "")
    else:
        to = a.get("destination", "")
        amt = a.get("amount", "") or str(a.get("wei", ""))
        tok = a.get("token", "")

    if to.lower() == wallet.lower():
        to = "Self"

    return {
        "wallet": wallet,
        "time": datetime.fromtimestamp(tx.get("time", 0) / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        "action_type": ttype,
        "from": tx.get("user", ""),
        "to": to,
        "token": tok,
        "amount": amt,
        "hash": tx.get("hash", "")
    }

async def fetch_all_wallets() -> Dict[str, List[Dict[str, Any]]]:
    with open(WALLET_FILE) as f:
        wallets = [line.strip() for line in f if line.strip()]

    all_actions = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user_details(session, w) for w in wallets]

        for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="📦 Fetching wallets"):
            addr, data = await fut
            txs = data.get("txs", [])
            all_actions[addr] = [extract(tx, addr) for tx in txs]

    return all_actions

# === PROCESSING ===

def process_wallet(address: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    hype = usdc = memecoins = 0.0
    txn_amounts = []   # For AUM
    avg_amounts = []   # For clean average

    for txn in transactions:
        token = str(txn.get("token", "")).upper().split(":")[0].strip()
        amount_raw = txn.get("amount", "").strip()
        action_type = txn.get("action_type", "")

        try:
            amt = float(amount_raw)
        except (ValueError, TypeError):
            amt = 0.0

        # For AUM
        if token == "HYPE":
            hype += amt
        elif token == "USDC":
            usdc += amt
        elif token in MEMECOINS:
            memecoins += amt

        txn_amounts.append(amt)

        # ✅ Only include relevant txs for average
        if action_type in {"spotSend", "order"} and amt > 0:
            avg_amounts.append(amt)

    # Staking
    staking = get_staking_info(address)
    net_staked = staking["net_staked"]
    staking_rewards = staking["delegation_rewards"]

    # AUM
    total_hype = hype + net_staked
    total_aum = round(total_hype * PRICES["HYPE"] + usdc * PRICES["USDC"], 2)

    # Clean average
    avg_txn = round(sum(avg_amounts) / len(avg_amounts), 2) if avg_amounts else 0.0

    return {
        "wallet": address,
        "total_aum": total_aum,
        "hype": round(hype, 2),
        "usdc": round(usdc, 2),
        "memecoins": round(memecoins, 2),
        "net_staked": net_staked,
        "staking_rewards": staking_rewards,
        "avg_txn_amt": avg_txn
    }

# === MAIN ===

async def main():
    print("🚀 Starting wallet processing...")
    wallet_data = await fetch_all_wallets()
    print("✅ Data fetched. Processing...")

    results = []
    for wallet, txs in wallet_data.items():
        results.append(process_wallet(wallet, txs))

    for r in results:
        print(f"{r['wallet']} | AUM: ${r['total_aum']} | HYPE: {r['hype']} | Staked: {r['net_staked']} | Rewards: {r['staking_rewards']}")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Finished. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
