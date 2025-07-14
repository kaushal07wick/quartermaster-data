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

SPECIAL_ADDRESSES = {
    "0xffffffffffffffffffffffffffffffffffffffff": "HIP-2",
    "0x0000000000000000000000000000000000000000": "Burn",
    "0x2222222222222222222222222222222222222222": "HyperEVM",
    "0x000000000000000000000000000000000000dead": "Burn_dead"
}

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
        tok = a.get("token", "")
    elif ttype == "order":
        orders = a.get("orders", [])
        if orders:
            order = orders[0]
            side = "Buy" if order.get("b", True) else "Sell"
            amt = str(order.get("s", ""))
            tok = order.get("t", "")
            to = f"Market ({side})"
    elif ttype in {"deposit", "genesis"}:
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
        "time": datetime.fromtimestamp(tx.get("time", 0) / 1000),
        "action_type": ttype,
        "from": tx.get("user", "").lower(),
        "to": to.lower(),
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

def process_wallet(address: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    hype = usdc = memecoins = 0.0
    txn_amounts = []
    avg_amounts = []
    max_txn_value_usd = 0.0
    inflow_usd = 0.0
    outflow_usd = 0.0
    token_totals = {}
    txn_times = []
    special_transfers = {label: 0.0 for label in SPECIAL_ADDRESSES.values()}

    for txn in transactions:
        token = str(txn.get("token", "")).upper().split(":")[0].strip()
        amount_raw = txn.get("amount", "").strip()
        action_type = txn.get("action_type", "")
        ts = txn.get("time")

        try:
            amt = float(amount_raw)
        except (ValueError, TypeError):
            amt = 0.0

        usd_val = amt * PRICES.get(token, 0)

        if token == "HYPE":
            hype += amt
        elif token == "USDC":
            usdc += amt
        elif token in MEMECOINS:
            memecoins += amt

        txn_amounts.append(amt)

        if action_type in {"spotSend", "order"} and amt > 0:
            avg_amounts.append(amt)

        max_txn_value_usd = max(max_txn_value_usd, usd_val)

        if action_type in {"deposit", "genesis"}:
            inflow_usd += usd_val
        elif action_type == "cWithdraw":
            outflow_usd += usd_val

        token_totals[token] = token_totals.get(token, 0) + usd_val

        if ts:
            txn_times.append(ts)

        # Check both FROM and TO for special address
        for addr_hex, label in SPECIAL_ADDRESSES.items():
            if txn["from"] == addr_hex.lower() or txn["to"] == addr_hex.lower():
                special_transfers[label] += usd_val

    staking = get_staking_info(address)
    net_staked = staking["net_staked"]
    staking_rewards = staking["delegation_rewards"]

    total_hype = hype + net_staked
    total_aum = round(total_hype * PRICES.get("HYPE", 0) + usdc * PRICES.get("USDC", 0), 2)

    for token, usd_value in token_totals.items():
        if token not in {"HYPE", "USDC"}:
            total_aum += usd_value

    avg_txn = round(sum(avg_amounts) / len(avg_amounts), 2) if avg_amounts else 0.0

    if len(txn_times) > 1:
        times_sorted = sorted(txn_times)
        diffs = [(t2 - t1).total_seconds() / 60 for t1, t2 in zip(times_sorted[:-1], times_sorted[1:])]
        avg_diff = sum(diffs) / len(diffs)
        txn_freq = f"Every {round(avg_diff)} min"
    else:
        txn_freq = "N/A"

    capital_flow = "Positive" if inflow_usd > outflow_usd else "Negative" if inflow_usd < outflow_usd else "Neutral"
    top_token = max(token_totals.items(), key=lambda x: x[1])[0] if token_totals else "N/A"

    return {
        "wallet": address,
        "total_aum": total_aum,
        "hype": round(hype, 2),
        "usdc": round(usdc, 2),
        "memecoins": round(memecoins, 2),
        "net_staked": round(net_staked, 2),
        "staking_rewards": round(staking_rewards, 2),
        "avg_txn_amt": avg_txn,
        "max_txn_usd": round(max_txn_value_usd, 2),
        "total_inflow": round(inflow_usd, 2),
        "total_outflow": round(outflow_usd, 2),
        "txn_frequency": txn_freq,
        "general_flow": capital_flow,
        "token_with_max_transfer": top_token,
        **{f"to_or_from_{label}": round(value, 2) for label, value in special_transfers.items()}
    }

async def main():
    print("🚀 Starting wallet processing...")
    wallet_data = await fetch_all_wallets()
    print("✅ Data fetched. Processing...")

    results = []
    for wallet, txs in wallet_data.items():
        results.append(process_wallet(wallet, txs))

    for r in results:
        print(f"{r['wallet']} | AUM: ${r['total_aum']} | Inflow: ${r['total_inflow']} | Outflow: ${r['total_outflow']} | Freq: {r['txn_frequency']} | Top Token: {r['token_with_max_transfer']}")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Finished. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
