# config.py

import json

# RPC URLs
RPC_URLS = {
    "HYPERLIQUID": "https://rpc.hyperliquid.xyz/explorer"
}

# Main coins with their prices
MAIN_TOKENS = {
    "HYPE": 41.684,
    "USDC": 1.0
}

# Memecoins with their prices (known or set to 0.0)
MEMECOIN_PRICES = {
    "ADHD": 0.0, "ANSEM": 0.0, "ARI": 0.0, "ASI": 0.0, "ATEHUN": 0.0, "AUTIST": 0.0,
    "BAGS": 0.0, "BEATS": 0.0, "BERA": 0.002902, "BID": 0.0, "BIGBEN": 0.0, "BOZO": 0.0,
    "BUBZ": 0.0, "BUDDY": 0.0, "BUSSY": 0.0, "CAPPY": 0.0, "CAT": 0.0, "CATBAL": 0.0,
    "CATNIP": 0.0, "CHEF": 0.0, "CHINA": 0.0, "COPE": 0.0, "COZY": 0.0, "CZ": 0.0,
    "DROP": 0.0, "FARM": 0.0, "FARMED": 0.0, "FATCAT": 0.0, "FEUSD": 0.0, "FLASK": 0.0,
    "FLY": 0.0, "FRAC": 0.0, "FRIED": 0.0, "FRUDO": 0.0, "FUCKY": 0.0, "FUN": 0.0,
    "FUND": 0.0, "GENESY": 0.0, "GMEOW": 0.0, "GPT": 0.0, "GUP": 0.0, "H": 0.0,
    "HBOOST": 0.0, "HFUN": 0.0, "HODL": 0.0, "HOP": 0.0, "HOPE": 0.0, "HPEPE": 0.0,
    "HPUMP": 0.0, "HPYH": 0.0, "HWTR": 0.0, "HYENA": 0.0, "ILIENS": 0.0, "JEET": 0.0,
    "JEFF": 0.0, "JPEG": 0.0, "KOBE": 0.0, "LADY": 0.0, "LAUNCH": 0.042081, "LICK": 0.0,
    "LICKO": 0.000611, "LIQD": 0.0, "LIQUID": 0.0, "LORA": 0.0, "LQNA": 0.0, "LUCKY": 0.0,
    "MAGA": 0.0, "MANLET": 0.0, "MBAPPE": 0.0, "MEOW": 0.001547, "MOG": 0.0, "MONAD": 0.0,
    "MUNCH": 0.00004542, "NASDAQ": 0.0, "NEIRO": 0.0007504, "NEKO": 0.0, "NFT": 0.0,
    "NMTD": 0.0, "NOCEX": 0.0, "OMNIX": 0.0, "PANDA": 0.0, "PEAR": 0.0005517, "PEPE": 0.0,
    "PIGEON": 0.0, "PILL": 0.0, "PIP": 0.0, "POINTS": 0.0, "PURR": 0.0, "PURRPS": 0.0,
    "RAGE": 0.0, "RANK": 0.0, "RAT": 0.0, "RETARD": 0.0, "RICH": 0.0, "RIP": 0.0,
    "RISE": 0.0, "RUG": 0.0, "SCHIZO": 0.0, "SELL": 0.0, "SENT": 0.0, "SPH": 0.0,
    "STACK": 0.0, "STAR": 0.0, "STEEL": 0.0, "STRICT": 0.0, "SUCKY": 0.0, "SYLVI": 0.0,
    "TATE": 0.0, "TEST": 0.0, "TIME": 0.0, "TJIF": 0.0, "TRUMP": 0.0, "UBTC": 0.0,
    "UETH": 0.0, "UFART": 0.0, "UP": 0.0, "USDE": 0.0, "USDHL": 0.0, "USDT0": 0.0,
    "USDXL": 0.0, "USOL": 0.0, "VAULT": 0.055293, "VAPOR": 0.0, "VEGAS": 0.0, "WAGMI": 0.0,
    "WASH": 0.0, "WHYPI": 0.0, "WOW": 0.00045663, "XAUT0": 0.0, "XULIAN": 0.0,
    "YAP": 0.0, "YEETI": 0.0
}

# Path to wallet address file
WALLET_FILE = "wallets.txt"

# Output CSV file name
OUTPUT_CSV = "100_wallets.csv"

# Global alias map (loaded from JSON file)
def load_alias_map(path="globalAliases.json"):
    try:
        with open(path) as f:
            data = json.load(f)
            return {k.lower(): v for k, v in data.items()}
    except Exception as e:
        print(f"⚠️ Failed to load alias map from {path}: {e}")
        return {}

WALLET_ALIAS_MAP = load_alias_map()

