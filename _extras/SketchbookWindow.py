class SketchbookWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Sketchbook 🌱📝")
        self.resize(1400, 900)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#282828")))

        self.add_background_texture()

        self.view = PanZoomGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.sensitivity_slider = SensitivitySlider(self.view, self)
        self.sensitivity_slider.move(self.width() - 180, self.height() - 40)
        self.sensitivity_slider.show()

        def on_resize(e):
            self.sensitivity_slider.move(self.width() - 180, self.height() - 40)
        self.resizeEvent = on_resize

        self.scene.setSceneRect(-2000, -2000, 4000, 4000)

        sample_texts = [
            "The morning light spilled through the cracked window like spilled honey.",
            "She whispered secrets to the plants, convinced they were listening.",
            "Sometimes silence is the loudest thing in the room.",
            "He collected moments the way others collect stamps.",
            "The old book smelled of dust and forgotten summers.",
            "Rain tapped gently on the roof like fingers drumming a lullaby.",
            "She folded the letter carefully, as if it held the weight of promises.",
            "The garden waited patiently for someone to remember its name.",
            "He smiled at the chaos, knowing beauty hides in the mess.",
            "Words danced on the page, shy at first, then bold and free.",
            "The tea grew cold, but the conversation stayed warm.",
            "Every crease in the paper told a story she hadn't yet written."
        ]

        for i in range(15):
            angle = radians(random.uniform(0, 360))
            distance = random.uniform(150, 800)
            x = distance * cos(angle)
            y = distance * sin(angle)

            text = random.choice(sample_texts)
            node = WarmNode(i + 1, text, QPointF(x, y))
            self.scene.addItem(node)

        self.view.centerOn(0, 0)

    def add_background_texture(self):
        """Procedural faint paper grain + scattered tiny leaves/dots"""
        tile_size = 512
        pixmap = QPixmap(tile_size, tile_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Faint paper grain (white noise dots)
        for _ in range(8000):
            x = random.uniform(0, tile_size)
            y = random.uniform(0, tile_size)
            radius = random.uniform(0.5, 1.5)
            opacity = random.randint(4, 12)
            painter.setPen(QPen(QColor(255, 255, 255, opacity)))
            painter.drawEllipse(QPointF(x, y), radius, radius)

        # Scattered tiny leaves/dots (muted green)
        for _ in range(100):
            x = random.uniform(0, tile_size)
            y = random.uniform(0, tile_size)
            size = random.uniform(6, 14)
            angle = random.uniform(0, 360)
            opacity = random.randint(5, 12)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(90, 160, 110, opacity)))
            painter.drawEllipse(QPointF(x, y), size * 0.6, size)

            # Stem
            painter.setPen(QPen(QColor(70, 120, 90, opacity), 1.5))
            end_x = x + size * 0.4 * cos(radians(angle))
            end_y = y + size * 0.4 * sin(radians(angle))
            painter.drawLine(int(x), int(y), int(end_x), int(end_y))

        painter.end()

        brush = QBrush(pixmap)
        brush.setStyle(Qt.TexturePattern)
        self.scene.setBackgroundBrush(brush)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SketchbookWindow()
    window.show()
    sys.exit(app.exec())
