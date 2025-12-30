"""Click automation worker executed outside the UI thread."""

from __future__ import annotations

from importlib import import_module, util
from typing import Optional

from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot

from .clicker_loop import ClickBackend, ClickLoop


def resolve_click_backend() -> ClickBackend:
    """Select an available click backend (pynput preferred, fallback to pyautogui)."""
    if util.find_spec("pynput") is not None:
        mouse_module = import_module("pynput.mouse")
        controller = mouse_module.Controller()
        button = mouse_module.Button.left
        return ClickBackend(
            click=lambda: controller.click(button),
            name="pynput",
        )

    if util.find_spec("pyautogui") is not None:
        pyautogui = import_module("pyautogui")
        return ClickBackend(
            click=pyautogui.click,
            name="pyautogui",
        )

    raise RuntimeError("pynput または pyautogui のいずれかをインストールしてください。")


class ClickerWorker(QObject):
    """Background worker that executes clicks at a fixed interval."""

    started = pyqtSignal(int, str)
    stopped = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, backend: Optional[ClickBackend] = None) -> None:
        super().__init__()
        self._backend = backend or resolve_click_backend()
        self._loop = ClickLoop(self._backend)

    @pyqtSlot(int)
    def start(self, interval_ms: int) -> None:
        """Start clicking on the worker thread."""
        if interval_ms <= 0:
            self.error.emit("クリック間隔は 1ms 以上を指定してください。")
            return

        self.started.emit(interval_ms, self._backend.name)
        try:
            self._loop.run(interval_ms)
        except Exception as exc:  # pragma: no cover - depends on backend
            self.error.emit(str(exc))
        finally:
            self.stopped.emit()

    @pyqtSlot()
    def stop(self) -> None:
        """Request the click loop to stop."""
        self._loop.stop()


class ClickerController(QObject):
    """Controller that manages the clicker worker thread."""

    started = pyqtSignal(int, str)
    stopped = pyqtSignal()
    error = pyqtSignal(str)

    request_start = pyqtSignal(int)
    request_stop = pyqtSignal()

    def __init__(self, backend: Optional[ClickBackend] = None) -> None:
        super().__init__()
        self._thread = QThread()
        self._worker = ClickerWorker(backend)
        self._worker.moveToThread(self._thread)

        self.request_start.connect(self._worker.start)
        self.request_stop.connect(self._worker.stop, Qt.ConnectionType.DirectConnection)
        self._worker.started.connect(self.started)
        self._worker.stopped.connect(self._handle_stopped)
        self._worker.error.connect(self.error)

        self._thread.start()

    def start(self, interval_ms: int) -> None:
        """Emit a signal to start clicking."""
        self.request_start.emit(interval_ms)

    def stop(self) -> None:
        """Emit a signal to stop clicking."""
        self.request_stop.emit()

    def shutdown(self) -> None:
        """Stop the worker thread and release resources."""
        self.stop()
        self._thread.quit()
        self._thread.wait()

    def _handle_stopped(self) -> None:
        self.stopped.emit()
