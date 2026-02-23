# dialogs/settings_dialog.py
import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

from utils.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings ⚙")
        self.setFixedSize(420, 340)
        self.setMinimumSize(420, 340)
        self.setMaximumSize(420, 340)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        layout.setSizeConstraint(QLayout.SetFixedSize)  # lock layout

        # Project root for relative path resolution
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # ── App Icon Section ────────────────────────────────────────────
        app_title = QLabel("App Window Icon")
        app_title.setFont(QFont("Lato", 14, QFont.Bold))
        app_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_title)

        layout.addSpacing(6)

        self.app_status = QLabel("No custom icon set")
        self.app_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        self.app_status.setAlignment(Qt.AlignCenter)
        self.app_status.setWordWrap(True)
        layout.addWidget(self.app_status)

        app_preview_container = QWidget()
        app_preview_container.setFixedSize(32, 32)
        app_preview_layout = QVBoxLayout(app_preview_container)
        app_preview_layout.setContentsMargins(0, 0, 0, 0)

        self.app_preview = QLabel()
        self.app_preview.setFixedSize(32, 32)
        self.app_preview.setAlignment(Qt.AlignCenter)
        app_preview_layout.addWidget(self.app_preview)

        layout.addWidget(app_preview_container, alignment=Qt.AlignCenter)

        app_browse = QPushButton("Choose Icon")
        app_browse.setFixedHeight(36)
        app_browse.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        app_browse.clicked.connect(self.choose_app_icon)
        layout.addWidget(app_browse)

        app_reset = QPushButton("Reset")
        app_reset.setFixedHeight(28)
        app_reset.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #4a3a2f;
                border-radius: 6px;
                color: #a08a7a;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333;
                color: #e0e0e0;
            }
        """)
        app_reset.clicked.connect(lambda: self.reset_icon("icon_path", self.app_status, self.app_preview))
        layout.addWidget(app_reset)

        layout.addSpacing(20)

        # ── Bullet Icon Section ─────────────────────────────────────────
        bullet_title = QLabel("Feature List Bullet Icon")
        bullet_title.setFont(QFont("Lato", 14, QFont.Bold))
        bullet_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(bullet_title)

        layout.addSpacing(6)

        self.bullet_status = QLabel("Using default")
        self.bullet_status.setStyleSheet("color: #8a7a67; font-size: 13px;")
        self.bullet_status.setAlignment(Qt.AlignCenter)
        self.bullet_status.setWordWrap(True)
        layout.addWidget(self.bullet_status)

        bullet_preview_container = QWidget()
        bullet_preview_container.setFixedSize(32, 32)
        bullet_preview_layout = QVBoxLayout(bullet_preview_container)
        bullet_preview_layout.setContentsMargins(0, 0, 0, 0)

        self.bullet_preview = QLabel()
        self.bullet_preview.setFixedSize(32, 32)
        self.bullet_preview.setAlignment(Qt.AlignCenter)
        bullet_preview_layout.addWidget(self.bullet_preview)

        layout.addWidget(bullet_preview_container, alignment=Qt.AlignCenter)

        bullet_browse = QPushButton("Choose Icon")
        bullet_browse.setFixedHeight(36)
        bullet_browse.setStyleSheet(app_browse.styleSheet())
        bullet_browse.clicked.connect(self.choose_bullet_icon)
        layout.addWidget(bullet_browse)

        bullet_reset = QPushButton("Reset")
        bullet_reset.setFixedHeight(28)
        bullet_reset.setStyleSheet(app_reset.styleSheet())
        bullet_reset.clicked.connect(lambda: self.reset_icon("bullet_icon_path", self.bullet_status, self.bullet_preview))
        layout.addWidget(bullet_reset)

        layout.addStretch()  # pushes content up

    def _get_absolute_path(self, rel_path: str) -> str:
        if not rel_path:
            return ""
        return os.path.normpath(os.path.join(self.project_root, rel_path))

    def _refresh_statuses(self):
        # App icon
        rel_path = Settings.get("icon_path")
        if rel_path:
            abs_path = self._get_absolute_path(rel_path)
            if os.path.exists(abs_path):
                self.app_status.setText(os.path.basename(abs_path))
                pix = QPixmap(abs_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.app_preview.setPixmap(pix)
                return
        self.app_status.setText("No custom icon")
        self.app_preview.clear()

        # Bullet icon
        rel_path = Settings.get("bullet_icon_path")
        if rel_path:
            abs_path = self._get_absolute_path(rel_path)
            if os.path.exists(abs_path):
                self.bullet_status.setText(os.path.basename(abs_path))
                pix = QPixmap(abs_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.bullet_preview.setPixmap(pix)
                return
        self.bullet_status.setText("Using default")
        self.bullet_preview.clear()

    def choose_app_icon(self):
        start_dir = Settings.get_directory("last_dir_icon")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select App Icon", start_dir, "Icons (*.ico *.png *.jpg *.jpeg)"
        )
        if not path or not os.path.exists(path):
            return

        try:
            rel_path = os.path.relpath(path, self.project_root).replace("\\", "/")
            self.parent().setWindowIcon(QIcon(path))
            Settings.set("icon_path", rel_path)
            last_dir_rel = os.path.relpath(os.path.dirname(path), self.project_root).replace("\\", "/")
            Settings.set("last_dir_icon", last_dir_rel)
            self._refresh_statuses()
            QMessageBox.information(self, "Success", "App icon updated 🛋️")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not set icon:\n{str(e)}")

    def choose_bullet_icon(self):
        start_dir = Settings.get_directory("last_dir_bullet") or Settings.get_directory("last_dir_icon") or ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Bullet Icon", start_dir, "Images (*.png *.ico *.jpg *.jpeg)"
        )
        if not path or not os.path.exists(path):
            return

        try:
            pix = QPixmap(path)
            if pix.isNull():
                raise ValueError("Invalid image")

            rel_path = os.path.relpath(path, self.project_root).replace("\\", "/")
            Settings.set("bullet_icon_path", rel_path)
            last_dir_rel = os.path.relpath(os.path.dirname(path), self.project_root).replace("\\", "/")
            Settings.set("last_dir_bullet", last_dir_rel)
            self._refresh_statuses()
            QMessageBox.information(self, "Success", "Bullet icon updated!\n(Re-open feature list to see changes)")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not set bullet icon:\n{str(e)}")

    def reset_icon(self, key: str, status_label: QLabel, preview: QLabel):
        Settings.set(key, None)
        if key == "icon_path":
            status_label.setText("No custom icon")
        else:
            status_label.setText("Using default")
        preview.clear()