import sys
import webbrowser
import json
import hashlib
import random
from pathlib import Path
from math import radians, cos, sin

from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QProgressBar, QMessageBox,
    QGraphicsScene, QComboBox, QToolButton, QStyle, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QThread, QObject, Signal, Slot, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtGui import QFont, QColor, QIcon, QAction, QPen, QBrush, QPainter, QPixmap

# Local modules
from utils.logging import AppLogger
from utils.trello_api import create_board, create_list, create_card
from utils.settings import Settings
from widgets.drop_area import CozyDropArea
from dialogs.settings_dialog import SettingsDialog
from widgets.feature_list_dialog import FeatureListDialog
from widgets.log_viewer_dialog import LogViewerDialog
from widgets.about_dialog import AboutDialog

# Sketchbook components
from utils.PanGraphicsView import PanZoomGraphicsView
from utils.WarmNode import WarmNode
from _extras.SensitivitySlider import SensitivitySlider

def get_content_hash(text):
    """Generates a unique ID based on the text content to track layout positions."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

class UploadWorker(QObject):
    """Background worker to handle API calls without freezing the UI."""
    progress_updated = Signal(int)
    total_updated = Signal(int)
    status_updated = Signal(str)
    finished = Signal(int, str)
    error_occurred = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = Path(path)

    @Slot()
    def run(self):
        try:
            api_key, token = Settings.get_trello_creds()
            if not api_key or not token:
                self.error_occurred.emit("Trello API keys missing.")
                return

            text = self.path.read_text(encoding='utf-8').strip()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            if not paragraphs:
                self.error_occurred.emit("File is empty.")
                return

            self.total_updated.emit(len(paragraphs))

            board_id, board_url = create_board(api_key, token)
            todo_id = create_list(api_key, token, board_id, "To Review 🌅")

            for i, para in enumerate(paragraphs, 1):
                # 1. Clean Markdown headers/formatting from the start
                # This removes leading #, *, -, or > (for quotes)
                clean_para = para.lstrip('#*-> ').strip()

                # 2. Extract Name from First Sentence
                # We look for . ! or ? to find the end of the first sentence
                first_period = clean_para.find('.')
                first_exclaim = clean_para.find('!')
                first_question = clean_para.find('?')
                
                stops = [pos for pos in [first_period, first_exclaim, first_question] if pos != -1]
                
                if stops:
                    end_of_sentence = min(stops) + 1
                    card_name = clean_para[:end_of_sentence].strip()
                else:
                    # Fallback: take a chunk of the first line
                    card_name = clean_para.split('\n')[0][:60].strip()
                
                # 3. Final Polish
                # Trello titles shouldn't be too long; 120 is a sweet spot for readability
                if len(card_name) > 120:
                    card_name = card_name[:117] + "..."
                
                # If for some reason the name is empty, use a fallback
                if not card_name:
                    card_name = f"Note {i}"

                # 4. Use the original 'para' for the description to keep formatting
                desc = (para[:4000] + "…") if len(para) > 4000 else para
                
                # Create the card
                create_card(api_key, token, todo_id, card_name, desc)
                
                # 5. Signal the UI (Safely!)
                self.progress_updated.emit(i)
                self.status_updated.emit(f"Created: {card_name[:30]}...")
                QThread.msleep(600)

            self.finished.emit(len(paragraphs), board_url)
        except Exception as e:
            self.error_occurred.emit(str(e))

class TrelloCushionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = AppLogger.get()
        self.worker_thread = None
        self.sketch_scene = None
        self.sketch_view = None
        self.sensitivity_slider = None
        self.action_combo = None
        self.save_btn = None
        self.sketch_title = None
        self.current_md_file = None

        self.setWindowTitle("Cushions - Warm Markdown Studio")
        self.resize(1280, 820)
        self.setMinimumSize(960, 620)
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
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip("Cushions - Trello Uploader")

        tray_menu = QMenu()
        restore_action = QAction("Restore Window", self)
        quit_action = QAction("Quit Cushions", self)
        restore_action.triggered.connect(self.show_and_fade)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def quit_app(self):
        self.logger.info("Quitting Cushions (Exit pressed)")
        self.tray_icon.hide()
        QApplication.instance().quit()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_and_fade()

    def show_and_fade(self):
        self.showNormal()
        self.activateWindow()
        self._run_fade_in()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage("Cushions", "Still running in the background 🌱 Right-click tray to quit.", self.app_icon, 2500)
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

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # LEFT PANEL
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(16)

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()
        self._add_tool_btn("📜", self.show_log, top_layout)
        self._add_tool_btn("📋", self.show_feature_list, top_layout)
        self._add_tool_btn("⚙", self.open_settings, top_layout)
        about_btn = self._add_tool_btn(None, self.show_about, top_layout)
        about_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self._add_tool_btn("🚪 Exit", self.quit_app, top_layout)
        left_layout.addWidget(top_bar)

        title = QLabel("What shall we do today?")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        self.drop_area = CozyDropArea()
        left_layout.addWidget(self.drop_area)

        self.browse_btn = QPushButton("Browse File")
        self.browse_btn.setFixedHeight(46)
        self.browse_btn.clicked.connect(self.browse_file)
        left_layout.addWidget(self.browse_btn)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Send to:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Upload to Trello 🌅", "Load into Warm Sketchbook 🌱"])
        self.action_combo.setCurrentIndex(0)
        self.action_combo.setStyleSheet("""
            QComboBox { color: #e0e0e0; background: #3a3a3a; border: 1px solid #6b5a47; border-radius: 6px; padding: 6px; }
            QComboBox:hover { background: #444444; }
            QComboBox::drop-down { border: none; }
        """)
        combo_layout.addWidget(self.action_combo)
        left_layout.addLayout(combo_layout)

        self.save_btn = QPushButton("💾 Save Edits & Layout")
        self.save_btn.clicked.connect(self._save_sketchbook_edits)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("background: #3a3a3a; color: #6b5a47; font-weight: bold; padding: 10px;")
        left_layout.addWidget(self.save_btn)

        self.status_label = QLabel("Drag or browse a .md/.txt file to start")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # RIGHT PANEL
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(6)

        self.sketch_title = QLabel("Warm Sketchbook 🌱")
        self.sketch_title.setAlignment(Qt.AlignCenter)
        self.sketch_title.setStyleSheet("color: #8a7a67; font-size: 18px; font-weight: bold; padding: 8px;")
        right_layout.addWidget(self.sketch_title)

        self.sketch_scene = QGraphicsScene(self)
        self.sketch_scene.setBackgroundBrush(QColor("#282828"))
        self.add_background_texture()

        self.sketch_view = PanZoomGraphicsView(self.sketch_scene, self)
        self.sketch_view.setMinimumWidth(720)
        right_layout.addWidget(self.sketch_view)
        main_layout.addWidget(right_panel)

        self.sensitivity_slider = SensitivitySlider(self)
        self.sensitivity_slider.setParent(self.sketch_view)
        self.sensitivity_slider.move(self.sketch_view.width() - 240, self.sketch_view.height() - 80)

        self._populate_sample_nodes()

    def _add_tool_btn(self, text, callback, layout):
        btn = QToolButton()
        if text:
            btn.setText(text)
            btn.setFont(QFont("Segoe UI Emoji", 18))
        btn.setFixedSize(65, 40)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def add_background_texture(self):
        tile_size = 512
        pixmap = QPixmap(tile_size, tile_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        for _ in range(8000):
            x = random.uniform(0, tile_size)
            y = random.uniform(0, tile_size)
            radius = random.uniform(0.5, 1.5)
            opacity = random.randint(4, 12)
            painter.setPen(QPen(QColor(255, 255, 255, opacity)))
            painter.drawEllipse(QPointF(x, y), radius, radius)

        for _ in range(100):
            x = random.uniform(0, tile_size)
            y = random.uniform(0, tile_size)
            size = random.uniform(6, 14)
            angle = random.uniform(0, 360)
            opacity = random.randint(5, 12)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(90, 160, 110, opacity)))
            painter.drawEllipse(QPointF(x, y), size * 0.6, size)
            painter.setPen(QPen(QColor(70, 120, 90, opacity), 1.5))
            end_x = x + size * 0.4 * cos(radians(angle))
            end_y = y + size * 0.4 * sin(radians(angle))
            painter.drawLine(int(x), int(y), int(end_x), int(end_y))

        painter.end()
        brush = QBrush(pixmap)
        brush.setStyle(Qt.TexturePattern)
        self.sketch_scene.setBackgroundBrush(brush)

    def _populate_sample_nodes(self):
        welcome_text = "Welcome to your Warm Sketchbook 🌱📝"
        node = WarmNode(1, welcome_text, QPointF(0, 0))
        self.sketch_scene.addItem(node)
        self.sketch_view.centerOn(0, 0)

    def _run_fade_in(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    def open_settings(self): SettingsDialog(self).exec()
    def show_feature_list(self): FeatureListDialog(self).exec()
    def show_log(self): LogViewerDialog(self).exec()
    def show_about(self): AboutDialog(self).exec()

    def browse_file(self):
        start_dir = Settings.get_directory("last_dir_upload") or str(Path.home())
        path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, "*.txt *.md")
        if path:
            Settings.set_directory("last_dir_upload", str(Path(path).parent))
            self.process_file(path)

    def process_file(self, path):
        if getattr(self, 'worker_thread', None) and self.worker_thread.isRunning():
            return
        
        self.show_and_fade()
        self.status_label.setText("Processing file...")

        if self.action_combo.currentText() == "Upload to Trello 🌅":
            self._upload_to_trello(path)
        else:
            self._load_to_sketchbook(path)

    def _upload_to_trello(self, path):
        self.status_label.setText("Starting upload to Trello...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.sketch_title.setText("Warm Sketchbook 🌱")

        self.worker_thread = QThread()
        self.worker = UploadWorker(path)
        self.worker.moveToThread(self.worker_thread)

        self.worker.total_updated.connect(self.progress.setMaximum)
        self.worker.progress_updated.connect(self.progress.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_success)
        self.worker.error_occurred.connect(self.on_error)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error_occurred.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self._cleanup_worker_thread)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def _cleanup_worker_thread(self):
        self.worker_thread = None
        self.setEnabled(True)

    def _load_to_sketchbook(self, path):
        try:
            file_path = Path(path)
            text = file_path.read_text(encoding='utf-8').strip()
            
            # Try to load existing layout from a hidden file
            layout_path = file_path.parent / f".{file_path.name}.layout.json"
            saved_layout = {}
            if layout_path.exists():
                try:
                    saved_layout = json.loads(layout_path.read_text(encoding='utf-8'))
                except Exception as e:
                    self.logger.warning(f"Could not load layout file: {e}")

            paragraphs = []
            for block in text.split('\n\n'):
                cleaned = block.strip()
                if not cleaned or not cleaned.replace('#', '').strip():
                    continue
                if cleaned.startswith('#'):
                    cleaned = cleaned.lstrip('#').strip()
                if cleaned:
                    paragraphs.append(cleaned)

            if not paragraphs:
                QMessageBox.warning(self, "Empty", "No content found after filtering.")
                return

            # Clear scene of old nodes
            for item in list(self.sketch_scene.items()):
                if isinstance(item, WarmNode):
                    self.sketch_scene.removeItem(item)

            for i, para in enumerate(paragraphs, 1):
                node_hash = get_content_hash(para)
                
                if node_hash in saved_layout:
                    # Use the saved coordinates
                    coords = saved_layout[node_hash]
                    pos = QPointF(coords[0], coords[1])
                else:
                    # Scattered Table logic for new or edited notes
                    angle = radians(random.uniform(0, 360))
                    distance = random.uniform(180, 850)
                    pos = QPointF(distance * cos(angle), distance * sin(angle))
                
                node = WarmNode(i, para, pos)
                self.sketch_scene.addItem(node)

            self.sketch_view.centerOn(0, 0)
            self.current_md_file = path
            self.save_btn.setEnabled(True)
            self.sketch_title.setText(f"Warm Sketchbook — {file_path.name}")
            self.status_label.setText(f"🌱 Loaded {len(paragraphs)} notes.")
            self.tray_icon.showMessage("Sketchbook Ready ✨", f"Arranged {len(paragraphs)} cozy cards", self.app_icon, 3000)
        except Exception as e:
            self.logger.error(str(e))
            QMessageBox.critical(self, "Load Failed", str(e))

    def _save_sketchbook_edits(self):
        if not self.current_md_file:
            return

        nodes = [item for item in self.sketch_scene.items() if isinstance(item, WarmNode)]
        nodes.sort(key=lambda n: n.node_id)

        # 1. Update text content
        new_content = '\n\n'.join(node.full_text for node in nodes)

        # 2. Build layout map { hash: [x, y] }
        layout_map = {
            get_content_hash(node.full_text): [node.pos().x(), node.pos().y()]
            for node in nodes
        }

        try:
            # Save Markdown file
            file_path = Path(self.current_md_file)
            file_path.write_text(new_content, encoding='utf-8')
            
            # Use the Settings utility to save the layout 
            # (Changed 'path' to 'self.current_md_file' here)
            Settings.save_layout(self.current_md_file, layout_map)

            self.status_label.setText("💾 Saved content and layout positions!")
            self.tray_icon.showMessage("Saved ✨", "Your changes and arrangement are safe.", self.app_icon, 3000)
        except Exception as e:
            self.logger.error(str(e))
            QMessageBox.critical(self, "Save Failed", str(e))

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TrelloCushionsWindow()
    window.show()
    sys.exit(app.exec())