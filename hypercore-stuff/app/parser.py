from collections import Counter
from datetime import datetime
from app.config import MEMECOINS
from app.logger import get_logger

logger = get_logger(__name__)
from app.config import MEMECOINS

def process_wallet(address, transactions, hype_price, usdc_price):
    hype = 0
    usdc = 0
    memecoins = 0
    txn_amounts = []

    for txn in transactions:
        token = str(txn.get("token", "")).upper().split(':')[0].strip()
        try:
            amt = float(txn.get("amount", "0") or 0)
        except Exception:
            amt = 0.0

        if token == "HYPE":
            hype += amt
        elif token == "USDC":
            usdc += amt
        elif token in MEMECOINS:
            memecoins += amt

        txn_amounts.append(amt)

    total_aum = (hype * hype_price) + (usdc * usdc_price)
    avg_txn_amount = sum(txn_amounts) / len(txn_amounts) if txn_amounts else 0.0

    return {
        "wallet": address,
        "total_aum": total_aum,
        "hype_amount": hype,
        "usdc_amount": usdc,
        "memecoin_amount": memecoins,
        "average_txn_amount": avg_txn_amount
    }
