# winutil.py
import win32gui
import win32con


def get_window_rect(title: str = "Buja Chart"):
    """
    제목이 title 인 윈도우의 핸들과 위치/크기를 반환.
    return: (hwnd, x, y, w, h)  - 모두 화면(Screen) 좌표 기준
    """
    hwnd = win32gui.FindWindow(None, title)
    if not hwnd:
        raise RuntimeError(f"Window '{title}' not found")

    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    return hwnd, x1, y1, x2 - x1, y2 - y1


def bring_to_front(hwnd):
    """
    해당 윈도우를 맨 앞으로 가져옴.
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        # 실패해도 프로그램이 죽지 않도록만 처리
        pass
