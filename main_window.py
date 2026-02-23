import sys
import webbrowser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QGraphicsDropShadowEffect, QToolButton, QStyle,
    QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QThread, QObject, Signal, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon, QAction

# Local modules
from utils.logging import AppLogger
from utils.trello_api import get_credentials, create_board, create_list, create_card
from utils.settings import Settings
from widgets.drop_area import CozyDropArea
from dialogs.settings_dialog import SettingsDialog
from widgets.feature_list_dialog import FeatureListDialog
from widgets.log_viewer_dialog import LogViewerDialog
from widgets.about_dialog import AboutDialog


class UploadWorker(QObject):
    """Background worker to handle API calls without freezing the UI."""
    progress_updated = Signal(int)
    total_updated = Signal(int)        # New: tells UI how many cards to expect
    status_updated = Signal(str)
    finished = Signal(int, str)
    error_occurred = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = Path(path)

    @Slot()
    def run(self):
        try:
            api_key, token = get_credentials()
            if not api_key or not token:
                self.error_occurred.emit("Trello API keys missing.")
                return

            text = self.path.read_text(encoding='utf-8').strip()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
           
            if not paragraphs:
                self.error_occurred.emit("File is empty.")
                return

            self.total_updated.emit(len(paragraphs))  # Tell UI total count for progress bar

            board_id, board_url = create_board(api_key, token)
            todo_id = create_list(api_key, token, board_id, "To Review 🌅")

            for i, para in enumerate(paragraphs, 1):
                desc = (para[:4000] + "…") if len(para) > 4000 else para
                create_card(api_key, token, todo_id, f"Note {i}", desc)
               
                self.progress_updated.emit(i)
                self.status_updated.emit(f"Uploading {i}/{len(paragraphs)}...")
                QThread.msleep(600)  # gentle UX delay so user sees cards appearing nicely

            self.finished.emit(len(paragraphs), board_url)
        except Exception as e:
            self.error_occurred.emit(str(e))


class TrelloCushionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = AppLogger.get()
        self.worker_thread = None

        self.setWindowTitle("Cushions")
        self.setFixedSize(500, 400)
        self.setWindowOpacity(0.0)

        self._init_window_icon()
        self._setup_ui()
        self._setup_tray()
        self._run_fade_in()

    def _init_window_icon(self):
        rel_path = Settings.get("icon_path")
        self.icon_path = Path(__file__).parent / (rel_path if rel_path else "icon.png")
        if self.icon_path.exists():
            self.app_icon = QIcon(str(self.icon_path))
            self.setWindowIcon(self.app_icon)
        else:
            self.app_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)

    def _setup_tray(self):
        """Sets up the system tray icon and its menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip("Cushions - Trello Uploader")

        tray_menu = QMenu()
        restore_action = QAction("Restore Window", self)
        quit_action = QAction("Quit Cushions", self)

        restore_action.triggered.connect(self.show_and_fade)
        quit_action.triggered.connect(self.quit_app)   # clean exit path

        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def quit_app(self):
        """Clean quit from tray icon (no more console-kill needed)."""
        self.logger.info("Quitting Cushions from tray")
        self.tray_icon.hide()
        QApplication.instance().quit()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_and_fade()

    def show_and_fade(self):
        """Helper to show the window with the fade animation."""
        self.showNormal()
        self.activateWindow()
        self._run_fade_in()

    def closeEvent(self, event):
        """Hide to tray instead of exiting (standard cozy behavior)."""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Cushions",
                "Still running in the background 🌱 Right-click tray to quit.",
                self.app_icon,
                2500
            )
            event.ignore()
        else:
            event.accept()

    def _setup_ui(self):
        qss_path = Path(__file__).parent / "styles.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text())

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
       
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header bar
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()

        self._add_tool_btn("📜", self.show_log, top_layout)
        self._add_tool_btn("📋", self.show_feature_list, top_layout)
        self._add_tool_btn("⚙", self.open_settings, top_layout)
        
        about_btn = self._add_tool_btn(None, self.show_about, top_layout)
        about_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))

        layout.addWidget(top_bar)

        # Title & Drop Area
        title = QLabel("Upload to Cushions")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.drop_area = CozyDropArea()
        layout.addWidget(self.drop_area)

        self.browse_btn = QPushButton("Browse File")
        self.browse_btn.setFixedHeight(40)
        self.browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_btn)

        self.status_label = QLabel("Drag or browse a .md/.txt file to start")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Soft shadow for that cozy floating feel
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        central.setGraphicsEffect(shadow)

    def _add_tool_btn(self, text, callback, layout):
        btn = QToolButton()
        if text:
            btn.setText(text)
            btn.setFont(QFont("Segoe UI Emoji", 18))
        btn.setFixedSize(40, 40)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def _run_fade_in(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    # --- Actions ---
    def open_settings(self): SettingsDialog(self).exec()
    def show_feature_list(self): FeatureListDialog(self).exec()
    def show_log(self): LogViewerDialog(self).exec()
    def show_about(self): AboutDialog(self).exec()

    def browse_file(self):
        start_dir = Settings.get_directory("last_dir_upload")
        path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, "*.txt *.md")
        if path:
            Settings.set_directory("last_dir_upload", str(Path(path).parent))
            self.process_file(path)

    def process_file(self, path):
        if self.worker_thread and self.worker_thread.isRunning():
            return
       
        self.show_and_fade()
        self.status_label.setText("Starting upload...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.setEnabled(False)

        self.worker_thread = QThread()
        self.worker = UploadWorker(path)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker.total_updated.connect(self.progress.setMaximum)
        self.worker.progress_updated.connect(self.progress.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_success)
        self.worker.error_occurred.connect(self.on_error)

        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def on_success(self, count, url):
        self.setEnabled(True)
        self.progress.setVisible(False)
        self.tray_icon.showMessage("Upload Success ✨", f"Created {count} cards on Trello!", self.app_icon, 3000)

        if QMessageBox.question(self, "Success", f"Created {count} cards!\n\nOpen the board in browser?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            webbrowser.open(url)

    def on_error(self, msg):
        self.setEnabled(True)
        self.progress.setVisible(False)
        self.logger.error(f"Upload failed: {msg}")
        QMessageBox.critical(self, "Upload Failed", msg)