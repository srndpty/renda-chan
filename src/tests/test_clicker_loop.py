from __future__ import annotations

import threading

import pytest

from ..domain.clicker_loop import ClickBackend, ClickLoop


def test_click_loop_runs_until_wait_requests_stop() -> None:
    clicks: list[str] = []
    stop_event = threading.Event()

    def wait(_: float) -> bool:
        stop_event.set()
        return True

    loop = ClickLoop(
        ClickBackend(click=lambda: clicks.append("click"), name="test"),
        stop_event=stop_event,
        wait=wait,
    )

    loop.run(10)

    assert clicks == ["click"]
    assert stop_event.is_set()


def test_click_loop_stop_ends_running_loop() -> None:
    clicks: list[str] = []
    stop_event = threading.Event()

    def wait(_: float) -> bool:
        return stop_event.wait(0)

    loop = ClickLoop(
        ClickBackend(click=lambda: clicks.append("click"), name="test"),
        stop_event=stop_event,
        wait=wait,
    )
    thread = threading.Thread(target=loop.run, args=(1,))

    thread.start()
    loop.stop()
    thread.join(timeout=1)

    assert stop_event.is_set()
    assert not thread.is_alive()
    assert clicks


def test_click_loop_rejects_non_positive_interval() -> None:
    loop = ClickLoop(ClickBackend(click=lambda: None, name="test"))

    with pytest.raises(ValueError, match="interval_ms must be positive"):
        loop.run(0)
