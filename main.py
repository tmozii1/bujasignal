import json
import os
import sys
import time
import threading
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PIL import ImageGrab

import win32gui
import win32con

FASTAPI_URL = "https://buja.tim.pe.kr/signal"
WIN_TITLE = "buja chart" # "파일 탐색기" #
TARGET_FILE = os.path.join("dist", "target.json")

# ===== 색 정의 =====
SIGNAL_COLORS = {
    (255, 0, 0): ("1", "1920틱 상승"),
    (0, 0, 255): ("2", "1920틱 하락"),
    (255, 0, 255): ("3", "480틱 상승"),
    (0, 255, 255): ("4", "480틱 하락")
}
WHITE = (255, 255, 255)
wx = 0
wy = 0

class SignalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buja Chart Signal Monitor")
        self.setGeometry(100, 600, 400, 300)

        # UI
        self.startBtn = QPushButton("시작", self)
        self.logBox = QTextEdit(self)
        self.logBox.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.startBtn)
        layout.addWidget(self.logBox)
        self.setLayout(layout)

        self.startBtn.clicked.connect(self.toggleStart)

        # 모니터링 타이머
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 0.1초

        self.timer.timeout.connect(self.checkSignals)

        # target.json 로드
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            self.targets = json.load(f)
            
        self.prev_color = {
            item["name"]: {"p0": None, "p1": None}
            for item in self.targets
        }
        # 중복 전송 방지
        self.sent_flag = {item["name"]: False for item in self.targets}

    # --------------------------------------------------------
    # Buja Chart 창을 최상단으로
    # --------------------------------------------------------
    def bringBujaToFront(self):
        def enumHandler(hwnd, result):
            title = win32gui.GetWindowText(hwnd)
            if WIN_TITLE in title.lower():
                result.append(hwnd)

        found = []
        win32gui.EnumWindows(enumHandler, found)

        if found:
            hwnd = found[0]
            win32gui.SetForegroundWindow(hwnd)
            wx, wy, _, _ = win32gui.GetWindowRect(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            self.log("Buja Chart 창을 최상단으로 띄움.")
        else:
            self.log("Buja Chart 창을 찾지 못함.")

    # --------------------------------------------------------
    # UI 로그 출력
    # --------------------------------------------------------
    def log(self, msg):
        self.logBox.append(msg)

    # --------------------------------------------------------
    # 시작 / 종료 버튼
    # --------------------------------------------------------
    def toggleStart(self):
        if self.startBtn.text() == "시작":
            self.startBtn.setText("종료")
            self.bringBujaToFront()
            self.timer.start()
            self.log("신호 모니터링 시작.")
        else:
            self.timer.stop()
            self.log("신호 모니터링 종료.")
            QApplication.quit()

    # --------------------------------------------------------
    # 픽셀 색 읽기
    # --------------------------------------------------------
    def getPixel(self, x, y):
        rx = wx + x
        ry = wy + y
        img = ImageGrab.grab(bbox=(rx, ry, rx+1, ry+1))
        pixel = img.getpixel((0, 0))
        return pixel  # RGB 튜플

    # --------------------------------------------------------
    # FastAPI 서버 전송
    # --------------------------------------------------------
    def sendToServer(self, name, signal, msg):
        data = {
            "name": name,
            "signal": signal,
            "msg": msg
        }
        try:
            requests.post(FASTAPI_URL, json=data, timeout=1)
            self.log(f"[전송 완료] {name} - {signal} ({msg})")
        except:
            self.log(f"[전송 실패] {name}")

    # --------------------------------------------------------
    # 메인 체크 로직
    # --------------------------------------------------------
    def checkSignals(self):
        for item in self.targets:
            name = item["name"]
            x0, y0 = item["x0"], item["y0"]
            x1, y1 = item["x1"], item["y1"]

            # 현재 색 읽기
            p0 = self.getPixel(x0, y0)
            p1 = self.getPixel(x1, y1)

            # 이전 색 가져오기
            prev_p0 = self.prev_color[name]["p0"]
            prev_p1 = self.prev_color[name]["p1"]

            # 변화 여부 체크
            changed = (prev_p0 != p0) or (prev_p1 != p1)

            # 변화 없으면 아무 동작 안함
            if not changed:
                continue

            # 이전 색 업데이트
            self.prev_color[name]["p0"] = p0
            self.prev_color[name]["p1"] = p1

            # p0이 지정 색이 아니라면 skip
            if p0 not in SIGNAL_COLORS:
                continue

            # 전송!
            signal, msg = SIGNAL_COLORS[p0]
            self.sendToServer(name, signal, msg)
            self.sent_flag[name] = True

                    
    def captureAreaAround(self, x, y, size=5, save_path=None):
        """
        (x, y) 중심으로 size 만큼 좌우 상하로 확장한 영역을 캡처.
        예: size=5 → 11x11 영역

        x, y        : 중심 좌표 (절대좌표)
        size        : 반경 (5 → -5~+5)
        save_path   : 파일 저장 경로 (None이면 이미지 반환만)
        """
        
        s = int(size / 2)

        left = x - s
        top = y - s
        right = x + s
        bottom = y + s

        img = ImageGrab.grab(bbox=(left, top, right, bottom))

        if save_path:
            img.save(save_path)
            return save_path

        return img


    def captureDebugImage(self, x, y, name):
        img = self.captureAreaAround(x, y, size=10, save_path=None)
        img.save(f"debug_{name}.png")
        self.log(f"디버그 이미지 저장: debug_{name}.png")

# ============================================================
#                      ★ main() 함수 ★
# ============================================================

def main():
    app = QApplication(sys.argv)
    win = SignalApp()
    win.show()
    sys.exit(app.exec_())


# ============================================================
#                       실행부
# ============================================================

if __name__ == "__main__":
    main()