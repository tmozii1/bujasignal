# rectangle.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor


class RoiRectangle(QWidget):
    """
    ROI 설정용 빨간 사각형 위젯

    - 드래그로 이동
    - 테두리 우측/하단 근처 드래그로 리사이즈
    - parent 쪽에 updateInputsFromRect() 메서드가 있다고 가정하고 호출
    - get_bar_count(): 현재 bar_count를 반환하는 콜백 (lambda 등) 전달
    """

    def __init__(self, parent, x, y, w, h, get_bar_count):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)

        self.get_bar_count = get_bar_count

        self.dragging = False
        self.resizing = False
        self.resize_margin = 8
        self.start_pos = None

        # 마우스 커서 변경용 플래그
        self.setMouseTracking(True)

    # -----------------------------
    #  그리기
    # -----------------------------
    def paintEvent(self, event):
        painter = QPainter(self)

        # 빨간 테두리 (ROI)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # bar_count 기준 가이드 라인 (차트 영역 분할용)
        bar_count = self.get_bar_count()
        if bar_count and bar_count > 0:
            # 차트 영역을 ROI 내부에서 x+9, y+60, w-83, h-42 기준으로 계산
            # 여기서는 ROI 내부 좌표이므로 (0,0) 기준으로 변환
            chart_x0 = 9
            chart_y0 = 60
            chart_x1 = self.width() - 83
            chart_y1 = self.height() - 42

            chart_w = chart_x1 - chart_x0
            chart_h = chart_y1 - chart_y0

            if chart_w > 0 and chart_h > 0:
                guide_pen = QPen(QColor(255, 0, 0, 100), 1)
                painter.setPen(guide_pen)

                # bar_count 개로 세로 분할선
                step = chart_w / bar_count
                for i in range(1, bar_count):
                    x = int(chart_x0 + i * step)
                    painter.drawLine(x, chart_y0, x, chart_y0 + chart_h)

    # -----------------------------
    #  마우스 이벤트 (드래그 / 리사이즈)
    # -----------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()

            # 우측/하단 근처면 리사이즈 모드
            near_right = abs(event.pos().x() - self.width()) < self.resize_margin
            near_bottom = abs(event.pos().y() - self.height()) < self.resize_margin

            if near_right or near_bottom:
                self.resizing = True
            else:
                self.dragging = True

    def mouseMoveEvent(self, event):
        # 커서 모양 변경 (우측/하단 근처이면 리사이즈 커서)
        near_right = abs(event.pos().x() - self.width()) < self.resize_margin
        near_bottom = abs(event.pos().y() - self.height()) < self.resize_margin
        if near_right or near_bottom:
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        if self.dragging:
            dx = event.x() - self.start_pos.x()
            dy = event.y() - self.start_pos.y()
            self.move(self.x() + dx, self.y() + dy)
            # 부모 쪽 인풋 동기화
            if hasattr(self.parent(), "update_inputs_from_rect"):
                self.parent().update_inputs_from_rect()
            self.parent().update()
            self.update()

        elif self.resizing:
            new_w = max(20, event.x())
            new_h = max(20, event.y())
            self.setGeometry(self.x(), self.y(), new_w, new_h)
            if hasattr(self.parent(), "update_inputs_from_rect"):
                self.parent().update_inputs_from_rect()
            self.parent().update()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.setCursor(Qt.ArrowCursor)
