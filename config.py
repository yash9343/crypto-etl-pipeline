from pathlib import Path
from urllib.parse import quote_plus
import os

BASE_DIR         = Path(__file__).parent
DATA_RAW         = BASE_DIR / "data" / "raw"
DATA_CLEANED     = BASE_DIR / "data" / "cleaned"
DATA_TRANSFORMED = BASE_DIR / "data" / "transformed"

COINS         = ["bitcoin", "ethereum", "binancecoin", "solana", "cardano"]
VS_CURRENCIES = ["usd", "inr"]
API_URL       = "https://api.coingecko.com/api/v3"

DB_CONFIG = {
    "host"    : os.environ.get("DB_HOST", "127.0.0.1"),
    "port"    : int(os.environ.get("DB_PORT", 4000)),
    "database": os.environ.get("DB_NAME", "crypto_etl"),
    "user"    : os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", "1234@"),
}

DB_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    f"?ssl=true"
)
NULL_DROP_THRESHOLD = 0.60
CRITICAL_COLUMNS = {
    "orders"   : ["order_id", "customer_id"],
    "customers": ["customer_id"],
    "products" : ["product_id"],
}
