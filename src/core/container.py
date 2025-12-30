"""Simple dependency container for the application."""

from __future__ import annotations

import logging
from typing import NamedTuple

from .app import AppCoordinator
from .config import AppConfig, load_config
from .logging import configure_logging
from ..domain.clicker import ClickerController
from ..infra.hotkey_service import HotkeyService
from ..infra.settings import SettingsRepository
from ..ui.main_window import MainWindow


class AppContainer(NamedTuple):
    """Hold core application components."""

    config: AppConfig
    window: MainWindow
    coordinator: AppCoordinator


def build_container() -> AppContainer:
    """Construct the application components."""
    config = load_config()
    configure_logging(config)
    logger = logging.getLogger("renda-chan")

    settings_repo = SettingsRepository()
    window = MainWindow(settings_repo)
    clicker = ClickerController()

    holder: dict[str, AppCoordinator] = {}

    def on_trigger() -> None:
        coordinator = holder.get("coordinator")
        if coordinator is not None:
            coordinator.toggle_clicking()

    hotkey_service = HotkeyService(on_trigger)
    coordinator = AppCoordinator(
        window=window,
        clicker=clicker,
        hotkey_service=hotkey_service,
        logger=logger,
    )
    holder["coordinator"] = coordinator
    return AppContainer(config=config, window=window, coordinator=coordinator)
