# roi_window.py
import os
import json

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen

from rectangle import RoiRectangle
from winutil import get_window_rect, bring_to_front


class RoiWindow(QWidget):
    """
    ROI 설정 + 클릭 좌표 설정용 오버레이 창

    - ROI(빨간박스) : x,y,w,h
    - 차트 박스(노란박스) : x+9, y+60, w-83, h-42
    - ox, oy : 화면 클릭으로 설정되는 좌표 (relative to Buja Chart)

    - 클릭하면 십자 표시 (+)
    """

    def __init__(self):
        super().__init__()
        
        # 1) Buja Chart 창 좌표
        hwnd, base_x, base_y, base_w, base_h = get_window_rect("Buja Chart")
        bring_to_front(hwnd)

        # 2) Overlay 창 설정
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(base_x, base_y, base_w, base_h)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 3) 기본값
        self.rx = 50
        self.ry = 50
        self.rw = 220
        self.rh = 180
        self.bar_count = 2

        # 추가된 값
        self.ox = 0
        self.oy = 0

        # 4) config.json 로딩
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.rx = int(cfg.get("x", self.rx))
                self.ry = int(cfg.get("y", self.ry))
                self.rw = int(cfg.get("w", self.rw))
                self.rh = int(cfg.get("h", self.rh))
                self.bar_count = int(cfg.get("bar_count", self.bar_count))
                self.ox = int(cfg.get("ox", self.ox))
                self.oy = int(cfg.get("oy", self.oy))
            except:
                pass

        # 5) ROI(빨간 박스)
        self.roi_rect = RoiRectangle(
            self,
            self.rx, self.ry, self.rw, self.rh,
            lambda: self.bar_count
        )

        self.build_controls()

    # -----------------------------
    # UI 입력창
    # -----------------------------
    def build_controls(self):

        labels = ["x", "y", "w", "h", "bar_count"]
        defaults = [self.rx, self.ry, self.rw, self.rh, self.bar_count]

        self.inputs = {}

        # ------------------------------
        # 버튼은 항상 하단 30px 위에 고정
        # ------------------------------
        button_y = self.height() - 40  # (아래 30px 여백 확보)
        self.btn_save = QPushButton("저장", self)
        self.btn_save.setGeometry(20, button_y, 70, 30)
        self.btn_save.clicked.connect(self.save_and_close)

        self.btn_close = QPushButton("닫기", self)
        self.btn_close.setGeometry(100, button_y, 70, 30)
        self.btn_close.clicked.connect(self.close)

        # ------------------------------
        # Input 창은 버튼 바로 위부터 쌓는다 (아래 정렬)
        # ------------------------------
        # 마지막 버튼 기준으로 input 을 아래쪽에 맞춤
        bottom_start = button_y - 30   # 버튼 위 여백 30px  
        row_gap = 25

        # input 을 아래에서 위로 배치
        current_y = bottom_start - row_gap

        for name, value in reversed(list(zip(labels, defaults))):
            # Input 줄 하나 배치
            lbl = QLabel(name, self)
            lbl.move(20, current_y)

            edit = QLineEdit(str(value), self)
            edit.setGeometry(80, current_y, 80, 20)
            edit.textChanged.connect(self.apply_input_change)
            self.inputs[name] = edit

            # 다음 줄은 위로 25px
            current_y -= row_gap



    # -----------------------------
    # 입력창 → 변수 반영
    # -----------------------------
    def apply_input_change(self):
        try:
            self.rx = int(self.inputs["x"].text())
            self.ry = int(self.inputs["y"].text())
            self.rw = int(self.inputs["w"].text())
            self.rh = int(self.inputs["h"].text())
            self.bar_count = int(self.inputs["bar_count"].text())
        except:
            return

        self.roi_rect.setGeometry(self.rx, self.ry, self.rw, self.rh)
        self.update()

    # -----------------------------
    # ROI 변경 → 입력창 반영
    # -----------------------------
    def update_inputs_from_rect(self):
        self.inputs["x"].setText(str(self.roi_rect.x()))
        self.inputs["y"].setText(str(self.roi_rect.y()))
        self.inputs["w"].setText(str(self.roi_rect.width()))
        self.inputs["h"].setText(str(self.roi_rect.height()))

    # -----------------------------
    # 저장
    # -----------------------------
    def save_and_close(self):
        data = {
            "x": self.roi_rect.x(),
            "y": self.roi_rect.y(),
            "w": self.roi_rect.width(),
            "h": self.roi_rect.height(),
            "bar_count": self.bar_count
        }

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "저장", "저장되었습니다.")
        self.close()

    # -----------------------------
    # 화면 표시
    # -----------------------------
    def paintEvent(self, event):
        painter = QPainter(self)

        # 반투명 전체 배경
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        # 🔶 노란 박스(차트 영역)
        roi_x = self.roi_rect.x()
        roi_y = self.roi_rect.y()
        roi_w = self.roi_rect.width()
        roi_h = self.roi_rect.height()
        
        offset_x = 10
        offset_y = 54
        
        chart_w = int((roi_w - offset_x - 81) / self.bar_count)
        
        chart_x = roi_x + offset_x + chart_w * (self.bar_count - 1)
        chart_y = roi_y + offset_y
        chart_h = roi_h - offset_y - 42

        if chart_w > 0 and chart_h > 0:
            pen = QPen(QColor(255, 255, 0), 2)
            painter.setPen(pen)
            painter.drawRect(chart_x, chart_y, chart_w, chart_h)

        # 🔶 클릭 십자 표시
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        cx = chart_x + int(chart_w / 2)
        cy = chart_y + int(chart_h * 4 / 5)

        painter.drawLine(cx - 5, cy, cx + 5, cy)  # 가로 10
        painter.drawLine(cx, cy - 5, cx, cy + 5)  # 세로 10
        
        pen = QPen(QColor(255, 0, 255), 2)
        painter.setPen(pen)
        painter.drawLine(cx - 5 - chart_w, cy, cx + 5 - chart_w, cy)  # 가로 10
        painter.drawLine(cx - chart_w, cy - 5, cx - chart_w, cy + 5)  # 세로 10
