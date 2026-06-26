import sys
import json
import pandas as pd
from pathlib import Path
from loguru import logger
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_CLEANED, DATA_TRANSFORMED, DB_CONFIG

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")

DB_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


def get_engine():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.success("MySQL connected!")
    return engine


def run_load():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL STEP 4 - LOAD")
    logger.info("=" * 50)

    engine = get_engine()
    total = 0

    # Current prices — APPEND karo replace nahi!
    # Har baar naya data add hoga
    df_prices = pd.read_csv(DATA_CLEANED / "current_prices_cleaned.csv")
    df_prices.to_sql("crypto_prices", con=engine, if_exists="append", index=False)
    total += len(df_prices)
    logger.success(f"  crypto_prices — {len(df_prices)} rows INSERTED")

    # History — replace karo
    df_history = pd.read_csv(DATA_CLEANED / "price_history_cleaned.csv")
    df_history.to_sql("crypto_history", con=engine, if_exists="replace", index=False)
    total += len(df_history)
    logger.success(f"  crypto_history — {len(df_history)} rows loaded")

    # Transformed tables
    for name in ["price_summary", "weekly_trend", "top_performers"]:
        df = pd.read_csv(DATA_TRANSFORMED / f"{name}.csv")
        df.to_sql(f"insight_{name}", con=engine, if_exists="replace", index=False)
        total += len(df)
        logger.success(f"  insight_{name} — {len(df)} rows loaded")

    result = {
        "status"    : "success",
        "total_rows": total
    }

    logger.success(f"LOAD DONE — {total} rows MySQL mein!")
    return result


if __name__ == "__main__":
    try:
        result = run_load()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Load fail: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
