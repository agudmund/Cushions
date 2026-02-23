class WarmNode(QGraphicsRectItem):
    def __init__(self, node_id: int, preview_text: str, pos: QPointF):
        super().__init__(QRectF(-140, -55, 280, 110))
        self.node_id = node_id
        self.preview_text = preview_text
        self.setPos(pos)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

        pastels = [
            QColor("#fae8db"), QColor("#eaf5e2"), QColor("#e5edf9"),
            QColor("#f6ebf4"), QColor("#fff8eb"), QColor("#f2ede3"),
        ]
        base_color = random.choice(pastels)

        gradient = QLinearGradient(0, -55, 0, 55)
        gradient.setColorAt(0.0, base_color.lighter(130))
        gradient.setColorAt(0.4, base_color)
        gradient.setColorAt(1.0, base_color.darker(120))
        self.setBrush(QBrush(gradient))

        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2.5)
        pen_gradient = QLinearGradient(-140, -55, 140, 55)
        pen_gradient.setColorAt(0, QColor(255, 255, 255, 220))
        pen_gradient.setColorAt(0.5, QColor(255, 255, 255, 80))
        pen_gradient.setColorAt(1, QColor(255, 255, 255, 20))
        pen.setBrush(QBrush(pen_gradient))
        self.setPen(pen)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(26)
        shadow.setOffset(4, 8)
        shadow.setColor(QColor(40, 30, 25, 110))
        self.setGraphicsEffect(shadow)

        emojis = ["🌿", "📝", "🍃", "🪴", "💭", "🌸", "✨", "🤗", "🍂", "🛋️"]
        emoji_item = QGraphicsTextItem(random.choice(emojis), self)
        emoji_item.setFont(QFont("Segoe UI Emoji", 28))
        emoji_item.setPos(-128, -48)

        header = QGraphicsTextItem(f"¶ {node_id}", self)
        header.setFont(QFont("Lato", 13, QFont.Bold))
        header.setDefaultTextColor(QColor("#6b5a47"))
        header.setPos(-110, -42)

        text_item = QGraphicsTextItem(
            preview_text[:50] + "…" if len(preview_text) > 50 else preview_text, self
        )
        text_item.setFont(QFont("Lato", 14))
        text_item.setDefaultTextColor(QColor("#7a6956"))
        text_item.setPos(-110, -12)

        self.setTransformOriginPoint(self.rect().center())

    def hoverEnterEvent(self, event):
        timeline = QTimeLine(200)
        timeline.setEasingCurve(QEasingCurve.Type.OutQuad)

        anim = QGraphicsItemAnimation()
        anim.setItem(self)
        anim.setTimeLine(timeline)

        current_scale = self.scale() or 1.0
        anim.setScaleAt(0.0, current_scale, current_scale)
        anim.setScaleAt(1.0, 1.08, 1.08)

        timeline.start()

        self.setPen(QPen(self.pen().color().lighter(140), 3.0))

        sparkle = QGraphicsTextItem("✨", self)
        sparkle.setFont(QFont("Segoe UI Emoji", 18))
        sparkle.setDefaultTextColor(QColor(255, 240, 180, 220))
        sparkle.setPos(90, -30)
        sparkle.setOpacity(0.0)

        op_anim = QPropertyAnimation(sparkle, b"opacity")
        op_anim.setDuration(1400)
        op_anim.setStartValue(0.9)
        op_anim.setEndValue(0.0)
        op_anim.setEasingCurve(QEasingCurve.OutCubic)

        pos_anim = QPropertyAnimation(sparkle, b"pos")
        pos_anim.setDuration(1400)
        pos_anim.setStartValue(sparkle.pos())
        pos_anim.setEndValue(sparkle.pos() + QPointF(0, -90))
        pos_anim.setEasingCurve(QEasingCurve.OutQuad)

        op_anim.start()
        pos_anim.start()

    def hoverLeaveEvent(self, event):
        timeline = QTimeLine(250)
        timeline.setEasingCurve(QEasingCurve.Type.InOutQuad)

        anim = QGraphicsItemAnimation()
        anim.setItem(self)
        anim.setTimeLine(timeline)

        current_scale = self.scale()
        anim.setScaleAt(0.0, current_scale, current_scale)
        anim.setScaleAt(1.0, 1.0, 1.0)

        timeline.start()

        self.setPen(QPen(self.pen().color().darker(110), 2.5))


