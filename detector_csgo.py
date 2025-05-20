import torch
import pyautogui
import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard  # pip install keyboard
import mss  # pip install mss

MODEL_PATH = 'csgo_Yolov5M/weights/best.pt'
CROP_SIZE = 512

# Coordenadas centradas para resolución 800x600
left = 256  # (1024 - 512) // 2
top = 128   # (768 - 512) // 2
center_x = CROP_SIZE // 2
center_y = CROP_SIZE // 2

sct = mss.mss()
monitor = {"top": top, "left": left, "width": CROP_SIZE, "height": CROP_SIZE}

model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH).to('cuda')
model.eval()

enemy_labels = ['enemy']

def move_mouse_relative(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

aim_active = False
k_prev_state = False

while True:
    start = time.time()

    if keyboard.is_pressed('k') and not k_prev_state:
        aim_active = not aim_active
        k_prev_state = True
    elif not keyboard.is_pressed('k'):
        k_prev_state = False

    screenshot = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    with torch.no_grad():
        results = model(frame)

    color_k = (0, 255, 0) if aim_active else (0, 0, 255)
    cv2.putText(frame, f'K: {"ON" if aim_active else "OFF"}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_k, 2)

    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        if label in enemy_labels:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            if aim_active:
                AIM_SPEED = 3.0
                dx = int((cx - center_x) * AIM_SPEED)
                dy = int((cy - center_y) * AIM_SPEED)
                if abs(dx) > 5 or abs(dy) > 5:
                    move_mouse_relative(dx, dy)

    fps = 1 / (time.time() - start)
    cv2.putText(frame, f'FPS: {fps:.1f}', (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("VisionAIM [K to toggle aim]", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
