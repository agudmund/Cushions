import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QLabel, QFrame, QTextEdit, QPushButton, QFileDialog,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice
from PySide6.QtGui import QDrag, QFont, QShortcut, QKeySequence

class Card(QFrame):
    def __init__(self, card_id, text, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumHeight(140)
        self.setMaximumWidth(420)
        self.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ced4da; border-radius: 6px;")
        self.editor.textChanged.connect(self.update_stats)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.header = QLabel(f"¶ {card_id}")
        self.header.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(self.header)

        split_btn = QPushButton("Split Here")
        split_btn.setStyleSheet("background: #dee2e6; font-size: 11px;")
        split_btn.clicked.connect(self.split_card)
        layout.addWidget(split_btn)

        self.stats = QLabel()
        self.stats.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(self.stats)
        self.update_stats()

        self.editor = QTextEdit(text)
        self.editor.setAcceptRichText(False)
        self.editor.setFont(QFont("Segoe UI", 14))  # or "Arial", 15 — whatever you like
        self.editor.setLineWrapMode(QTextEdit.WidgetWidth)
        self.editor.setMinimumHeight(160)           # give breathing room
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.editor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setData("application/x-card-id", QByteArray(str(self.card_id).encode()))
            drag.setMimeData(mime)
            drag.setHotSpot(event.pos())
            drag.exec(Qt.MoveAction)

    def update_stats(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.stats.setText(f"{words} words • {chars} chars")

    def split_card(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            return
        selected = cursor.selectedText()
        cursor.removeSelectedText()
        new_text = selected.strip()
        if not new_text:
            return

        # Create new card with selected text
        new_card = Card(app.next_id, new_text)  # global app ref needed — see below
        # Insert after current in same column
        parent_col = self.parent()
        while not isinstance(parent_col, Column):
            parent_col = parent_col.parent()
        insert_idx = parent_col.card_layout.indexOf(self) + 1
        parent_col.card_layout.insertWidget(insert_idx, new_card)
        app.cards.append(new_card)
        app.next_id += 1


class Column(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.header = QLabel(title)
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; background: #e9ecef; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.card_layout = QVBoxLayout(self.content)
        self.card_layout.addStretch()
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-card-id"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        card_id_bytes = event.mimeData().data("application/x-card-id")
        card_id = int(bytes(card_id_bytes).decode())
        # Find the card by id (global lookup – hacky but simple)
        card = next((c for c in app.cards if c.card_id == card_id), None)
        if card:
            # Remove from old parent
            card.setParent(None)
            # Add to this column's layout (before stretch)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)
            event.acceptProposedAction()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Pile Proofreader")
        self.resize(1400, 900)
        self.cards = []           # All cards for lookup
        self.next_id = 1

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        shortcut_next = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_next.activated.connect(self.move_selected_to_next)

        self.columns = {}
        for title in ["Unread", "Reviewing", "Polished", "Done"]:
            col = Column(title)
            main_layout.addWidget(col)
            self.columns[title] = col

        # Toolbar
        toolbar = QWidget()
        tb_layout = QHBoxLayout(toolbar)
        load_btn = QPushButton("Load Text File")
        load_btn.clicked.connect(self.load_file)
        save_btn = QPushButton("Save Progress")
        save_btn.clicked.connect(self.save_state)
        export_btn = QPushButton("Export Clean Text")
        export_btn.clicked.connect(self.export_text)
        tb_layout.addWidget(load_btn)
        tb_layout.addWidget(save_btn)
        tb_layout.addWidget(export_btn)
        tb_layout.addStretch()

        

        font_label = QLabel("Card Font:")
        font_combo = QComboBox()
        # Populate with common good ones (Qt will use system-available)
        common_fonts = ["Inter", "Segoe UI", "Arial", "Roboto", "Open Sans", "Helvetica", "Georgia", "Times New Roman", "Consolas", "Courier New"]
        for f in common_fonts:
            font_combo.addItem(f)

        font_combo.setCurrentText("Segoe UI")  # or your favorite default

        def change_font():
            font_name = font_combo.currentText()
            font = QFont(font_name, 14)  # base size
            for card in self.cards:
                card.editor.setFont(font)
                card.update_stats()  # if you added the stats

        font_combo.currentIndexChanged.connect(change_font)
        # Add to toolbar layout
        tb_layout.addWidget(font_label)
        tb_layout.addWidget(font_combo)

        dock = QWidget()
        dock_layout = QVBoxLayout(dock)
        dock_layout.addWidget(toolbar)
        dock_layout.addStretch()
        main_layout.addWidget(dock)  # Wait—no, better as top bar

        # Actually put toolbar at top
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.addWidget(toolbar)
        main_layout.insertWidget(0, top_widget)  # Hack reorder

    def move_selected_to_next(self):
        # Find focused card (hacky: check which editor has focus)
        focused = QApplication.focusWidget()
        if isinstance(focused, QTextEdit):
            card = focused.parent()
            while not isinstance(card, Card):
                card = card.parent()
            if card:
                current_col = card.parent()
                while not isinstance(current_col, Column):
                    current_col = current_col.parent()
                cols = list(self.columns.values())
                idx = cols.index(current_col)
                if idx < len(cols) - 1:
                    next_col = cols[idx + 1]
                    card.setParent(None)
                    next_col.card_layout.insertWidget(next_col.card_layout.count() - 1, card)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt *.md)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if not paragraphs:
                QMessageBox.warning(self, "Oops", "No paragraphs found!")
                return

            # Clear old cards
            for col in self.columns.values():
                while self.card_layout.count() > 1:  # leave stretch
                    item = col.card_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            self.cards.clear()
            self.next_id = 1

            # Add to "Unread"
            unread = self.columns["Unread"]
            for para in paragraphs:
                card = Card(self.next_id, para)
                unread.card_layout.insertWidget(unread.card_layout.count() - 1, card)
                self.cards.append(card)
                self.next_id += 1

            QMessageBox.information(self, "Loaded", f"Split into {len(paragraphs)} cards.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_state(self):
        # Very basic: save card texts + column positions
        data = {}
        for title, col in self.columns.items():
            data[title] = []
            for i in range(col.card_layout.count() - 1):  # skip stretch
                card = col.card_layout.itemAt(i).widget()
                if card:
                    data[title].append({"id": card.card_id, "text": card.editor.toPlainText()})
        path, _ = QFileDialog.getSaveFileName(self, "Save Progress", "", "JSON (*.json)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Saved", "Progress saved!")

    def export_text(self):
        all_text = []
        for title in ["Polished", "Done"]:  # or all columns
            col = self.columns[title]
            for i in range(col.card_layout.count() - 1):
                card = col.card_layout.itemAt(i).widget()
                if card:
                    all_text.append(card.editor.toPlainText())
        if not all_text:
            QMessageBox.warning(self, "Nothing", "No polished text yet!")
            return
        out = "\n\n".join(all_text) + "\n"
        path, _ = QFileDialog.getSaveFileName(self, "Export Clean Text", "", "Text (*.txt)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(out)
            QMessageBox.information(self, "Exported", f"Saved to {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())