"""Pipeline logging setup."""
import logging
from pathlib import Path


def get_logger(log_dir="reports"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("yottaflex_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(Path(log_dir) / "pipeline.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    return logger
