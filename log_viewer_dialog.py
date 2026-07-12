# widgets/log_viewer_dialog.py
import os

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTextBrowser,
    QSlider,
    QLineEdit,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from utils.logging import AppLogger


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = AppLogger.get()

        self.setWindowTitle("Today's Log 📜")
        self.setFixedSize(720, 520)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Left side: path + search + text + refresh
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Current log file path indicator
        self.path_label = QLabel()
        self.path_label.setStyleSheet("color: #666; font-size: 11px;")
        self.path_label.setWordWrap(True)
        left_layout.addWidget(self.path_label)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter messages… (type to search)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #4a3a2f;
                border-radius: 6px;
                padding: 8px 10px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #8a7a67;
            }
        """)
        self.search_input.textChanged.connect(self.debounce_filter)
        left_layout.addWidget(self.search_input)

        # Log content area
        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 11))
        self.log_display.setStyleSheet("""
            QTextBrowser {
                background: #222;
                color: #e0e0e0;
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;  /* hide native scrollbar – using custom slider */
            }
        """)
        left_layout.addWidget(self.log_display, stretch=1)

        # Refresh button
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setFixedHeight(32)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 6px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        refresh_btn.clicked.connect(self.load_log_content)
        left_layout.addWidget(refresh_btn)

        main_layout.addWidget(left_container, stretch=1)

        # Right side: custom vertical slider
        slider_container = QWidget()
        slider_container.setFixedWidth(40)
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 10, 0, 10)
        slider_layout.setSpacing(0)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setInvertedAppearance(True)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #3a3a3a;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }
            QSlider::handle:vertical {
                background: #6b5a47;
                border: 1px solid #8a7a67;
                height: 18px;
                width: 18px;
                margin: -6px -6px -6px -6px;
                border-radius: 9px;
            }
            QSlider::handle:vertical:hover {
                background: #8a7a67;
            }
        """)
        self.slider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.slider, stretch=1)

        main_layout.addWidget(slider_container)

        # State
        self.full_content = ""
        self.lines = []
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self._apply_filter_now)

        # Scroll synchronization
        self.log_display.verticalScrollBar().valueChanged.connect(self.update_slider_from_text)
        self.log_display.document().contentsChanged.connect(self.update_slider_range)

        # Initial load
        QTimer.singleShot(0, self.load_log_content)

    def load_log_content(self):
        log_path = self.logger.get_today_log_path()
        self.path_label.setText(f"Log: {os.path.basename(log_path)}")

        if not os.path.exists(log_path):
            msg = (
                "No entries logged today yet.\n\n"
                "Nothing has happened yet — or the cushions are still very quiet ☕"
            )
            self.log_display.setPlainText(msg)
            self.full_content = ""
            self.lines = []
            self.update_slider_range()
            return

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            self.full_content = content
            self.lines = content.splitlines()
            self.log_display.setPlainText(content)

            # Auto-scroll to bottom on fresh load
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )

        except Exception:
            self.logger.exception("Failed to read today's log file")
            error_text = (
                "Could not read the log file.\n\n"
                "Check the console/log for details or try refreshing."
            )
            self.log_display.setPlainText(error_text)
            self.full_content = ""
            self.lines = []

        self.update_slider_range()
        self._apply_filter_now()

    def update_slider_range(self):
        max_scroll = self.log_display.verticalScrollBar().maximum()
        self.slider.setRange(0, max_scroll if max_scroll > 0 else 100)
        # Stay at bottom if we were already there
        if self.slider.value() in (0, self.slider.maximum()):
            self.slider.setValue(self.slider.maximum())

    def on_slider_changed(self, value):
        self.log_display.verticalScrollBar().setValue(value)

    def update_slider_from_text(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

    def debounce_filter(self):
        self.filter_timer.start(200)

    def _apply_filter_now(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            self.log_display.setPlainText(self.full_content)
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )
            self.update_slider_range()
            return

        filtered_lines = [
            f">> {line}" for line in self.lines if search_text in line.lower()
        ]

        if filtered_lines:
            self.log_display.setPlainText("\n".join(filtered_lines))
        else:
            self.log_display.setPlainText(
                f'No matches for "{search_text}"\n\nTry a different term…'
            )

        self.log_display.verticalScrollBar().setValue(0)
        self.update_slider_range()