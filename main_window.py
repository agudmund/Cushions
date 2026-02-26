from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from utils.logging import setup_logging   # we'll grab the logger here


class NodalTester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nodal-tester")
        self.setWindowTitle("Nodal Tester")
        self.resize(600, 500)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ── Canvas page ───────────────────────────────────────────────
        self.page_canvas = QWidget()
        layout_canvas = QVBoxLayout(self.page_canvas)
        layout_canvas.setContentsMargins(20, 20, 20, 20)
        layout_canvas.setSpacing(15)

        # Big friendly placeholder
        self.placeholder_label = QLabel(
            "Canvas Area\n(preview will appear here soon)\n\nReady when you are! ✨"
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("font-size: 24px; color: #aaaaff;")
        layout_canvas.addWidget(self.placeholder_label, stretch=1)  # ← pushes buttons down

        # Bottom bar with Exit button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()  # ← pushes button to the right

        exit_btn = QPushButton("Exit")
        exit_btn.setFixedWidth(120)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9999;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7777;
            }
        """)
        exit_btn.clicked.connect(self.quit_app)
        bottom_layout.addWidget(exit_btn)

        layout_canvas.addLayout(bottom_layout)

        self.stack.addWidget(self.page_canvas)
        self.show_canvas()  # start on canvas

    def show_canvas(self):
        self.stack.setCurrentWidget(self.page_canvas)
        self.setWindowTitle("Nodal Tester – Canvas")

    def quit_app(self):
        self.logger.info("Quitting Nodal Tester (Exit pressed) 🌙")
        # If we ever add a system tray icon, we would hide it here:
        # self.tray_icon.hide()   # ← commented for now, add later if needed
        QApplication.instance().quit()