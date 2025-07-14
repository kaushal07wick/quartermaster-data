import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm
from aiohttp import ClientConnectionError, ServerDisconnectedError, ClientPayloadError

from app.config import RPC_URLS
from app.logger import get_logger

logger = get_logger(__name__)
URL = RPC_URLS["HYPERLIQUID"]

# Retry decorator for robustness
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
async def fetch_user_details(session: aiohttp.ClientSession, address: str):
    try:
        payload = {"type": "userDetails", "user": address}
        async with session.post(URL, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return address, data
    except (ClientConnectionError, ServerDisconnectedError, ClientPayloadError) as e:
        logger.warning(f"Connection error for {address}: {e}")
        raise

def extract(tx: Dict[str, Any], wallet: str):
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
        tok = ""
    elif ttype == "order":
        orders = a.get("orders", [])
        if orders:
            order = orders[0]
            side = "Buy" if order.get("b", True) else "Sell"
            price = order.get("p", "")
            size = order.get("s", "")
            tok = order.get("t", "")  # Token symbol (if available)
            amt = str(size)  # Use size as amount
            to = f"Market ({side})"
        else:
            to = "Market"
            amt = ""
            tok = ""
    elif ttype == "deposit":
        to = "Self"
        amt = str(a.get("wei", ""))
        tok = a.get("token", "")
    else:
        # For unknown or other types, just capture available fields
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

async def fetch_all_wallets():
    wallets = [w.strip() for w in open("wallets.txt") if w.strip()]
    all_actions = {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user_details(session, w) for w in wallets]

        for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching Wallets"):
            addr, data = await fut
            txs = data.get("txs", [])  # <<< take ALL txs directly

            extracted = [extract(tx, addr) for tx in txs]

            if extracted:
                all_actions[addr] = extracted

    return all_actions

async def main():
    by_wallet_data = await fetch_all_wallets()

    # Print detailed data per wallet
    for wallet, txs in by_wallet_data.items():
        print(f"\n========== Wallet: {wallet} ==========")
        print(f"Total Transactions: {len(txs)}\n")
        for tx in txs:
            print(tx)
        print("\n--------------------------------------")

    print("\n\nFinished fetching and processing all wallets.\n")

if __name__ == "__main__":
    asyncio.run(main())
