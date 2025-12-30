"""Main application window UI."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Compact main window for click interval configuration."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Renda-chan")

        central = QWidget()
        self.setCentralWidget(central)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60_000)
        self.interval_spin.setValue(100)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.hotkey_label = QLabel("未設定")
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.hotkey_button = QPushButton("設定")

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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

        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(6)
        status_row.addWidget(self.status_label, 1)
        form_layout.addRow("状態", status_row)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)
        root_layout.addLayout(form_layout)

        self.set_running(False)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def set_running(self, running: bool) -> None:
        """Update status label based on running state."""
        if running:
            self.status_label.setText("実行中")
        else:
            self.status_label.setText("停止中")

    def set_hotkey_text(self, text: str) -> None:
        """Update hotkey display text."""
        self.hotkey_label.setText(text)
