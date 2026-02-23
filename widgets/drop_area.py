# widgets/drop_area.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent


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
        self.restore_default_style()

    def dropEvent(self, event: QDropEvent):
        self.restore_default_style()
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            # Forward the first file to the parent's processing method
            self.parent().process_file(files[0])
        event.acceptProposedAction()

    def restore_default_style(self):
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