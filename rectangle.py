# rectangle.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor


class RoiRectangle(QWidget):
    """
    ROI 설정용 빨간 사각형 위젯

    기능:
    - 드래그로 이동
    - 우측/하단 리사이즈
    - 변경될 때마다 on_changed 콜백 호출 (입력창 즉시 갱신)

    개선 사항:
    - 콜백 방식으로 부모 업데이트 호출
    """
    def __init__(self, parent, x, y, w, h, ox0, ox1, on_changed=None):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)

        self.ox0 = ox0
        self.ox1 = ox1
        self.on_changed = on_changed

        self.dragging = False
        self.resizing = False
        self.resize_margin = 8
        self.start_pos = None
        self.selected = False

        self.setMouseTracking(True)
        
    def getOX0(self):
        return self.ox0
        
    def getOX1(self):
        return self.ox1

    def setOX0(self, ox0):
        self.ox0 = ox0
        
    def setOX1(self, ox1):
        self.ox1 = ox1
        
    def setSelected(self, selected: bool):
        self.selected = selected
        self.update()
        
    def getPoints(self):
        offset_x = 10
        offset_y = 54
        
        chart_y = offset_y
        x = self.x() + self.width()
        y = self.y() + self.height()
        
        cy = y - 45 - 10
        p0 = (x - self.ox0, cy)
        p1 = (x - self.ox1, cy)

        return p0, p1

    def paintEvent(self, event):
        painter = QPainter(self)

        # ROI 테두리 색 적용
        color  = QColor(0,0,255)
        if self.selected:
            color = QColor(255,0,0)  # 빨간색(선택됨)
        
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # 🔶 클릭 십자 표시
        p0, p1 = self.getPoints()
        mark = 5

        cx = p0[0] - self.x()
        cy = p0[1] - self.y()
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        painter.drawLine(cx - mark, cy, cx + mark, cy)
        painter.drawLine(cx, cy - mark, cx, cy + mark)
        
        cx = p1[0] - self.x()
        cy = p1[1] - self.y()
        pen = QPen(QColor(255, 0, 255), 2)
        painter.setPen(pen)
        painter.drawLine(cx - mark, cy, cx + mark, cy)
        painter.drawLine(cx, cy - mark, cx, cy + mark)


    # ---------------------------------------------------------
    # 마우스 이벤트
    # ---------------------------------------------------------
    def mousePressEvent(self, event):
        if self.selected == False:
            return
        
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()

            near_right = abs(event.pos().x() - self.width()) < self.resize_margin
            near_bottom = abs(event.pos().y() - self.height()) < self.resize_margin

            if near_right or near_bottom:
                self.resizing = True
            else:
                self.dragging = True

    def mouseMoveEvent(self, event):
        if self.selected == False:
            return
        
        # 커서 모양 설정
        near_right = abs(event.pos().x() - self.width()) < self.resize_margin
        near_bottom = abs(event.pos().y() - self.height()) < self.resize_margin

        if near_right or near_bottom:
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        # 드래그 이동
        if self.dragging:
            dx = event.x() - self.start_pos.x()
            dy = event.y() - self.start_pos.y()
            self.move(self.x() + dx, self.y() + dy)

            self.call_on_changed()
            return

        # 리사이즈
        if self.resizing:
            new_w = max(20, event.x())
            new_h = max(20, event.y())
            self.setGeometry(self.x(), self.y(), new_w, new_h)

            self.call_on_changed()
            return

    def mouseReleaseEvent(self, event):
        if self.selected == False:
            return
        
        self.dragging = False
        self.resizing = False
        self.setCursor(Qt.ArrowCursor)
        self.call_on_changed()

    # ---------------------------------------------------------
    # 부모 업데이트 콜백 호출 함수
    # ---------------------------------------------------------
    def call_on_changed(self):
        if self.on_changed:
            self.on_changed()

        # 부모 화면 다시 그리기
        if self.parent():
            self.parent().update()

        self.update()
