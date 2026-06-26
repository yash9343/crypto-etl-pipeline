import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_RAW, COINS

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


def fetch_current_prices():
    logger.info("Fetching current prices...")
    coins_str = ",".join(COINS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coins_str}&vs_currencies=usd,inr&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_7day_history(coin):
    logger.info(f"Fetching 7 day history: {coin}")
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=7&interval=daily"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def run_extract():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL STEP 1 - EXTRACT")
    logger.info("=" * 50)

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Current prices
    prices = fetch_current_prices()
    rows = []
    for coin, data in prices.items():
        rows.append({
            "timestamp"     : timestamp,
            "coin"          : coin,
            "price_usd"     : data.get("usd"),
            "price_inr"     : data.get("inr"),
            "market_cap_usd": data.get("usd_market_cap"),
            "volume_24h_usd": data.get("usd_24h_vol"),
            "change_24h_pct": data.get("usd_24h_change"),
        })

    df_prices = pd.DataFrame(rows)
    df_prices.to_csv(DATA_RAW / "current_prices.csv", index=False)
    logger.success(f"Current prices saved - {len(df_prices)} coins")

    # 7 day history — 15 second wait between requests
    history_rows = []
    for i, coin in enumerate(COINS):
        if i > 0:
            logger.info(f"  Waiting 15 seconds — rate limit avoid...")
            time.sleep(15)
        hist = fetch_7day_history(coin)
        for price_point in hist["prices"]:
            ts = datetime.fromtimestamp(price_point[0] / 1000).strftime("%Y-%m-%d")
            history_rows.append({
                "date"     : ts,
                "coin"     : coin,
                "price_usd": round(price_point[1], 2)
            })

    df_history = pd.DataFrame(history_rows)
    df_history.to_csv(DATA_RAW / "price_history.csv", index=False)
    logger.success(f"7 day history saved - {len(df_history)} rows")

    result = {
        "status"      : "success",
        "timestamp"   : timestamp,
        "coins"       : len(rows),
        "history_rows": len(history_rows)
    }

    logger.success("EXTRACT DONE!")
    return result


if __name__ == "__main__":
    try:
        result = run_extract()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Extract fail: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
