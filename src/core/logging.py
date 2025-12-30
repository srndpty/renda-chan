"""Logging configuration and structured formatter."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from dataclasses import asdict
from typing import Any

from .config import AppConfig


class JsonFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _resolve_level(level: str) -> int:
    normalized = level.strip().upper()
    if not normalized:
        return logging.INFO
    return logging._nameToLevel.get(normalized, logging.INFO)


def configure_logging(config: AppConfig) -> None:
    """Configure structured logging based on application config."""
    handler = logging.StreamHandler()
    if config.log_format.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            )
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(_resolve_level(config.log_level))

    logging.getLogger(__name__).debug("Logging configured", extra={"config": _config_map(config)})


def _config_map(config: AppConfig) -> Mapping[str, str]:
    return {key: str(value) for key, value in asdict(config).items()}
