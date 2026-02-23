from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SensitivitySlider(QWidget):
    """Cozy Polish Sensitivity slider — Gentle Nudge ↔ Deep Rewrite 🌿
    Emits the current level (0.0–1.0) so WarmNodes can listen later."""
    
    sensitivityChanged = Signal(float)  # 0.0 = gentle, 1.0 = deep

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 55)
        
        # Warm woodsy styling that matches the main app
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                color: #8a7a67;
                font-family: "Segoe UI", sans-serif;
            }
            QSlider::groove:horizontal {
                background: #3a3a3a;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #6b5a47;
                border: 2px solid #8a7a67;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #8a7a67;
            }
            QSlider::sub-page:horizontal {
                background: #6b5a47;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Top row: label + value
        top = QHBoxLayout()
        self.title_label = QLabel("Polish Sensitivity 🌿")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        top.addWidget(self.title_label)

        self.value_label = QLabel("Moderate")
        self.value_label.setFont(QFont("Segoe UI", 9))
        top.addStretch()
        top.addWidget(self.value_label)

        layout.addLayout(top)

        # The slider itself
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)          # start in the middle
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self._on_slider_moved)
        layout.addWidget(self.slider)

    def _on_slider_moved(self, value: int):
        """Update label and emit normalized 0.0–1.0 value."""
        level = value / 100.0
        self.sensitivityChanged.emit(level)

        # Friendly labels that feel like a real sketchbook
        if level < 0.25:
            text = "Gentle Nudge"
        elif level < 0.5:
            text = "Soft Polish"
        elif level < 0.75:
            text = "Moderate"
        else:
            text = "Deep Rewrite"
        self.value_label.setText(text)

    def current_level(self) -> float:
        """Convenience for WarmNodes later."""
        return self.slider.value() / 100.0