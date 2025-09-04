import logging.config
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List


def setup_logging(
    output_to_console: bool = False,
    log_directory: str = "logs",
    backup_count: int = 7,
    log_level: str = "DEBUG",
) -> None:
    # Create logs directory if it doesn't exist
    log_path = Path(log_directory)
    try:
        log_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fallback to basic console logging
        _setup_fallback_logging(log_level)
        return

    # Generate log file name with current date
    current_date: str = datetime.now().strftime("%Y-%m-%d")
    log_filename: Path = log_path / f"log-{current_date}.log"

    # Define handlers
    handlers: List[str] = ["file"]
    if output_to_console:
        handlers.append("console")

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": (
                    "%(asctime)s | %(levelname)-8s | "
                    "%(filename)s.%(funcName)s, line %(lineno)d: "
                    "%(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": str(log_filename),
                "when": "midnight",
                "interval": 1,
                "backupCount": backup_count,
                "formatter": "detailed",
                "encoding": "utf-8",
            },
        },
        "root": {
            "handlers": handlers,
            "level": log_level,
        },
    }

    try:
        logging.config.dictConfig(logging_config)
        logger: Logger = logging.getLogger(__name__)
        logger.info(f"Logging configured successfully. Handlers: {handlers}")

    except (ValueError, TypeError):
        _setup_fallback_logging(log_level)
    except OSError:
        _setup_fallback_logging(log_level)
    except Exception:
        _setup_fallback_logging(log_level)


def _setup_fallback_logging(log_level: str) -> None:
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
        force=True,  # Override any existing handlers
    )
