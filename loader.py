import sys
import json
import pandas as pd
from pathlib import Path
from loguru import logger
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os

sys.path.append(str(Path(__file__).parent))
from config import DATA_CLEANED, DATA_TRANSFORMED, DB_CONFIG

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")

TRANSFORMED = DATA_CLEANED.parent / "transformed"

DB_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    f"?ssl_ca=/etc/ssl/certs/ca-certificates.crt"
)


def get_engine():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.success("TiDB connected!")
    return engine


def run_load():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL STEP 4 - LOAD")
    logger.info("=" * 50)

    engine = get_engine()
    total = 0

    for name in ["current_prices", "price_history"]:
        f = DATA_CLEANED / f"{name}_cleaned.csv"
        if f.exists():
            df = pd.read_csv(f, low_memory=False)
            df.to_sql(f"crypto_{name}", con=engine, if_exists="append", index=False)
            total += len(df)
            logger.success(f"  crypto_{name} — {len(df)} rows loaded")

    for name in ["price_summary", "weekly_trend", "top_performers"]:
        f = TRANSFORMED / f"{name}.csv"
        if f.exists():
            df = pd.read_csv(f, low_memory=False)
            df.to_sql(f"insight_{name}", con=engine, if_exists="replace", index=False)
            total += len(df)
            logger.success(f"  insight_{name} — {len(df)} rows loaded")

    result = {"status": "success", "total_rows": total}
    logger.success(f"LOAD DONE — {total} rows!")
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
