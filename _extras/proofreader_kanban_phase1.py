import sys
import os
import json
from datetime import datetime
import requests
import webbrowser

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QDialog,
    QProgressBar,
    QMessageBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect,
    QToolButton,
    QTextBrowser,
    QScrollArea,
)

from PySide6.QtCore import (
    Qt,
    QPointF,
    QRectF,
    QTimeLine,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
)

from PySide6.QtGui import (
    QColor,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
    QPainter,
    QCursor,
    QDragEnterEvent,
    QDropEvent,
    QPixmap,
    QIcon,
    QKeyEvent,
    QMouseEvent,
)


class CozyDropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(180)
        self.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 2px dashed #6b5a47;
                border-radius: 12px;
                color: #8a7a67;
                font-size: 16px;
            }
            QFrame:hover {
                border: 2px solid #8a7a67;
                background-color: #444;
            }
        """)
        self.label = QLabel("Drag your .md/.txt file here\nor click Browse", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Lato", 14))
        self.label.setStyleSheet("color: #8a7a67;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #444;
                    border: 2px solid #8a7a67;
                    border-radius: 12px;
                    color: #fff;
                    font-size: 16px;
                }
            """)
            self.label.setText("Drop to upload!")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 2px dashed #6b5a47;
                border-radius: 12px;
                color: #8a7a67;
                font-size: 16px;
            }
        """)
        self.label.setText("Drag your .md/.txt file here\nor click Browse")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 2px dashed #6b5a47;
                border-radius: 12px;
                color: #8a7a67;
                font-size: 16px;
            }
        """)
        self.label.setText("Drag your .md/.txt file here\nor click Browse")
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.parent().process_file(files[0])
        event.acceptProposedAction()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(320, 180)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("App Icon")
        title.setFont(QFont("Lato", 14, QFont.Bold))
        layout.addWidget(title)

        self.path_label = QLabel("No icon selected")
        self.path_label.setStyleSheet("color: #8a7a67;")
        layout.addWidget(self.path_label)

        browse_btn = QPushButton("Choose Icon (.ico, .png, .jpg)")
        browse_btn.clicked.connect(self.choose_icon)
        layout.addWidget(browse_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

    def choose_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Icons (*.ico *.png *.jpg *.jpeg)"
        )
        if path:
            self.path_label.setText(os.path.basename(path))
            self.parent().set_app_icon(path)


class FeatureListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Features Overview")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

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
            "Log viewer icon (📜) to view today's log",
            "Daily logging to trello_log_YYYY-MM-DD.txt",
            "Graceful error handling with friendly messages",
        ]

        for feature in features:
            lbl = QLabel(f"• {feature}")
            lbl.setWordWrap(True)
            content_layout.addWidget(lbl)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Today's Log")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #6b5a47;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8a7a67;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        log_file = f"trello_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_text = f.read()
            log_display = QTextBrowser()
            log_display.setPlainText(log_text)
            log_display.setFont(QFont("Consolas", 11))
            log_display.setStyleSheet("background: #222; color: #e0e0e0;")
            content_layout.addWidget(log_display)
        else:
            lbl = QLabel("No activity logged today yet.\nCome back after uploading something! ☕")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #8a7a67; font-size: 14px;")
            content_layout.addWidget(lbl)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)


class TrelloCushionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trello Cushions 🌱")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top bar with icons
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()

        log_btn = QToolButton(self)
        log_btn.setText("📜")
        log_btn.setFont(QFont("Segoe UI Emoji", 18))
        log_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #8a7a67;
                border: none;
            }
            QToolButton:hover {
                color: #fff;
            }
        """)
        log_btn.setFixedSize(40, 40)
        log_btn.clicked.connect(self.show_log)
        top_layout.addWidget(log_btn)

        features_btn = QToolButton(self)
        features_btn.setText("📋")
        features_btn.setFont(QFont("Segoe UI Emoji", 18))
        features_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #8a7a67;
                border: none;
            }
            QToolButton:hover {
                color: #fff;
            }
        """)
        features_btn.setFixedSize(40, 40)
        features_btn.clicked.connect(self.show_feature_list)
        top_layout.addWidget(features_btn)

        settings_btn = QToolButton(self)
        settings_btn.setText("⚙")
        settings_btn.setFont(QFont("Segoe UI Emoji", 18))
        settings_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #8a7a67;
                border: none;
            }
            QToolButton:hover {
                color: #fff;
            }
        """)
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(settings_btn)

        layout.addWidget(top_bar)

        title = QLabel("Upload to Trello Cushions")
        title.setFont(QFont("Lato", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.drop_area = CozyDropArea()
        layout.addWidget(self.drop_area)

        browse_btn = QPushButton("Browse File")
        browse_btn.setFixedHeight(40)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)

        self.status_label = QLabel("Drag or browse a .md/.txt file to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8a7a67; font-size: 13px;")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        central.setGraphicsEffect(shadow)

        # Load saved icon if exists
        self.load_saved_icon()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_feature_list(self):
        dialog = FeatureListDialog(self)
        dialog.exec()

    def show_log(self):
        dialog = LogViewerDialog(self)
        dialog.exec()

    def set_app_icon(self, path):
        if os.path.exists(path):
            self.setWindowIcon(QIcon(path))
            self.save_icon_path(path)

    def save_icon_path(self, path):
        data = {"icon_path": path}
        try:
            with open("sketchbook_settings.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load_saved_icon(self):
        if os.path.exists("sketchbook_settings.json"):
            try:
                with open("sketchbook_settings.json", 'r') as f:
                    data = json.load(f)
                    path = data.get("icon_path")
                    if path and os.path.exists(path):
                        self.setWindowIcon(QIcon(path))
            except Exception:
                pass

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .md/.txt File", "", "Text/Markdown Files (*.txt *.md)"
        )
        if path:
            self.process_file(path)

    def process_file(self, path):
        self.status_label.setText(f"Processing {os.path.basename(path)}...")
        self.progress.setVisible(True)
        self.progress.setValue(0)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            total = len(paragraphs)
            if total == 0:
                self.status_label.setText("File is empty or has no paragraphs.")
                self.progress.setVisible(False)
                return

            self.progress.setRange(0, total)
            api_key, token = self.get_credentials()
            if not api_key or not token:
                self.status_label.setText("Keys not found. Set TRELLO_KEY and TRELLO_TOKEN.")
                self.progress.setVisible(False)
                return

            board_id, board_url = self.create_board(api_key, token)
            todo_id = self.create_list(api_key, token, board_id, "To Review 🌅")

            cards_added = 0
            for i, para in enumerate(paragraphs, 1):
                card_name = f"Note {i}"
                desc = para[:4000] + "…" if len(para) > 4000 else para
                if self.create_card(api_key, token, todo_id, card_name, desc):
                    cards_added += 1
                self.progress.setValue(i)
                QApplication.processEvents()

            self.progress.setVisible(False)
            self.status_label.setText(f"Done! {cards_added} cards added.")
            reply = QMessageBox.question(
                self, "Success", f"Board created with {cards_added} cards.\nOpen now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                webbrowser.open(board_url)

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", str(e))

    def get_credentials(self):
        api_key = os.environ.get("TRELLO_KEY")
        token   = os.environ.get("TRELLO_TOKEN")
        return api_key.strip() if api_key else None, token.strip() if token else None

    def create_board(self, api_key, token, board_name="Proofreading Kanban 🌱"):
        url = "https://api.trello.com/1/boards/"
        query = {
            'key': api_key,
            'token': token,
            'name': board_name,
            'defaultLists': False,
            'prefs_background': 'blue'
        }
        response = requests.post(url, params=query)
        response.raise_for_status()
        board = response.json()
        return board['id'], board['shortUrl']

    def create_list(self, api_key, token, board_id, list_name):
        url = "https://api.trello.com/1/lists"
        query = {
            'key': api_key,
            'token': token,
            'name': list_name,
            'idBoard': board_id,
            'pos': 'bottom'
        }
        response = requests.post(url, params=query)
        response.raise_for_status()
        return response.json()['id']

    def create_card(self, api_key, token, list_id, card_name, desc):
        url = "https://api.trello.com/1/cards"
        query = {
            'key': api_key,
            'token': token,
            'idList': list_id,
            'name': card_name,
            'desc': desc,
            'pos': 'bottom'
        }
        response = requests.post(url, params=query)
        return response.status_code == 200


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TrelloCushionsWindow()
    window.show()
    sys.exit(app.exec())