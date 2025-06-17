# VisionAIM GUI Pro con modo oscuro y control AIM por checkbox
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
MODEL_PATH = 'yolov5/runs/train/csgo_custom7/weights/best.pt'
CROP_SIZE = 512
AIM_SPEED = 3.0

# Inicialización global
detecciones_pendientes = []
running = False
fps_list = []
aim_enabled = False

# Resolución y centro de pantalla
screen_w, screen_h = pyautogui.size()
left = screen_w // 2 - CROP_SIZE // 2
top = screen_h // 2 - CROP_SIZE // 2
center_x = CROP_SIZE // 2
center_y = CROP_SIZE // 2
monitor = {"top": top, "left": left, "width": CROP_SIZE, "height": CROP_SIZE}

# Modelo YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH).to('cuda')
model.eval()
enemy_labels = ['ct', 'cthead', 't', 'thead']

# CSV por sesión
def generar_csv():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre = f"visionaim_log_{timestamp}.csv"
    ruta = os.path.join(os.getcwd(), nombre)
    with open(ruta, mode="w", newline="") as f:
        csv.writer(f).writerow(["evento", "timestamp", "cx", "cy"])
    return nombre, ruta

csv_filename, csv_path = generar_csv()

# Movimiento del mouse
def move_mouse_relative(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

# Ejecución principal
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

        closest_target = None
        min_distance = float('inf')

        for det in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = det
            label = model.names[int(cls)]
            if label == 't' and conf > 0.5:
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                dist = np.hypot(cx - center_x, cy - center_y)
                if dist < min_distance:
                    min_distance = dist
                    closest_target = (cx, cy)
                if mostrar_video.get():
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                    cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if closest_target:
            cx, cy = closest_target
            now = time.time()
            detecciones_pendientes.append(now)
            with open(csv_path, "a", newline="") as f:
                csv.writer(f).writerow(["deteccion", f"{now:.3f}", cx, cy])

            if aim_checkbox.get():
                dx = int((cx - center_x) * velocidad_aim.get())
                dy = int((cy - center_y) * velocidad_aim.get())
                if abs(dx) > 5 or abs(dy) > 5:
                    move_mouse_relative(dx, dy)

        if mouse.is_pressed(button='left'):
            now = time.time()
            cx_str = cx if closest_target else "-"
            cy_str = cy if closest_target else "-"
            with open(csv_path, "a", newline="") as f:
                csv.writer(f).writerow(["disparo", f"{now:.3f}", cx_str, cy_str])
            if closest_target and center_x - rango_precision.get() <= cx <= center_x + rango_precision.get():
                for i, t in enumerate(detecciones_pendientes):
                    reaccion = now - t
                    if reaccion > 0.05:
                        with open(csv_path, "a", newline="") as f:
                            csv.writer(f).writerow(["reaccion_acertada", f"{reaccion:.3f}", "-", "-"])
                        detecciones_pendientes.pop(i)
                        break

        fps = 1 / (time.time() - start)
        fps_list.append(fps)

        if mostrar_video.get():
            # Mostrar FPS
            cv2.putText(frame, f'FPS: {fps:.1f}', (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Mostrar estado del BOT solo si está activado
            if aim_checkbox.get():
                cv2.putText(frame, "BOT ACTIVADO", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("VisionAIM", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    cv2.destroyAllWindows()
    root.after(0, show_summary)

def start_program():
    global running, fps_list, detecciones_pendientes, csv_path, csv_filename
    if not running:
        fps_list = []
        detecciones_pendientes = []
        csv_filename, csv_path = generar_csv()
        with open(csv_path, mode="w", newline="") as f:
            csv.writer(f).writerow(["evento", "timestamp", "cx", "cy"])
        running = True
        threading.Thread(target=run_detection).start()

def stop_program():
    global running
    running = False

def show_summary():
    text = f"Archivo: {csv_filename}\n\n"
    try:
        df = pd.read_csv(csv_path)
        if 'cx' not in df.columns or 'cy' not in df.columns or df.empty:
            text += "El archivo CSV no contiene datos válidos para análisis.\n\n"
            resultado_texto.config(text=text)
            boton_guardar.pack(pady=5)
            boton_abrir.pack(pady=5)
            return

        df['cx'] = pd.to_numeric(df['cx'], errors='coerce')
        df['cy'] = pd.to_numeric(df['cy'], errors='coerce')

        det = df[df['evento'] == 'deteccion']
        total = len(det)
        en_mira = det['cx'].between(center_x - rango_precision.get(), center_x + rango_precision.get()).sum()
        prec = (en_mira / total) * 100 if total > 0 else 0
        dis = df[df['evento'] == 'disparo']
        d_mira = dis['cx'].between(center_x - rango_precision.get(), center_x + rango_precision.get()).sum()
        prec2 = (d_mira / len(dis)) * 100 if len(dis) > 0 else 0
        reac = df[df['evento'] == 'reaccion_acertada']
        t_reac = reac['timestamp'].astype(float).mean() if not reac.empty else 0
        text += f"Detecciones: {total}\nEn mira: {en_mira}\nPrecisión detección: {prec:.2f}%\n\n"
        text += f"Disparos: {len(dis)}\nEn mira: {d_mira}\nPrecisión real: {prec2:.2f}%\n\n"
        text += f"Reacciones: {len(reac)}\nTiempo promedio: {t_reac:.3f} s"
    except Exception as e:
        text += f"Error en el análisis: {e}"
    resultado_texto.config(text=text)
    boton_guardar.pack(pady=5)
    boton_abrir.pack(pady=5)

def save_csv_copy():
    name = csv_filename.replace(".csv", "_copia.csv")
    path = os.path.join(os.getcwd(), name)
    with open(csv_path, 'r') as orig, open(path, 'w', newline='') as copy:
        copy.write(orig.read())
    messagebox.showinfo("Guardado", f"Copia guardada en:\n{path}")

def abrir_ubicacion():
    os.startfile(os.path.dirname(csv_path))

# Tema oscuro
DARK_BG = "#121212"
DARK_PANEL = "#1e1e1e"
DARK_TEXT = "#e0e0e0"
DARK_GREEN = "#2e7d32"
DARK_RED = "#c62828"
DARK_BLUE = "#1565c0"
DARK_FONT = ("Segoe UI", 10)

# Variables GUI
root = tk.Tk()
root.title("VisionAIM GUI Pro")
root.geometry("540x500")
root.minsize(540, 500)
root.configure(bg=DARK_BG)

# Ícono personalizado
root.iconbitmap("logo.ico")

mostrar_video = tk.BooleanVar(value=True)
rango_precision = tk.IntVar(value=25)
velocidad_aim = tk.DoubleVar(value=3.0)
aim_checkbox = tk.BooleanVar(value=False)

# Header
tk.Label(root, text="VisionAIM Trainer", font=("Segoe UI", 22, "bold"),
         bg=DARK_BG, fg=DARK_TEXT).pack(pady=10)

# Config frame
config_frame = tk.Frame(root, bg=DARK_BG)
config_frame.pack(pady=5)

tk.Checkbutton(config_frame, text="Mostrar video detección", variable=mostrar_video, bg=DARK_BG,
               fg=DARK_TEXT, selectcolor=DARK_BG, activebackground=DARK_BG, font=DARK_FONT).grid(row=0, column=0, padx=10, sticky="w")

tk.Label(config_frame, text="Rango de mira (± px):", bg=DARK_BG, fg=DARK_TEXT,
         font=DARK_FONT).grid(row=0, column=1)

tk.Spinbox(config_frame, from_=10, to=100, textvariable=rango_precision, width=5,
           font=DARK_FONT).grid(row=0, column=2, padx=5)

# Velocidad AIM (oculta por defecto)
velocidad_label = tk.Label(config_frame, text="Velocidad AIM:", bg=DARK_BG, fg=DARK_TEXT, font=DARK_FONT)
velocidad_slider = tk.Scale(config_frame, from_=1.0, to=10.0, resolution=0.5, orient="horizontal",
                             variable=velocidad_aim, bg=DARK_BG, fg=DARK_TEXT, highlightthickness=0)

# Mostrar/ocultar velocidad según estado del checkbox
def toggle_aim_speed(*args):
    if aim_checkbox.get():
        velocidad_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        velocidad_slider.grid(row=1, column=1, columnspan=2, pady=5)
    else:
        velocidad_label.grid_remove()
        velocidad_slider.grid_remove()

aim_checkbox.trace_add("write", toggle_aim_speed)
toggle_aim_speed()

# Botones
btn_frame = tk.Frame(root, bg=DARK_BG)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Iniciar detección", bg=DARK_GREEN, fg="white",
          font=("Segoe UI", 11, "bold"), width=18, command=start_program).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="Detener", bg=DARK_RED, fg="white",
          font=("Segoe UI", 11, "bold"), width=10, command=stop_program).grid(row=0, column=1)

# Estadísticas
stats_frame = tk.Frame(root, bg=DARK_PANEL, bd=2, relief="groove")
stats_frame.pack(padx=30, pady=(15, 0), fill="both", expand=False, anchor="n")

resultado_texto = tk.Label(stats_frame, text="Esperando resultados...", justify="left",
                           font=DARK_FONT, bg=DARK_PANEL, fg=DARK_TEXT, anchor="nw")
resultado_texto.pack(padx=10, pady=10, fill="both", expand=True)

# Botón Guardar y Abrir
boton_guardar = tk.Button(root, text="Guardar copia CSV", command=save_csv_copy,
                          font=DARK_FONT, bg=DARK_BLUE, fg="white")
boton_abrir = tk.Button(root, text="Abrir ubicación del archivo", command=abrir_ubicacion,
                        font=DARK_FONT)

# Checkbox AIM "BOT" en esquina inferior derecha
aim_check = tk.Checkbutton(root, text="BOT", variable=aim_checkbox, bg=DARK_BG, fg=DARK_TEXT,
                           selectcolor=DARK_BG, font=("Segoe UI", 10, "bold"))
aim_check.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

# Lanzar GUI
root.mainloop()

