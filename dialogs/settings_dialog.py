#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Cushions - dialogs/settings_dialog.py
# The cozy beautiful settings home
# Built using a single shared braincell by Yours Truly and Grok

import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QLayout,
    QWidget,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QIcon
from utils.settings import Settings
from utils.trello_api import TrelloAPI


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings ⚙️")
        self.setFixedSize(520, 520)          # slightly wider for the new side-by-side layout
        self.setMinimumSize(520, 520)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(22)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # ── Trello Credentials Section ────────────────────────────────
        trello_title = QLabel("Trello Credentials 🌅")
        trello_title.setFont(QFont("Lato", 14, QFont.Bold))
        trello_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(trello_title)

        self.trello_status = QLabel("Click Test Connection below")
        self.trello_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        self.trello_status.setAlignment(Qt.AlignCenter)
        self.trello_status.setWordWrap(True)
        layout.addWidget(self.trello_status)

        test_btn = QPushButton("Test Connection")
        test_btn.setFixedHeight(42)
        test_btn.clicked.connect(self.test_trello_connection)
        layout.addWidget(test_btn, alignment=Qt.AlignCenter)

        self._add_separator(layout)

        # ── App Icon Section ──────────────────────────────────────────
        app_row = QHBoxLayout()
        app_title = QLabel("App Window Icon")
        app_title.setFont(QFont("Lato", 14, QFont.Bold))
        app_row.addWidget(app_title)

        app_row.addStretch()

        self.app_status = QLabel("No custom icon set")
        self.app_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        app_row.addWidget(self.app_status)

        app_row.addSpacing(20)

        # Preview icon on the far right of the row
        self.app_preview = QLabel()
        self.app_preview.setFixedSize(32, 32)
        self.app_preview.setAlignment(Qt.AlignCenter)
        app_row.addWidget(self.app_preview)

        layout.addLayout(app_row)

        self._add_icon_buttons(layout, self.choose_app_icon, lambda: self.reset_icon("icon_path", self.app_status, self.app_preview))

        self._add_separator(layout)

        # ── Bullet Icon Section ───────────────────────────────────────
        bullet_row = QHBoxLayout()
        bullet_title = QLabel("Feature List Bullet Icon")
        bullet_title.setFont(QFont("Lato", 14, QFont.Bold))
        bullet_row.addWidget(bullet_title)

        bullet_row.addStretch()

        self.bullet_status = QLabel("Using default")
        self.bullet_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        bullet_row.addWidget(self.bullet_status)

        bullet_row.addSpacing(20)

        self.bullet_preview = QLabel()
        self.bullet_preview.setFixedSize(32, 32)
        self.bullet_preview.setAlignment(Qt.AlignCenter)
        bullet_row.addWidget(self.bullet_preview)

        layout.addLayout(bullet_row)

        self._add_icon_buttons(layout, self.choose_bullet_icon, lambda: self.reset_icon("bullet_icon_path", self.bullet_status, self.bullet_preview))

        layout.addStretch()

        self._refresh_statuses()

    # (the rest of the file stays exactly the same as the previous version)
    def _add_separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #333333; max-height: 1px;")
        layout.addWidget(line)

    def _add_icon_buttons(self, layout, choose_callback, reset_callback):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        browse = QPushButton("Choose Icon")
        browse.setFixedHeight(38)
        browse.clicked.connect(choose_callback)
        reset = QPushButton("Reset")
        reset.setFixedHeight(32)
        reset.clicked.connect(reset_callback)

        for btn in (browse, reset):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    border: 1px solid #6b5a47;
                    border-radius: 8px;
                    color: #e0e0e0;
                }
                QPushButton:hover { background-color: #444444; }
            """)
            if btn.text() == "Reset":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2a2a2a;
                        border: 1px solid #4a3a2f;
                        border-radius: 6px;
                        color: #a08a7a;
                    }
                    QPushButton:hover { background-color: #333333; color: #e0e0e0; }
                """)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

    def _get_absolute_path(self, rel_path: str) -> str:
        if not rel_path:
            return ""
        return os.path.normpath(os.path.join(self.project_root, rel_path))

    def _update_icon_status(self, key: str, status_label: QLabel, preview: QLabel, default_name: str, default_filename: str):
        rel_path = Settings.get(key)
        if rel_path:
            abs_path = self._get_absolute_path(rel_path)
            if os.path.exists(abs_path):
                status_label.setText(os.path.basename(abs_path))
                pix = QPixmap(abs_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                preview.setPixmap(pix)
                return

        status_label.setText(default_name)
        default_path = self._get_absolute_path(default_filename)
        if os.path.exists(default_path):
            pix = QPixmap(default_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            preview.setPixmap(pix)
        else:
            preview.clear()

    def _refresh_statuses(self):
        self._update_icon_status("icon_path", self.app_status, self.app_preview,
                                 "Using default (icon.png)", "icon.png")
        self._update_icon_status("bullet_icon_path", self.bullet_status, self.bullet_preview,
                                 "Using default (bullet.png)", "bullet.png")

        api_key, token = Settings.get_trello_creds()
        if api_key and token:
            self.trello_status.setText("Credentials saved • Ready to test")
        else:
            self.trello_status.setText("No credentials set yet")

    def choose_app_icon(self):
        start_dir = Settings.get_directory("last_dir_icon") or str(self.project_root)
        path, _ = QFileDialog.getOpenFileName(self, "Select App Icon", start_dir, "Icons (*.ico *.png *.jpg *.jpeg)")
        if not path or not os.path.exists(path):
            return
        try:
            rel_path = os.path.relpath(path, self.project_root).replace("\\", "/")
            self.parent().setWindowIcon(QIcon(path))
            Settings.set("icon_path", rel_path)
            Settings.set_directory("last_dir_icon", os.path.dirname(path))
            self._refresh_statuses()
            QMessageBox.information(self, "Success ✨", "App icon updated 🛋️")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not set icon:\n{str(e)}")

    def choose_bullet_icon(self):
        start_dir = Settings.get_directory("last_dir_bullet") or Settings.get_directory("last_dir_icon") or str(self.project_root)
        path, _ = QFileDialog.getOpenFileName(self, "Select Bullet Icon", start_dir, "Images (*.png *.ico *.jpg *.jpeg)")
        if not path or not os.path.exists(path):
            return
        try:
            rel_path = os.path.relpath(path, self.project_root).replace("\\", "/")
            Settings.set("bullet_icon_path", rel_path)
            Settings.set_directory("last_dir_bullet", os.path.dirname(path))
            self._refresh_statuses()
            QMessageBox.information(self, "Success ✨", "Bullet icon updated!\n(Re-open Feature List to see changes)")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not set bullet icon:\n{str(e)}")

    def reset_icon(self, key: str, status_label: QLabel, preview: QLabel):
        Settings.set(key, None)
        if key == "icon_path" and self.parent() and hasattr(self.parent(), '_init_window_icon'):
            self.parent()._init_window_icon()
        self._refresh_statuses()

    def test_trello_connection(self):
        try:
            TrelloAPI.from_settings()
            QMessageBox.information(
                self, "Connection Successful ✨", 
                "Trello credentials are valid and working!\n\nYou're all set to create cozy boards 🌱"
            )
            self.trello_status.setText("✅ Connected and ready")
            self.trello_status.setStyleSheet("color: #90d490;")
        except ValueError as e:
            QMessageBox.warning(self, "Connection Failed", str(e))
            self.trello_status.setText("❌ Check your keys")
            self.trello_status.setStyleSheet("color: #e07a7a;")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected issue:\n{str(e)}")