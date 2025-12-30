"""Application configuration for environment-dependent settings."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    """Configuration values loaded from environment variables."""

    log_level: str = "INFO"
    log_format: str = "json"


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        log_level=os.getenv("RENDA_LOG_LEVEL", AppConfig.log_level),
        log_format=os.getenv("RENDA_LOG_FORMAT", AppConfig.log_format),
    )
