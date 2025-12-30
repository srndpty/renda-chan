"""Persistent application settings storage."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QSettings


@dataclass(frozen=True)
class AppSettings:
    """Application settings persisted between launches."""

    interval_ms: int = 100
    start_stop_hotkey: str = ""


class SettingsRepository:
    """Read and write persisted settings via QSettings."""

    _INTERVAL_KEY = "interval_ms"
    _HOTKEY_KEY = "start_stop_hotkey"

    def __init__(self) -> None:
        self._settings = QSettings("renda-chan", "renda-chan")

    def load(self) -> AppSettings:
        """Load settings from persistent storage."""
        interval_ms = self._settings.value(self._INTERVAL_KEY, AppSettings.interval_ms, type=int)
        hotkey = self._settings.value(self._HOTKEY_KEY, "", type=str)
        if not isinstance(interval_ms, int) or interval_ms <= 0:
            interval_ms = AppSettings.interval_ms
        if not isinstance(hotkey, str):
            hotkey = ""
        return AppSettings(interval_ms=interval_ms, start_stop_hotkey=hotkey)

    def save(self, settings: AppSettings) -> None:
        """Persist settings to storage."""
        self._settings.setValue(self._INTERVAL_KEY, settings.interval_ms)
        self._settings.setValue(self._HOTKEY_KEY, settings.start_stop_hotkey)
