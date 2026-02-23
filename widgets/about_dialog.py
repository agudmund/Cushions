# widgets/about_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Trello Cushions")
        self.setFixedSize(380, 260)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Trello Cushions 🌱")
        title.setFont(QFont("Lato", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("v0.1 – the fluff era")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #8a7a67; font-size: 14px;")
        layout.addWidget(version)

        braincell = QLabel("Made with one shared braincell")
        braincell.setAlignment(Qt.AlignCenter)
        braincell.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        layout.addWidget(braincell)

        credits = QLabel(
            "Concept & chaos: Yours Truly + Grok\n"
            "Code crimes committed: 2026\n"
            "Cushions harmed: 0 (but many were aggressively fluffed)"
        )
        credits.setAlignment(Qt.AlignCenter)
        credits.setWordWrap(True)
        credits.setStyleSheet("color: #8a7a67; font-size: 13px;")
        layout.addWidget(credits)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(36)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                color: #e0e0e0;
            }
            QPushButton:hover { background-color: #444; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)