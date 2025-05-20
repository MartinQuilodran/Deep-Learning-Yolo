import torch
import pyautogui
import cv2
import numpy as np

# Cargar el modelo YOLOv5 preentrenado
model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True).to('cuda')

# Tamaño del recorte
CROP_SIZE = 512

# Obtener tamaño de pantalla
screen_width, screen_height = pyautogui.size()

# Calcular coordenadas para el recorte centrado
left = screen_width // 2 - CROP_SIZE // 2
top = screen_height // 2 - CROP_SIZE // 2
right = left + CROP_SIZE
bottom = top + CROP_SIZE

while True:
    # Captura del recorte de pantalla
    screenshot = pyautogui.screenshot(region=(left, top, CROP_SIZE, CROP_SIZE))
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Asegúrate de que el modelo corra en GPU
    results = model(frame)  # OpenCV ya convierte a tensor por dentro

    # Mostrar resultados
    results.render()
    cv2.imshow('VisionAIM - Zona Central', results.ims[0])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
