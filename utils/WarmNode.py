import random
from PySide6.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QDialog, QVBoxLayout, QTextEdit,
    QDialogButtonBox, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import (
    QColor, QBrush, QPen, QLinearGradient, QFont
)


class CozyNoteEditor(QDialog):
    """Much larger, cozy note editor — feels like a full warm notebook page 🌱📝"""
    
    def __init__(self, node_id: int, current_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Note {node_id} 🌿")
        self.setMinimumSize(940, 680)
        self.resize(980, 740)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 2px solid #6b5a47;
                border-radius: 12px;
            }
            QLabel {
                color: #8a7a67;
                font-size: 16px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #252525;
                color: #e0e0e0;
                font-family: "Lato", "Segoe UI", sans-serif;
                font-size: 16px;
                line-height: 1.6;
                border: 1px solid #6b5a47;
                border-radius: 8px;
                padding: 20px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #6b5a47;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)
        
        header = QLabel(f"Editing Note {node_id} 🌱")
        layout.addWidget(header)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(current_text)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_text(self):
        return self.text_edit.toPlainText().strip()


class WarmNode(QGraphicsRectItem):
    """A single warm, draggable, editable text node for the proofreader sketchbook 🌿📝"""
    
    def __init__(self, node_id: int, full_text: str, pos: QPointF):
        super().__init__(QRectF(-145, -68, 290, 136))
        self.node_id = node_id
        self.full_text = full_text.strip()
        self.preview_text = self.full_text[:68] + "…" if len(self.full_text) > 68 else self.full_text
        
        self.setPos(pos)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.setTransformOriginPoint(self.rect().center())

        # Beautiful pastel card
        pastels = [
            QColor("#fae8db"), QColor("#eaf5e2"), QColor("#e5edf9"),
            QColor("#f6ebf4"), QColor("#fff8eb"), QColor("#f2ede3"),
        ]
        base_color = random.choice(pastels)
        
        gradient = QLinearGradient(0, -68, 0, 68)
        gradient.setColorAt(0.0, base_color.lighter(135))
        gradient.setColorAt(0.45, base_color)
        gradient.setColorAt(1.0, base_color.darker(115))
        self.setBrush(QBrush(gradient))

        pen = QPen()
        pen.setWidth(2.8)
        pen_gradient = QLinearGradient(-145, -68, 145, 68)
        pen_gradient.setColorAt(0, QColor(255, 255, 255, 230))
        pen_gradient.setColorAt(0.5, QColor(255, 255, 255, 90))
        pen_gradient.setColorAt(1, QColor(255, 255, 255, 25))
        pen.setBrush(QBrush(pen_gradient))
        self.setPen(pen)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setOffset(5, 9)
        shadow.setColor(QColor(35, 28, 22, 125))
        self.setGraphicsEffect(shadow)

        # Content
        emojis = ["🌿", "📝", "🍃", "🪴", "💭", "🌸", "✨", "🤗", "🍂", "🛋️", "☕"]
        self.emoji_item = QGraphicsTextItem(random.choice(emojis), self)
        self.emoji_item.setFont(QFont("Segoe UI Emoji", 29))
        self.emoji_item.setPos(-130, -58)

        self.header = QGraphicsTextItem(f"¶ {node_id}", self)
        self.header.setFont(QFont("Lato", 13, QFont.Bold))
        self.header.setDefaultTextColor(QColor("#6b5a47"))
        self.header.setPos(-108, -48)

        self.text_item = QGraphicsTextItem(self.preview_text, self)
        self.text_item.setFont(QFont("Lato", 13.5))
        self.text_item.setDefaultTextColor(QColor("#6f5f4f"))
        self.text_item.setTextWidth(235)
        self.text_item.setPos(-108, -12)

    def hoverEnterEvent(self, event):
        self.setScale(1.085)
        self.setPen(QPen(self.pen().color().lighter(135), 3.2))
        self._show_sparkle()

    def hoverLeaveEvent(self, event):
        self.setScale(1.0)
        self.setPen(QPen(self.pen().color().darker(105), 2.8))

    def _show_sparkle(self):
        """Gentle floating sparkle with proper QTimer import"""
        sparkle = QGraphicsTextItem("✨", self)
        sparkle.setFont(QFont("Segoe UI Emoji", 20))
        sparkle.setDefaultTextColor(QColor(255, 245, 180, 255))
        sparkle.setPos(95, -35)
        sparkle.setOpacity(1.0)

        def move_and_fade():
            if sparkle.scene():
                sparkle.setPos(sparkle.pos() + QPointF(8, -45))
                sparkle.setOpacity(0.3)
        
        QTimer.singleShot(80, lambda: sparkle.setPos(sparkle.pos() + QPointF(4, -20)) if sparkle.scene() else None)
        QTimer.singleShot(220, move_and_fade)
        QTimer.singleShot(650, lambda: sparkle.scene().removeItem(sparkle) if sparkle.scene() else None)

    def mouseDoubleClickEvent(self, event):
        """Open the much larger, cozy editor"""
        if event.button() == Qt.LeftButton:
            dialog = CozyNoteEditor(self.node_id, self.full_text)
            if dialog.exec() == QDialog.Accepted:
                new_text = dialog.get_text()
                if new_text and new_text != self.full_text:
                    self.full_text = new_text
                    self.preview_text = self.full_text[:68] + "…" if len(self.full_text) > 68 else self.full_text
                    self.text_item.setPlainText(self.preview_text)
        super().mouseDoubleClickEvent(event)