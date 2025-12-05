# winutil.py
import win32gui
import win32con

def get_window_list():
    """
    현재 Windows OS에서 실행 중인 모든 '표시되는' 윈도우 목록을 가져온다.
    return: [(hwnd, title), ...]
    """
    window_list = []

    def enum_handler(hwnd, _):
        # 화면에 보이지 않는 창은 제외
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)

        # 제목이 없는 창은 제외
        if not title.strip():
            return

        window_list.append((hwnd, title))

    win32gui.EnumWindows(enum_handler, None)
    return window_list


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


def force_topmost(hwnd):
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,    # ← 진짜 TopMost 그룹
        0, 0, 0, 0,
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
    )
    
def remove_topmost(hwnd):
    # TopMost 해제 → 일반 창으로 돌림
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_NOTOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )