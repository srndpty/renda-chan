"""Main application window UI."""

from __future__ import annotations

from typing import Final

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..infra.settings import AppSettings, SettingsRepository
from .hotkey_capture import HotkeyCaptureFilter

_STYLE_RUNNING: Final[str] = "color: #15803d; font-weight: 700;"
_STYLE_STOPPED: Final[str] = "color: #b91c1c; font-weight: 700;"
_STYLE_MUTED: Final[str] = "color: #6b7280;"


class MainWindow(QMainWindow):
    """Compact main window for click interval configuration."""

    hotkey_changed = pyqtSignal(str)

    def __init__(self, settings_repo: SettingsRepository) -> None:
        super().__init__()
        self.setWindowTitle("renda-chan")

        central = QWidget()
        self.setCentralWidget(central)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60_000)
        self.interval_spin.setValue(100)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.interval_spin.setSingleStep(10)
        self.interval_spin.setFixedWidth(120)

        self.hotkey_label = QLabel("未設定")
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.hotkey_label.setStyleSheet(_STYLE_MUTED)
        self.hotkey_button = QPushButton("設定")
        self.hotkey_hint_label = QLabel()
        self.hotkey_hint_label.setStyleSheet(_STYLE_MUTED)
        self.hotkey_hint_label.setVisible(False)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(6)
        form_layout.setVerticalSpacing(4)
        form_layout.addRow("クリック間隔", self.interval_spin)

        hotkey_row = QHBoxLayout()
        hotkey_row.setContentsMargins(0, 0, 0, 0)
        hotkey_row.setSpacing(6)
        hotkey_row.addWidget(self.hotkey_label, 1)
        hotkey_row.addWidget(self.hotkey_button)
        form_layout.addRow("開始/停止ホットキー", hotkey_row)
        form_layout.addRow("", self.hotkey_hint_label)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(6)
        status_row.addWidget(self.status_label, 1)
        form_layout.addRow("状態", status_row)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)
        root_layout.addLayout(form_layout)

        self._capturing_hotkey = False
        self.start_stop_hotkey = ""
        self._settings_repo = settings_repo
        self._hotkey_capture = HotkeyCaptureFilter(self)
        self._hotkey_capture.hotkey_captured.connect(self._handle_hotkey_captured)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self._hotkey_capture)

        self._apply_settings(self._settings_repo.load())

        self.hotkey_button.clicked.connect(self._toggle_hotkey_capture)
        self.interval_spin.valueChanged.connect(self._handle_interval_changed)

        self.set_running(False)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def set_running(self, running: bool) -> None:
        """Update status label based on running state."""
        if running:
            self.status_label.setText("実行中")
            self.status_label.setStyleSheet(_STYLE_RUNNING)
        else:
            self.status_label.setText("停止中")
            self.status_label.setStyleSheet(_STYLE_STOPPED)

    def set_hotkey_text(self, text: str) -> None:
        """Update hotkey display text."""
        text = text.strip()
        if not text:
            self.hotkey_label.setText("未設定")
            self.hotkey_label.setStyleSheet(_STYLE_MUTED)
            return
        self.hotkey_label.setText(text)
        self.hotkey_label.setStyleSheet("")

    def _toggle_hotkey_capture(self) -> None:
        if self._capturing_hotkey:
            self._stop_hotkey_capture()
            return
        self._start_hotkey_capture()

    def _start_hotkey_capture(self) -> None:
        self._capturing_hotkey = True
        self.hotkey_hint_label.setText("次のキー入力を割り当てます")
        self.hotkey_hint_label.setVisible(True)
        self.hotkey_button.setText("キャンセル")
        self._hotkey_capture.start()

    def _stop_hotkey_capture(self) -> None:
        self._capturing_hotkey = False
        self.hotkey_hint_label.setVisible(False)
        self.hotkey_hint_label.setText("")
        self.hotkey_button.setText("設定")
        self._hotkey_capture.stop()

    def _handle_hotkey_captured(self, sequence: QKeySequence) -> None:
        text = sequence.toString(QKeySequence.SequenceFormat.NativeText)
        self.start_stop_hotkey = text
        self.set_hotkey_text(text)
        self._save_settings()
        self._stop_hotkey_capture()
        self.hotkey_changed.emit(text)

    def _apply_settings(self, settings: AppSettings) -> None:
        self.interval_spin.setValue(settings.interval_ms)
        self.start_stop_hotkey = settings.start_stop_hotkey
        self.set_hotkey_text(settings.start_stop_hotkey)

    def _current_settings(self) -> AppSettings:
        return AppSettings(
            interval_ms=self.interval_spin.value(),
            start_stop_hotkey=self.start_stop_hotkey,
        )

    def current_interval_ms(self) -> int:
        """Return the current click interval in milliseconds."""
        return self.interval_spin.value()

    def current_hotkey(self) -> str:
        """Return the currently configured hotkey string."""
        return self.start_stop_hotkey

    def _save_settings(self) -> None:
        self._settings_repo.save(self._current_settings())

    def _handle_interval_changed(self, value: int) -> None:
        _ = value
        self._save_settings()
