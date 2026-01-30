from datetime import datetime
from pathlib import Path
import time
import uuid

import pandas as pd
from google_play_scraper import Sort

from .scraper import scrape_reviews
from .config import PIPELINE_CONFIG
from .logging_utils import get_logger
from .processing import basic_clean
from .storage import save_run_outputs

logger = get_logger()

SORT_MODES = {
    "newest": Sort.NEWEST,
    "most_relevant": Sort.MOST_RELEVANT,
}

def run_pipeline():
    start_ts = time.time()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    logger.info(f"[RUN_START] run_id={run_id}")

    # 1) Collect (scrape) OR load data
    if PIPELINE_CONFIG.get("use_scraper", False):
        df_raw = scrape_reviews(
            app_id=PIPELINE_CONFIG["app_id"],
            lang=PIPELINE_CONFIG.get("lang", "en"),
            country=PIPELINE_CONFIG.get("country", "us"),
            target_per_mode=PIPELINE_CONFIG["target_per_mode"],
            sort_modes=SORT_MODES,
        )
        logger.info(f"[SCRAPE] rows={len(df_raw)} cols={len(df_raw.columns)}")

        # quick per-sort breakdown
        if "sort_mode" in df_raw.columns:
            counts = df_raw["sort_mode"].value_counts(dropna=False).to_dict()
            logger.info(f"[SCRAPE_BREAKDOWN] {counts}")

    else:
        input_path = Path(PIPELINE_CONFIG["input_csv"])
        if not input_path.exists():
            raise FileNotFoundError(f"Input CSV not found: {input_path}")
        df_raw = pd.read_csv(input_path)
        logger.info(f"[LOAD] rows={len(df_raw)} cols={len(df_raw.columns)} path={input_path}")

    # 2) Basic processing
    df = basic_clean(df_raw, logger=logger)

    # 3) Save outputs + run metadata
    save_run_outputs(
        df_raw=df_raw,
        df_processed=df,
        run_id=run_id,
        config=PIPELINE_CONFIG,
        logger=logger,
    )

    elapsed = time.time() - start_ts
    logger.info(f"[RUN_END] run_id={run_id} duration_sec={elapsed:.2f}")

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.exception(f"[RUN_ERROR] {e}")
        raise
