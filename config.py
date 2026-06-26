from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR     = Path(r"C:\Users\Yash Admin\Documents\Crypto ETL")
DATA_RAW     = BASE_DIR / "data" / "raw"
DATA_CLEANED = BASE_DIR / "data" / "cleaned"
DATA_TRANSFORMED = BASE_DIR / "data" / "transformed"

COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "cardano"]
VS_CURRENCIES = ["usd", "inr"]

API_URL = "https://api.coingecko.com/api/v3"

DB_CONFIG = {
    "host"    : "127.0.0.1",
    "port"    : 3306,
    "database": "crypto_etl",
    "user"    : "root",
    "password": "Root@1234",
}

DB_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
