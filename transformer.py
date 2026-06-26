import sys
import json
import pandas as pd
from pathlib import Path
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_CLEANED, DATA_TRANSFORMED

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


def price_summary(df_prices):
    logger.info("Transforming: price summary")
    df = df_prices.copy()
    df["price_inr_formatted"] = df["price_inr"].apply(lambda x: f"₹{x:,.2f}")
    df["price_usd_formatted"] = df["price_usd"].apply(lambda x: f"")
    df["trend_emoji"] = df["trend"].apply(lambda x: "📈" if x == "UP" else "📉")
    logger.success(f"  price_summary: {len(df)} rows")
    return df


def weekly_trend(df_history):
    logger.info("Transforming: weekly trend")
    df = df_history.copy()
    df["date"] = pd.to_datetime(df["date"])

    result = []
    for coin in df["coin"].unique():
        coin_df = df[df["coin"] == coin].sort_values("date")
        if len(coin_df) >= 2:
            first_price = coin_df.iloc[0]["price_usd"]
            last_price  = coin_df.iloc[-1]["price_usd"]
            change_pct  = round(((last_price - first_price) / first_price) * 100, 2)
            result.append({
                "coin"          : coin,
                "price_7d_ago"  : first_price,
                "price_today"   : last_price,
                "change_7d_pct" : change_pct,
                "trend_7d"      : "UP" if change_pct > 0 else "DOWN"
            })

    logger.success(f"  weekly_trend: {len(result)} coins")
    return pd.DataFrame(result)


def top_performer(df_prices):
    logger.info("Transforming: top performer")
    df = df_prices.copy()
    df = df.sort_values("change_24h_pct", ascending=False)
    logger.success(f"  top_performer: ranked {len(df)} coins")
    return df[["coin", "price_usd", "change_24h_pct", "trend"]].reset_index(drop=True)


def run_transform():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL STEP 3 - TRANSFORM")
    logger.info("=" * 50)

    DATA_TRANSFORMED.mkdir(parents=True, exist_ok=True)

    df_prices  = pd.read_csv(DATA_CLEANED / "current_prices_cleaned.csv")
    df_history = pd.read_csv(DATA_CLEANED / "price_history_cleaned.csv")

    transforms = {
        "price_summary" : price_summary(df_prices),
        "weekly_trend"  : weekly_trend(df_history),
        "top_performers": top_performer(df_prices),
    }

    for name, df in transforms.items():
        df.to_csv(DATA_TRANSFORMED / f"{name}.csv", index=False)
        logger.success(f"  {name}.csv saved - {len(df)} rows")

    result = {
        "status"         : "success",
        "transforms_done": len(transforms)
    }

    logger.success("TRANSFORM DONE!")
    return result


if __name__ == "__main__":
    try:
        result = run_transform()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Transform fail: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
