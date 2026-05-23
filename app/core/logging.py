from __future__ import annotations

import logging
import os


def get_logger(name: str = "cyberify_kb") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    )

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
