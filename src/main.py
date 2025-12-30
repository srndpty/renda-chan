"""Application entrypoint."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .core.container import build_container

APP_NAME = "renda-chan"


def main() -> int:
    """Run the desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    container = build_container()
    container.window.show()

    exit_code = app.exec()
    container.coordinator.shutdown()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())