# class WarmNode(QGraphicsRectItem):
#     def __init__(self, node_id: int, preview_text: str, pos: QPointF):
#         super().__init__(QRectF(-140, -55, 280, 110))
#         self.node_id = node_id
#         self.preview_text = preview_text
#         self.setPos(pos)
#         self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
#         self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
#         self.setAcceptHoverEvents(True)

#         pastels = [
#             QColor("#fae8db"), QColor("#eaf5e2"), QColor("#e5edf9"),
#             QColor("#f6ebf4"), QColor("#fff8eb"), QColor("#f2ede3"),
#         ]
#         base_color = random.choice(pastels)

#         gradient = QLinearGradient(0, -55, 0, 55)
#         gradient.setColorAt(0.0, base_color.lighter(130))
#         gradient.setColorAt(0.4, base_color)
#         gradient.setColorAt(1.0, base_color.darker(120))
#         self.setBrush(QBrush(gradient))

#         pen = QPen()
#         pen.setStyle(Qt.SolidLine)
#         pen.setWidth(2.5)
#         pen_gradient = QLinearGradient(-140, -55, 140, 55)
#         pen_gradient.setColorAt(0, QColor(255, 255, 255, 220))
#         pen_gradient.setColorAt(0.5, QColor(255, 255, 255, 80))
#         pen_gradient.setColorAt(1, QColor(255, 255, 255, 20))
#         pen.setBrush(QBrush(pen_gradient))
#         self.setPen(pen)

#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(26)
#         shadow.setOffset(4, 8)
#         shadow.setColor(QColor(40, 30, 25, 110))
#         self.setGraphicsEffect(shadow)

#         emojis = ["🌿", "📝", "🍃", "🪴", "💭", "🌸", "✨", "🤗", "🍂", "🛋️"]
#         emoji_item = QGraphicsTextItem(random.choice(emojis), self)
#         emoji_item.setFont(QFont("Segoe UI Emoji", 28))
#         emoji_item.setPos(-128, -48)

#         header = QGraphicsTextItem(f"¶ {node_id}", self)
#         header.setFont(QFont("Lato", 13, QFont.Bold))
#         header.setDefaultTextColor(QColor("#6b5a47"))
#         header.setPos(-110, -42)

#         text_item = QGraphicsTextItem(
#             preview_text[:50] + "…" if len(preview_text) > 50 else preview_text, self
#         )
#         text_item.setFont(QFont("Lato", 14))
#         text_item.setDefaultTextColor(QColor("#7a6956"))
#         text_item.setPos(-110, -12)

#         self.setTransformOriginPoint(self.rect().center())

#     def hoverEnterEvent(self, event):
#         timeline = QTimeLine(200)
#         timeline.setEasingCurve(QEasingCurve.Type.OutQuad)

#         anim = QGraphicsItemAnimation()
#         anim.setItem(self)
#         anim.setTimeLine(timeline)

#         current_scale = self.scale() or 1.0
#         anim.setScaleAt(0.0, current_scale, current_scale)
#         anim.setScaleAt(1.0, 1.08, 1.08)

#         timeline.start()

#         self.setPen(QPen(self.pen().color().lighter(140), 3.0))

#         sparkle = QGraphicsTextItem("✨", self)
#         sparkle.setFont(QFont("Segoe UI Emoji", 18))
#         sparkle.setDefaultTextColor(QColor(255, 240, 180, 220))
#         sparkle.setPos(90, -30)
#         sparkle.setOpacity(0.0)

#         op_anim = QPropertyAnimation(sparkle, b"opacity")
#         op_anim.setDuration(1400)
#         op_anim.setStartValue(0.9)
#         op_anim.setEndValue(0.0)
#         op_anim.setEasingCurve(QEasingCurve.OutCubic)

#         pos_anim = QPropertyAnimation(sparkle, b"pos")
#         pos_anim.setDuration(1400)
#         pos_anim.setStartValue(sparkle.pos())
#         pos_anim.setEndValue(sparkle.pos() + QPointF(0, -90))
#         pos_anim.setEasingCurve(QEasingCurve.OutQuad)

#         op_anim.start()
#         pos_anim.start()

#     def hoverLeaveEvent(self, event):
#         timeline = QTimeLine(250)
#         timeline.setEasingCurve(QEasingCurve.Type.InOutQuad)

#         anim = QGraphicsItemAnimation()
#         anim.setItem(self)
#         anim.setTimeLine(timeline)

#         current_scale = self.scale()
#         anim.setScaleAt(0.0, current_scale, current_scale)
#         anim.setScaleAt(1.0, 1.0, 1.0)

#         timeline.start()

#         self.setPen(QPen(self.pen().color().darker(110), 2.5))

