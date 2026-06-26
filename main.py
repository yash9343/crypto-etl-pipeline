import sys
import json
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")

def run():
    logger.info("=" * 50)
    logger.info("CRYPTO ETL PIPELINE — START")
    logger.info("=" * 50)

    logger.info("\n🔵 STEP 1 — EXTRACT")
    from extract.extract import run_extract
    r1 = run_extract()
    logger.success(f"Extract done — {r1['coins']} coins fetched")

    logger.info("\n🟡 STEP 2 — CLEAN")
    from transform.cleaner import run_clean
    r2 = run_clean()
    logger.success(f"Clean done!")

    logger.info("\n🟣 STEP 3 — TRANSFORM")
    from transform.transformer import run_transform
    r3 = run_transform()
    logger.success(f"Transform done — {r3['transforms_done']} insights")

    logger.info("\n🔴 STEP 4 — LOAD")
    from load.loader import run_load
    r4 = run_load()
    logger.success(f"Load done — {r4['total_rows']} rows MySQL mein")

    logger.info("\n📊 STEP 5 — DASHBOARD UPDATE")
    import subprocess, sys as _sys
    subprocess.run([_sys.executable, "dashboard.py"])
    logger.success("Dashboard updated!")

    logger.info("\n" + "=" * 50)
    logger.success("CRYPTO ETL COMPLETE!")
    logger.info("=" * 50)

    return {"status": "success"}

if __name__ == "__main__":
    try:
        result = run()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline fail: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
