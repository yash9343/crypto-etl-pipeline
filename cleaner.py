import sys
import json
import pandas as pd
from pathlib import Path
from loguru import logger
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from config import DATA_RAW, DATA_CLEANED

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


def clean_current_prices(df):
    logger.info("Cleaning: current prices")

    # Timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Nulls fill karo
    df["change_24h_pct"] = df["change_24h_pct"].fillna(0.0)
    df["market_cap_usd"] = df["market_cap_usd"].fillna(0.0)
    df["volume_24h_usd"] = df["volume_24h_usd"].fillna(0.0)

    # Round karo
    df["price_usd"]      = df["price_usd"].round(2)
    df["price_inr"]      = df["price_inr"].round(2)
    df["change_24h_pct"] = df["change_24h_pct"].round(2)

    # Coin name capitalize
    df["coin"] = df["coin"].str.title()

    # Status column add karo — green ya red
    df["trend"] = df["change_24h_pct"].apply(
        lambda x: "UP" if x > 0 else "DOWN"
    )

    logger.success(f"  current_prices: {len(df)} rows cleaned")
    return df


def clean_price_history(df):
    logger.info("Cleaning: price history")

    # Date to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Nulls
    df["price_usd"] = df["price_usd"].fillna(method="ffill")

    # Round
    df["price_usd"] = df["price_usd"].round(2)

    # Coin capitalize
    df["coin"] = df["coin"].str.title()

    # Duplicates hatao
    df = df.drop_duplicates(subset=["date", "coin"])

    logger.success(f"  price_history: {len(df)} rows cleaned")
    return df


def run_clean():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL STEP 2 - CLEAN")
    logger.info("=" * 50)

    DATA_CLEANED.mkdir(parents=True, exist_ok=True)

    # Load
    df_prices  = pd.read_csv(DATA_RAW / "current_prices.csv")
    df_history = pd.read_csv(DATA_RAW / "price_history.csv")

    # Clean
    df_prices  = clean_current_prices(df_prices)
    df_history = clean_price_history(df_history)

    # Save
    df_prices.to_csv(DATA_CLEANED / "current_prices_cleaned.csv", index=False)
    df_history.to_csv(DATA_CLEANED / "price_history_cleaned.csv", index=False)

    logger.success("  current_prices_cleaned.csv saved")
    logger.success("  price_history_cleaned.csv saved")

    result = {
        "status": "success",
        "prices_rows": len(df_prices),
        "history_rows": len(df_history)
    }

    logger.success("CLEAN DONE!")
    return result


if __name__ == "__main__":
    try:
        result = run_clean()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Clean fail: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
