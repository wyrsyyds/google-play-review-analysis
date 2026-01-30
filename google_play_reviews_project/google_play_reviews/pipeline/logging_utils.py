import logging
from pathlib import Path
from datetime import datetime

from .config import PIPELINE_CONFIG

def get_logger() -> logging.Logger:
    logs_dir = Path(PIPELINE_CONFIG["logs_dir"])
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        ts = datetime.now().strftime("%Y%m%d")
        log_path = logs_dir / f"pipeline_{ts}.log"

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)

        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)

        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(sh)

    return logger
