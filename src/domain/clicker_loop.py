"""Domain click loop logic independent from UI framework."""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable


@dataclass(frozen=True)
class ClickBackend:
    """Callable wrapper for executing a click action."""

    click: Callable[[], None]
    name: str


class ClickLoop:
    """Click loop that can run on any thread."""

    def __init__(
        self,
        backend: ClickBackend,
        stop_event: threading.Event | None = None,
        wait: Callable[[float], bool] | None = None,
    ) -> None:
        self._backend = backend
        self._stop_event = stop_event or threading.Event()
        self._wait = wait or self._stop_event.wait

    def run(self, interval_ms: int) -> None:
        """Run the click loop until stopped."""
        if interval_ms <= 0:
            raise ValueError("interval_ms must be positive")

        self._stop_event.clear()
        interval_s = interval_ms / 1000.0
        while not self._stop_event.is_set():
            self._backend.click()
            if self._wait(interval_s):
                break

    def stop(self) -> None:
        """Request the click loop to stop."""
        self._stop_event.set()
