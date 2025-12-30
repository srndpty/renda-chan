"""Application coordinator wiring UI with domain services."""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import QObject

from ..domain.clicker import ClickerController
from ..infra.hotkey_service import HotkeyService
from ..ui.main_window import MainWindow


class AppCoordinator(QObject):
    """Connect UI events with domain services."""

    def __init__(
        self,
        window: MainWindow,
        clicker: ClickerController,
        hotkey_service: HotkeyService,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()
        self._window = window
        self._clicker = clicker
        self._hotkey_service = hotkey_service
        self._logger = logger or logging.getLogger(__name__)
        self._running = False

        self._window.hotkey_changed.connect(self._handle_hotkey_changed)
        self._clicker.started.connect(self._handle_clicker_started)
        self._clicker.stopped.connect(self._handle_clicker_stopped)
        self._clicker.error.connect(self._handle_clicker_error)

        self._register_hotkey(self._window.current_hotkey())

    def shutdown(self) -> None:
        """Clean up any running services."""
        self._logger.info("Shutting down application coordinator")
        self._hotkey_service.unregister()
        self._clicker.shutdown()

    def _handle_clicker_started(self, interval_ms: int, backend: str) -> None:
        self._running = True
        self._window.set_running(True)
        self._logger.info(
            "Clicker started",
            extra={"interval_ms": interval_ms, "backend": backend},
        )

    def _handle_clicker_stopped(self) -> None:
        self._running = False
        self._window.set_running(False)
        self._logger.info("Clicker stopped")

    def _handle_clicker_error(self, message: str) -> None:
        self._running = False
        self._window.set_running(False)
        self._logger.error("Clicker error: %s", message)

    def _handle_hotkey_changed(self, hotkey: str) -> None:
        self._register_hotkey(hotkey)

    def _register_hotkey(self, hotkey: str) -> None:
        try:
            self._hotkey_service.register(hotkey)
        except ValueError as exc:
            self._logger.warning("Hotkey registration failed: %s", exc)

    def toggle_clicking(self) -> None:
        """Toggle clicker start/stop based on current state."""
        if self._running:
            self._clicker.stop()
            return
        self._clicker.start(self._window.current_interval_ms())
