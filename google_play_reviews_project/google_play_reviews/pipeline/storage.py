from pathlib import Path
from datetime import datetime
import json
import pandas as pd

def save_run_outputs(df_raw, df_processed, run_id, config, logger):
    raw_dir = Path(config["raw_out_dir"])
    proc_dir = Path(config["processed_out_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)

    raw_out = raw_dir / f"reviews_raw_{run_id}.csv"
    proc_out = proc_dir / f"reviews_processed_{run_id}.csv"

    df_raw.to_csv(raw_out, index=False)
    df_processed.to_csv(proc_out, index=False)

    logger.info(f"[SAVE] raw={raw_out} processed={proc_out}")

    # Save small run metadata JSON (observability)
    meta = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "rows_raw": int(len(df_raw)),
        "rows_processed": int(len(df_processed)),
        "columns": list(df_processed.columns),
        "config": config,
    }
    meta_out = proc_dir / f"run_metadata_{run_id}.json"
    meta_out.write_text(json.dumps(meta, indent=2))
    logger.info(f"[SAVE] metadata={meta_out}")
