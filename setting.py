import os
import json

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen

from rectangle import RoiRectangle
from winutil import get_window_rect, bring_to_front


# dist 폴더 생성
DIST_DIR = "dist"
if not os.path.exists(DIST_DIR):
    os.makedirs(DIST_DIR)

CONFIG_FILE = os.path.join(DIST_DIR, "config.json")
TARGET_FILE = os.path.join(DIST_DIR, "target.json")
WIN_TITLE = "BuJa Chart"

class RoiWindow(QWidget):
    """
    ROI 설정 + 클릭 좌표 설정용 오버레이 창

    - config.json 구조:
    [
        { "name": "Gold", "x":..., "y":..., "w":..., "h":..., "bar_count":... },
        { "name": "CrudeOil", ... },
        ...
    ]
    """
    
    def __init__(self):
        super().__init__()
        
        # 1) Buja Chart 창 좌표
        hwnd, base_x, base_y, base_w, base_h = get_window_rect(WIN_TITLE)
        bring_to_front(hwnd)

        # Overlay 창 설정
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(base_x, base_y, base_w, base_h)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowModality(Qt.ApplicationModal)

        # 저장된 config 리스트 전체
        self.config_list = []
        self.current_index = 0  # ComboBox에서 선택된 index

        # 기본값
        self.rx = 50
        self.ry = 50
        self.rw = 220
        self.rh = 180
        self.bar_count = 2
        self.show_point = False

        # config.json 로딩
        self.load_config()

        self.roi_rects = []    # ROI 전체 리스트

        for cfg in self.config_list:
            rect = RoiRectangle(
                self,
                cfg["x"], cfg["y"], cfg["w"], cfg["h"],
                self.bar_count,
                on_changed=self.update_inputs_from_rect
            )
            rect.setSelected(self.config_list.index(cfg) == 0)
            self.roi_rects.append(rect)

        # UI 구성
        self.build_controls()

    # ---------------------------------------------------------
    # config.json 로딩
    # ---------------------------------------------------------
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config_list = json.load(f)
            except:
                self.config_list = []

        # config 없으면 기본 템플릿 하나 생성
        if not self.config_list:
            self.config_list = [
                {
                    "name": "Gold",
                    "x": self.rx,
                    "y": self.ry,
                    "w": self.rw,
                    "h": self.rh,
                    "bar_count": self.bar_count
                }
            ]

        # 첫 항목 적용
        self.apply_selected_config(0)

    # ---------------------------------------------------------
    # 선택한 config 항목을 ROI/UI에 적용
    # ---------------------------------------------------------
    def apply_selected_config(self, idx):
        self.current_index = idx
        item = self.config_list[idx]

        self.rx = int(item.get("x", self.rx))
        self.ry = int(item.get("y", self.ry))
        self.rw = int(item.get("w", self.rw))
        self.rh = int(item.get("h", self.rh))
        self.bar_count = int(item.get("bar_count", self.bar_count))

    # ---------------------------------------------------------
    # UI 생성
    # ---------------------------------------------------------
    def build_controls(self):

        # ------------------------------
        # 저장/닫기 버튼은 아래 고정
        # ------------------------------
        button_y = self.height() - 40
        self.btn_save = QPushButton("저장", self)
        self.btn_save.setGeometry(20, button_y, 70, 30)
        self.btn_save.clicked.connect(self.save_selected_config)

        self.btn_close = QPushButton("닫기", self)
        self.btn_close.setGeometry(100, button_y, 70, 30)
        self.btn_close.clicked.connect(self.close)

        self.btn_show = QPushButton("좌표X", self)
        self.btn_show.setGeometry(180, button_y, 100, 30)
        self.btn_show.clicked.connect(self.toogle)

        # ------------------------------
        # 입력창들 (x,y,w,h,bar_count)
        # ------------------------------
        labels = ["x", "y", "w", "h", "bar_count"]
        defaults = [self.rx, self.ry, self.rw, self.rh, self.bar_count]

        self.inputs = {}

        # 버튼 위 시작지점
        bottom_start = button_y - 30
        row_gap = 25

        current_y = bottom_start - row_gap

        # x,y,w,h,bar_count 역순으로 배치
        for name, value in reversed(list(zip(labels, defaults))):
            lbl = QLabel(name, self)
            lbl.move(20, current_y)

            edit = QLineEdit(str(value), self)
            edit.setGeometry(80, current_y, 80, 20)
            edit.textChanged.connect(self.apply_input_change)

            self.inputs[name] = edit
            current_y -= row_gap

        # ------------------------------
        # ComboBox를 x Input 바로 위에 배치!
        # ------------------------------
        combo_y = current_y - 35  # x 입력창 바로 위 35px
        self.combo = QComboBox(self)
        self.combo.setGeometry(20, combo_y, 160, 25)

        for cfg in self.config_list:
            self.combo.addItem(cfg["name"])

        self.combo.currentIndexChanged.connect(self.on_combo_changed)

        # ------------------------------
        # TAB ORDER (위 → 아래)
        # ------------------------------
        self.setTabOrder(self.combo, self.inputs["x"])
        self.setTabOrder(self.inputs["x"], self.inputs["y"])
        self.setTabOrder(self.inputs["y"], self.inputs["w"])
        self.setTabOrder(self.inputs["w"], self.inputs["h"])
        self.setTabOrder(self.inputs["h"], self.inputs["bar_count"])
        self.setTabOrder(self.inputs["bar_count"], self.btn_save)
        self.setTabOrder(self.btn_save, self.btn_close)


    # ---------------------------------------------------------
    # ComboBox 선택 변경 시 → 화면 갱신
    # ---------------------------------------------------------
    def on_combo_changed(self, idx):
        self.apply_selected_config(idx)
        
        # 모든 ROI 색상 조정
        for i, rect in enumerate(self.roi_rects):
            rect.setSelected(i == idx)

        # --- 입력창 업데이트 시 textChanged 신호 차단 ---
        for key in ["x", "y", "w", "h", "bar_count"]:
            widget = self.inputs[key]
            widget.blockSignals(True)
        
        selected = self.roi_rects[idx]
        self.inputs["x"].setText(str(selected.x()))
        self.inputs["y"].setText(str(selected.y()))
        self.inputs["w"].setText(str(selected.width()))
        self.inputs["h"].setText(str(selected.height()))
        self.inputs["bar_count"].setText(str(selected.getBarCount()))

        # --- 신호 다시 활성화 ---
        for key in ["x", "y", "w", "h", "bar_count"]:
            widget = self.inputs[key]
            widget.blockSignals(False)

        self.update()


    # ---------------------------------------------------------
    # 입력창 → ROI 변수 반영 (저장은 아님)
    # ---------------------------------------------------------
    def apply_input_change(self):
        try:
            self.rx = int(self.inputs["x"].text())
            self.ry = int(self.inputs["y"].text())
            self.rw = int(self.inputs["w"].text())
            self.rh = int(self.inputs["h"].text())
            self.bar_count = int(self.inputs["bar_count"].text())
        except:
            return

        roi_rect = self.roi_rects[self.current_index]
        roi_rect.setGeometry(self.rx, self.ry, self.rw, self.rh)
        roi_rect.bar_count = self.bar_count
        self.update()

    # ---------------------------------------------------------
    # 좌표에 사각형 그리기 토글
    # ---------------------------------------------------------
    def toogle(self):
        self.show_point = not self.show_point
        if self.show_point:         
            self.btn_show.setText("좌표O")
        else:
            self.btn_show.setText("좌표X")   
        self.update()    

    # ---------------------------------------------------------
    # 선택한 항목만 저장
    # ---------------------------------------------------------
    def save_selected_config(self):
        
        target = []
        for i, cfg in enumerate(self.config_list):        
            roi_rect = self.roi_rects[i]
            cfg["x"] = roi_rect.x()
            cfg["y"] = roi_rect.y()
            cfg["w"] = roi_rect.width()
            cfg["h"] = roi_rect.height()
            cfg["bar_count"] = roi_rect.getBarCount()
            
            x0, y0, x1, y1 = roi_rect.getPoints()
            t = {
                "name": cfg["name"],
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1               
            }
            target.append(t)

        # 전체 리스트를 다시 저장
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_list, f, indent=4, ensure_ascii=False)
            
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            json.dump(target, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "저장", "저장되었습니다.")

    # ---------------------------------------------------------
    # 그리기
    # ---------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        
        
    def update_inputs_from_rect(self):
        """ROI(Rectangle)의 현재 위치/크기를 입력창에 즉시 반영"""
        roi_rect = self.roi_rects[self.current_index]
        rx = roi_rect.x()
        ry = roi_rect.y()
        rw = roi_rect.width()
        rh = roi_rect.height()
        count = roi_rect.getBarCount()

        # QLineEdit 입력창 갱신
        self.inputs["x"].setText(str(rx))
        self.inputs["y"].setText(str(ry))
        self.inputs["w"].setText(str(rw))
        self.inputs["h"].setText(str(rh))
        self.inputs["bar_count"].setText(str(count))

        # bar_count는 rectangle 이동/리사이즈에 영향 X → 갱신 없음
        # 화면 다시 그리기
        self.update()



import sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    w = RoiWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
