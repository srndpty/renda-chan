"""Hotkey capture event filter."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QKeySequence

_MODIFIER_KEYS = {
    Qt.Key.Key_Shift,
    Qt.Key.Key_Control,
    Qt.Key.Key_Alt,
    Qt.Key.Key_Meta,
}


class HotkeyCaptureFilter(QObject):
    """Capture the next key sequence from the event stream."""

    hotkey_captured = pyqtSignal(QKeySequence)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._capturing = False

    def start(self) -> None:
        self._capturing = True

    def stop(self) -> None:
        self._capturing = False

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
        if not self._capturing:
            return super().eventFilter(obj, event)
        if event is None or event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(obj, event)

        key_event = event if isinstance(event, QKeyEvent) else None
        if key_event is None or key_event.isAutoRepeat():
            return True

        sequence = self._sequence_from_event(key_event)
        if sequence is None:
            return True

        self._capturing = False
        self.hotkey_captured.emit(sequence)
        return True

    @staticmethod
    def _sequence_from_event(event: QKeyEvent) -> QKeySequence | None:
        key = event.key()
        if key in _MODIFIER_KEYS or key == Qt.Key.Key_unknown:
            return None
        return QKeySequence(event.keyCombination())
