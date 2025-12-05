# colorutil.py
import mss
import win32gui
import win32ui
import win32con
import numpy as np

# Buja chart window title
WINDOW_TITLE = "Buja Chart"

# 신호 색상 정의 (RGB 기반)
COLOR_MAP = {
    "red":     (255, 0, 0),
    "blue":    (0, 0, 255),
    "pink":    (255, 0, 255),
    "sky":     (0, 255, 255),
}

def get_pixel_color2(x, y):
    """
    화면 전체 기준 (screen 좌표)의 특정 픽셀 RGB 반환
    """
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    colorref = win32gui.GetPixel(hdc, x, y)
    win32gui.ReleaseDC(hwnd, hdc)

    r = colorref & 0xff
    g = (colorref >> 8) & 0xff
    b = (colorref >> 16) & 0xff

    return (r, g, b)

def get_pixel_color(x, y):
    """
    mss로 좌표 1픽셀만 캡처해서 색상 추출
    (win32gui.GetPixel 불가 문제 완전 해결)
    """
    with mss.mss() as sct:
        grab_area = {"top": y, "left": x, "width": 1, "height": 1}
        
        img = sct.grab(grab_area)
        arr = np.array(img)

        # BGRA → RGB 변환
        b, g, r, _ = arr[0, 0]
        return (r, g, b)


def match_color(rgb):
    R, G, B = rgb

    def near(a, b, tol=20):
        return abs(a - b) <= tol

    # 흰색 제외 (배경)
    if near(R, 255) and near(G, 255) and near(B, 255):
        return "white"

    # 빨강(상승2)
    if near(R, 255) and near(G, 0) and near(B, 0):
        return "red"

    # 파랑(하락2)
    if near(R, 0) and near(G, 0) and near(B, 255):
        return "blue"

    # 분홍(상승1)
    if near(R, 255) and near(G, 0) and near(B, 255):
        return "pink"

    # 하늘(하락1)
    if near(R, 0) and near(G, 255) and near(B, 255):
        return "sky"

    return "unknown"
