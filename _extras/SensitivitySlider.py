
class SensitivitySlider(QWidget):
    """Small horizontal slider in bottom-right for zoom sensitivity"""
    def __init__(self, view: PanZoomGraphicsView, parent=None):
        super().__init__(parent)
        self.view = view
        self.setFixedSize(160, 30)
        self.setStyleSheet("""
            QWidget { background: transparent; }
            QSlider::groove:horizontal {
                background: #3a3a3a;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6b5a47;
                border: 1px solid #8a7a67;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #8a7a67;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Zoom Sens.")
        label.setStyleSheet("color: #8a7a67; font-size: 11px;")
        layout.addWidget(label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 20)  # 0.0001 to 0.002
        self.slider.setValue(5)      # default 0.0005
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)

        self.value_label = QLabel("0.0005")
        self.value_label.setStyleSheet("color: #8a7a67; font-size: 11px;")
        layout.addWidget(self.value_label)

    def on_slider_changed(self, value):
        sensitivity = value * 0.0001
        self.view.zoom_sensitivity = sensitivity
        self.value_label.setText(f"{sensitivity:.4f}")

