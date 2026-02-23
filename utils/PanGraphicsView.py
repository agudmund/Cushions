import sys
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QWheelEvent, QKeyEvent, QCursor

class PanZoomGraphicsView(QGraphicsView):
    """Cozy pan + zoom view perfect for the warm digital sketchbook 🌱📖"""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        
        self.setRenderHints(
            QPainter.Antialiasing | 
            QPainter.SmoothPixmapTransform | 
            QPainter.TextAntialiasing
        )
        
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Clean sketchbook look — no visible scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self._is_panning = False
        self._pan_start_pos = QPointF()
        
        # Gentle zoom settings (feels natural, never overwhelming)
        self._zoom_factor = 1.18
        self._min_zoom = 0.25
        self._max_zoom = 6.0

    def wheelEvent(self, event: QWheelEvent):
        """Smooth zoom toward mouse cursor."""
        if event.angleDelta().y() > 0:
            factor = self._zoom_factor
        else:
            factor = 1 / self._zoom_factor
            
        current_scale = self.transform().m11()
        
        if (factor > 1 and current_scale >= self._max_zoom) or \
           (factor < 1 and current_scale <= self._min_zoom):
            return
            
        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start_pos = event.position()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position() - self._pan_start_pos
            self._pan_start_pos = event.position()
            
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard shortcuts that feel like turning real pages."""
        if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self.scale(self._zoom_factor, self._zoom_factor)
        elif event.key() == Qt.Key_Minus:
            self.scale(1 / self._zoom_factor, 1 / self._zoom_factor)
        elif event.key() == Qt.Key_0:
            self.resetTransform()  # reset zoom & pan
        else:
            super().keyPressEvent(event)