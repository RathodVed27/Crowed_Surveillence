"""
logging_config.py
---------------------------------------------------------
AI Crowd Surveillance System — Enterprise Logging Service
Configures production-grade RotatingFileHandler with automatic
log rotation (max 10MB per file, 7 backups) and console stream output.
---------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_file: str = "logs/surveillance.log", level: int = logging.INFO) -> logging.Logger:
    """
    Initializes root logging with RotatingFileHandler and StreamHandler.
    Creates log directory automatically if not present.
    Prevents duplicate file handlers for the same log path.
    """
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create log dir {log_dir}: {e}")

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Add Console Stream Handler if not present
    has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler) for h in root_logger.handlers)
    if not has_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 2. Check if RotatingFileHandler for this specific file is already attached
    abs_log_path = os.path.abspath(log_file)
    has_file_handler = any(
        isinstance(h, RotatingFileHandler) and os.path.abspath(getattr(h, "baseFilename", "")) == abs_log_path
        for h in root_logger.handlers
    )

    if not has_file_handler:
        try:
            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=7,
                encoding="utf-8"
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not attach file handler for {log_file}: {e}")

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified component name.
    """
    return logging.getLogger(name)
