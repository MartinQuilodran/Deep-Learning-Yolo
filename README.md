# VisionAim

## Instalación

### VENV - Instalar entorno virtual

python -m venv venv

venv\Scripts\activate

### Librerias necesarias

pip install opencv-python torch torchvision pyautogui numpy matplotlib

### Requerimientos YOLOv5

git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt

### Requerimientos necesarios

GPU compatible con CUDA (Nvidia)

## Comparacion Modelos Entrenados
En un inicio ocupamos el modelo preentrenado por yolo, pero este era muy lento, tenia pocos fotogramas por segundo y tenia mucha latencia, decidimos cambiar un modelo entrenado por un dataset de 267 fotos especificas de CS:GO, pero debido a su bajo rendimiento decidimos cambiar a otro dataset de 10.000 fotos
### 1er Dataset(267 fotos)
![results](https://github.com/user-attachments/assets/b4048bad-359d-4b74-8354-d2b2c9662bde)

### 2do Dataset
Fueron entrenados 3 modelos, basado en los modelos de yolo Nano, Small, y Medium

> Nano
![results (1)](https://github.com/user-attachments/assets/868f858c-0772-40a9-8a4d-b694dde1109f)
> Small
![results (2)](https://github.com/user-attachments/assets/11871e75-6f94-4b77-825f-eccc833ebe29)
> Medium
![results (3)](https://github.com/user-attachments/assets/440f0ec2-340b-4a0f-b173-9d71920088a1)

El modelo Medium ofrece un rendimiento significativamente superior en detección de objetos, tanto en precisión como en capacidad de generalización. El resto, aunque más ligeros, compromete notablemente la calidad de los resultados. Idealmente, usar Medium si los recursos lo permiten.

