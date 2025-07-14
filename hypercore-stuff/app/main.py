import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio
from app.api import fetch_all_wallets
from app.parser import process_wallet
from app.db import setup_database, insert_wallet_analysis
from app.logger import get_logger

logger = get_logger(__name__)

def load_wallet_addresses(wallet_file='wallets.txt'):
    with open(wallet_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

async def process_and_store_wallet(wallet, transactions, hype_price, usdc_price):
    if transactions:
        processed = process_wallet(wallet, transactions, hype_price, usdc_price)
        if processed:
            insert_wallet_analysis(processed)
            logger.info(f"✅ Successfully processed and stored data for {wallet}")
        else:
            logger.warning(f"⚠️ No processed data for wallet {wallet}")
    else:
        logger.warning(f"⚠️ No transactions found for wallet {wallet}")

async def run():
    logger.info("🚀 Quartermaster started.")
    setup_database()

    # 👉 Define your hype price here
    hype_price = 39.60  # You can replace this with dynamic pricing if needed
    usdc_price = 1.0

    # Fetch all wallets and their transactions
    by_wallet_data = await fetch_all_wallets()

    tasks = [
        process_and_store_wallet(wallet, transactions, hype_price, usdc_price)
        for wallet, transactions in by_wallet_data.items()
    ]

    for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Processing wallets"):
        await f

    logger.info("✅ Data processing completed.")

if __name__ == "__main__":
    asyncio.run(run())
