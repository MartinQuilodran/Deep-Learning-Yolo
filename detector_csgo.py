import torch
import pyautogui
import cv2
import numpy as np
import time
import win32api
import win32con
import keyboard
import mss

# Configuración
MODEL_PATH = 'yolov5/runs/train/csgo_custom7/weights/best.pt'
CROP_SIZE = 512
AIM_SPEED = 3.0

# Tamaño centrado
screen_w, screen_h = pyautogui.size()
left = screen_w // 2 - CROP_SIZE // 2
top = screen_h // 2 - CROP_SIZE // 2
center_x = CROP_SIZE // 2
center_y = CROP_SIZE // 2

# Log de eventos
LOG_FILE = "feedback_log.txt"
with open(LOG_FILE, "w") as f:
    f.write("evento,timestamp,cx,cy\n")

detecciones_pendientes = []

# Captura con MSS
sct = mss.mss()
monitor = {"top": top, "left": left, "width": CROP_SIZE, "height": CROP_SIZE}

# Cargar modelo YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH).to('cuda')
model.eval()
enemy_labels = ['ct', 'cthead', 't', 'thead']

def move_mouse_relative(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

# Bucle principal
while True:
    start = time.time()
    screenshot = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    with torch.no_grad():
        results = model(frame)

    aim_active = keyboard.is_pressed('k')
    cv2.putText(frame, f"K: {'ON' if aim_active else 'OFF'}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0) if aim_active else (0, 0, 255), 2)

    closest_target = None
    min_distance = float('inf')

    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        if label == 't' and conf > 0.5:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            distance_to_center = np.hypot(cx - center_x, cy - center_y)
            if distance_to_center < min_distance:
                min_distance = distance_to_center
                closest_target = (cx, cy)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    if closest_target:
        cx, cy = closest_target
        now = time.time()
        detecciones_pendientes.append(now)

        with open(LOG_FILE, "a") as f:
            f.write(f"deteccion,{now:.3f},{cx},{cy}\n")

        if aim_active:
            dx = int((cx - center_x) * AIM_SPEED)
            dy = int((cy - center_y) * AIM_SPEED)
            if abs(dx) > 5 or abs(dy) > 5:
                move_mouse_relative(dx, dy)

    if aim_active and keyboard.is_pressed('mouse left'):
        now = time.time()
        with open(LOG_FILE, "a") as f:
            f.write(f"disparo,{now:.3f},{cx if closest_target else '-'},{cy if closest_target else '-'}\n")

        if detecciones_pendientes:
            inicio = detecciones_pendientes.pop(0)
            reaccion = now - inicio
            with open(LOG_FILE, "a") as f:
                f.write(f"reaccion,{reaccion:.3f},-,-\n")

    # FPS y ventana
    fps = 1 / (time.time() - start)
    cv2.putText(frame, f'FPS: {fps:.1f}', (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("VisionAIM [Stretched Fix]", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
w
