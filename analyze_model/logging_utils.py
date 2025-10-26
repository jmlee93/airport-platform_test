"""Shared logging helpers for CLI, web app, and scheduler."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


AUDIT_LOG_NAME = "audit.log"
ERROR_LOG_NAME = "errors.log"


def configure_logging(log_dir: Path, verbose: bool = False) -> logging.Logger:
    """Configure and return an audit logger."""

    log_dir.mkdir(parents=True, exist_ok=True)
    audit_path = log_dir / AUDIT_LOG_NAME
    error_path = log_dir / ERROR_LOG_NAME

    logger = logging.getLogger("analyze_model.audit")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        audit_handler = RotatingFileHandler(audit_path, maxBytes=1024 * 1024, backupCount=5)
        audit_handler.setFormatter(formatter)
        logger.addHandler(audit_handler)

        error_logger = logging.getLogger("analyze_model.error")
        error_logger.setLevel(logging.WARNING)
        error_logger.propagate = False
        error_handler = RotatingFileHandler(error_path, maxBytes=1024 * 1024, backupCount=5)
        error_handler.setFormatter(formatter)
        error_logger.addHandler(error_handler)

    return logger


def get_error_logger() -> logging.Logger:
    return logging.getLogger("analyze_model.error")


__all__ = ["configure_logging", "get_error_logger", "AUDIT_LOG_NAME", "ERROR_LOG_NAME"]
