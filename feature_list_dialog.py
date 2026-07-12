# widgets/feature_list_dialog.py
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

from utils.settings import Settings


class FeatureListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Features Overview")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        title = QLabel("Current cushions achievements ✨")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #8a7a67;")
        main_layout.addWidget(title)
        main_layout.addSpacing(10)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)

        # Bullet icon logic
        custom_path = Settings.get("bullet_icon_path")
        fallback_path = "assets/icons/bulletpoint.ico"

        pixmap = None
        bullet_text = None

        if custom_path and os.path.exists(custom_path):
            temp_pix = QPixmap(custom_path)
            if not temp_pix.isNull():
                pixmap = temp_pix

        if pixmap is None:
            temp_pix = QPixmap(fallback_path)
            if not temp_pix.isNull():
                pixmap = temp_pix
            else:
                bullet_text = "•"
                print("Warning: No valid bullet icon found (custom or fallback)")

        # ── The features list ── (moved here so it's defined before the loop)
        features = [
            "Dark cozy theme with soft pastel accents",
            "Drag-and-drop file area with hover feedback",
            "Browse file button",
            "Live progress bar during upload",
            "Creates new Trello board with custom name",
            "Adds paragraphs as cards in 'To Review' list",
            "Cards named 'Note N' (pretty, customizable)",
            "Truncates long descriptions to fit Trello limits",
            "Success message with 'Open now?' popup",
            "Auto-opens board in browser on confirmation",
            "Sensitivity slider for zoom drag speed (saved)",
            "Settings gear to change app icon (saved)",
            "Feature list icon (📋) to view this dialog",
            "Daily logging to trello_log_YYYY-MM-DD.txt",
            "Graceful error handling with friendly messages",
            "Made with one shared braincell (and zero regrets) 🧠💀",
            "Refuses to resize (perfection needs no opinions)",
            "Sleeps dramatically between Trello cards (0.6s of pure theater)",
            "Has a heart icon with perfect alpha (no jagged edges allowed)",
            "Opens an About box that proudly confesses it was made with literally one shared braincell",
            "Logs its own existence with zero irony",
            "Log viewer now has real-time search/filter (type to find messages instantly)",
        ]

        for feature in features:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(10)

            bullet_label = QLabel()
            bullet_label.setFixedSize(28, 28)
            bullet_label.setAlignment(Qt.AlignCenter)

            if pixmap and not pixmap.isNull():
                scaled = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                bullet_label.setPixmap(scaled)
            else:
                bullet_label.setText(bullet_text or "•")
                bullet_label.setStyleSheet("font-size: 18px; color: #8a7a67;")

            row_layout.addWidget(bullet_label)

            text_label = QLabel(feature)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("font-size: 13px;")
            row_layout.addWidget(text_label)

            row_layout.addStretch()

            content_layout.addWidget(row_widget)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)