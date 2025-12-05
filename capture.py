# capture.py
import mss
import numpy as np
from PIL import Image

def save_capture_point(x, y, save_path="capture_point.png"):
    
    w = 10
    h = 10
    
    """
    화면의 (x, y) 한 점을 캡처하여 저장하는 함수
    """
    try:
        with mss.mss() as sct:
            monitor = {
                "top": y - h / 2,
                "left": x - w / 2,
                "width": w,
                "height": h
            }

            img = sct.grab(monitor)
            arr = np.array(img)

            # BGRA → RGB
            rgb = arr[:, :, :3][:, :, ::-1]

            image = Image.fromarray(rgb)
            image.save(save_path)
            print(f"📸 캡처 저장 완료 → {save_path}")

    except Exception as e:
        print(f"⚠️ 캡처 실패: {e}")

def save_capture_roi(x, y, w, h, p1, p2, save_path="capture_test.png"):
    """
    x, y는 화면의 절대좌표 기준
    p1, p2는 (x, y)로 x, y기준으로 상대 좌표
    
    화면의 (x, y, w, h) 영역을 캡처하고,
    캡쳐한 이미지의 p1, p2 위치에 '+' 표시를 한 뒤 저장하는 함수
    ※ 디버깅/확인용
    """
    if w <= 0 or h <= 0:
        print("❌ 캡처 영역 오류: 너비/높이 값이 잘못되었습니다.")
        return

    try:
        with mss.mss() as sct:
            monitor = {
                "top": y,
                "left": x,
                "width": w,
                "height": h
            }

            img = sct.grab(monitor)
            arr = np.array(img)

            # BGRA → RGB
            rgb = arr[:, :, :3][:, :, ::-1]

            image = Image.fromarray(rgb)
            draw = ImageDraw.Draw(image)

            def draw_cross(px, py, color):
                # 캡처 영역 기준 좌표로 변환
                rel_x = px
                rel_y = py
                # + 표시 길이 10px
                draw.line((rel_x - 5, rel_y, rel_x + 5, rel_y), fill=color, width=2)
                draw.line((rel_x, rel_y - 5, rel_x, rel_y + 5), fill=color, width=2)

            # 색상은 하얀색 (255,255,255) 또는 원하시는 색
            cross_color = (0, 0, 0)   # 노란색 추천

            draw_cross(p1[0], p1[1], cross_color)
            draw_cross(p2[0], p2[1], cross_color)

            image.save(save_path)
            print(f"📸 캡처 + p1/p2 마킹 저장 완료 → {save_path}")

    except Exception as e:
        print(f"⚠️ 캡처 실패: {e}")
