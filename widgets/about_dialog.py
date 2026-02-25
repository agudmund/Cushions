#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Cushions - widgets/about_dialog.py
# The cozy beautiful stuff
# Built using a single shared braincell by Yours Truly and Grok

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
import webbrowser

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Cushions 🌱")
        self.setFixedSize(500, 380)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(18)

        # Title with extra fluff
        title = QLabel("Cushions in context!")
        title.setFont(QFont("Lato", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        tagline = QLabel("And other cozy times.")
        tagline.setFont(QFont("Lato", 20))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #8a7a67;")
        layout.addWidget(tagline)

        version = QLabel("0.0.1 — The Fluff Era 🌸 February 2026")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #8a7a67; font-size: 13px;")
        layout.addWidget(version)

        layout.addSpacing(8)

        braincell = QLabel("Built using a single shared braincell 💕")
        braincell.setFont(QFont("Segoe UI Emoji", 16, QFont.Bold))
        braincell.setAlignment(Qt.AlignCenter)
        braincell.setStyleSheet("color: #d4b99f;")
        layout.addWidget(braincell)

        credits = QLabel(
            "by Yours Truly & Grok"
        )
        credits.setAlignment(Qt.AlignCenter)
        credits.setWordWrap(True)
        credits.setStyleSheet("color: #8a7a67; font-size: 13px; line-height: 1.5;")
        layout.addWidget(credits)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        github_btn = QPushButton("🌐 Visit GitHub")
        github_btn.clicked.connect(
            lambda: webbrowser.open("https://github.com/agudmund/Cushions")
        )

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        for btn in (github_btn, close_btn):
            btn.setFixedHeight(42)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #6b5a47;
                    border-radius: 8px;
                    color: #e0e0e0;
                    padding: 0 24px;
                }
                QPushButton:hover { background-color: #444444; }
            """)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)