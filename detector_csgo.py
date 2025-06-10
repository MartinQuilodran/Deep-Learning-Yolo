import torch
import pyautogui
import cv2
import numpy as np
import time
import win32api
import win32con
import mouse
import keyboard
import mss
import os
import datetime
import csv
import threading
import tkinter as tk
from tkinter import messagebox
import pandas as pd
# CONFIG
MODEL_PATH = 'csgo_Yolov5M/weights/best.pt'
CROP_SIZE = 512
AIM_SPEED = 3.0

# CSV
timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_filename = f"visionaim_log_{timestamp_str}.csv"
csv_path = os.path.join(os.getcwd(), csv_filename)

# Escritura inicial del CSV
with open(csv_path, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["evento", "timestamp", "cx", "cy"])

# Variables globales
detecciones_pendientes = []
running = False
fps_list = []

# Pantalla
screen_w, screen_h = pyautogui.size()
left = screen_w // 2 - CROP_SIZE // 2
top = screen_h // 2 - CROP_SIZE // 2
center_x = CROP_SIZE // 2
center_y = CROP_SIZE // 2
monitor = {"top": top, "left": left, "width": CROP_SIZE, "height": CROP_SIZE}


# Modelo
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH).to('cuda')
model.eval()
enemy_labels = ['ct', 'cthead', 't', 'thead']

def move_mouse_relative(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

def run_detection():
    sct = mss.mss()
    global running, detecciones_pendientes, fps_list
    fps_list = []

    while running:
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

            with open(csv_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["deteccion", f"{now:.3f}", cx, cy])

            if aim_active:
                dx = int((cx - center_x) * AIM_SPEED)
                dy = int((cy - center_y) * AIM_SPEED)
                if abs(dx) > 5 or abs(dy) > 5:
                    move_mouse_relative(dx, dy)

        # --- Disparo registrado siempre, con estado del aimbot ---
        if mouse.is_pressed(button='left'):
            now = time.time()
            cx_str = cx if closest_target else "-"
            cy_str = cy if closest_target else "-"
            with open(csv_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["disparo", f"{now:.3f}", cx_str, cy_str])

            if closest_target and 235 <= cx <= 265:
                # Buscar la detección más lejana (fuera de la mira) antes de este disparo
                for i, t in enumerate(detecciones_pendientes):
                    reaccion = now - t
                    if reaccion > 0.05:  # solo contar si ha pasado tiempo mínimo
                        with open(csv_path, mode="a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["reaccion_acertada", f"{reaccion:.3f}", "-", "-"])
                        detecciones_pendientes.pop(i)
                        break  # solo una por disparo



        fps = 1 / (time.time() - start)
        fps_list.append(fps)
        cv2.putText(frame, f'FPS: {fps:.1f}', (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("VisionAIM [K para aim]", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    root.after(0, show_summary)

def start_program():
    global running, fps_list, detecciones_pendientes, csv_path, csv_filename

    if not running:
        # Limpiar listas
        fps_list = []
        detecciones_pendientes = []

        # Crear nuevo archivo CSV por sesión
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_filename = f"visionaim_log_{timestamp_str}.csv"
        csv_path = os.path.join(os.getcwd(), csv_filename)

        with open(csv_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["evento", "timestamp", "cx", "cy"])

        # Iniciar hilo
        running = True
        threading.Thread(target=run_detection).start()


def stop_program():
    global running
    running = False

def show_summary():
    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    summary_text = f"📊 FPS Promedio: {avg_fps:.2f}\n📁 Log guardado en:\n{csv_path}"
    
    # Ejecutar análisis de puntería
    try:
        df = pd.read_csv(csv_path)

        # Asegurar que 'cx' y 'cy' sean numéricos; los '-' se vuelven NaN
        df['cx'] = pd.to_numeric(df['cx'], errors='coerce')
        df['cy'] = pd.to_numeric(df['cy'], errors='coerce')

        # ---- Análisis de puntería general ----
        detecciones = df[df['evento'] == 'deteccion']
        total_detecciones = len(detecciones)
        en_rango = detecciones['cx'].between(235, 265, inclusive='both')
        en_mira = en_rango.sum()
        porcentaje_detecciones = (en_mira / total_detecciones) * 100 if total_detecciones > 0 else 0

        resumen_deteccion = (
            f"\n🎯 Detecciones:\n"
            f"• Total: {total_detecciones}\n"
            f"• En la mira: {en_mira}\n"
            f"• Precisión detección: {porcentaje_detecciones:.2f}%"
        )

        # ---- Análisis de disparos ----
        disparos = df[df['evento'] == 'disparo']
        disparos_con_target = disparos.dropna(subset=['cx'])
        disparos_sin_target = disparos[disparos['cx'].isna()]
        disparos_en_mira = disparos_con_target['cx'].between(235, 265, inclusive='both').sum()

        resumen_disparo = (
            f"\n🔫 Disparos:\n"
            f"• Totales: {len(disparos)}\n"
            f"• Con target: {len(disparos_con_target)}\n"
            f"   - En la mira: {disparos_en_mira}\n"
            f"• Sin target (disparo sin enemigo): {len(disparos_sin_target)}"
        )

        # Precisión real: disparos buenos / disparos totales
        precision_real = (disparos_en_mira / len(disparos)) * 100 if len(disparos) > 0 else 0
        resumen_precision = f"\n📌 Precisión real de disparo: {precision_real:.2f}%"

        # Agregar al resumen
        summary_text += resumen_deteccion + resumen_disparo + resumen_precision

    except Exception as e:
        summary_text += f"\n❌ Error al analizar puntería:\n{e}"

    result_label.config(text=summary_text)
    save_button.pack()

def save_csv_copy():
    copy_name = f"{csv_filename.replace('.csv', '')}_copia.csv"
    copy_path = os.path.join(os.getcwd(), copy_name)
    with open(csv_path, 'r') as original, open(copy_path, 'w', newline='') as copy:
        copy.write(original.read())
    messagebox.showinfo("Guardado", f"Copia CSV guardada como:\n{copy_path}")


# GUI
root = tk.Tk()
root.title("VisionAIM GUI")
root.geometry("450x300")

tk.Label(root, text="🎯 Control VisionAIM", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="Iniciar detección", bg="green", fg="white", command=start_program).pack(pady=5)
tk.Button(root, text="Detener", bg="red", fg="white", command=stop_program).pack(pady=5)

result_label = tk.Label(root, text="", justify="left")
result_label.pack(pady=10)

save_button = tk.Button(root, text="Guardar copia CSV", command=save_csv_copy)

root.mainloop()
