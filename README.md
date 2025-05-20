VENV - Instalar entorno virtual

python -m venv venv
venv\Scripts\activate


Librerias necesarias

pip install opencv-python torch torchvision pyautogui numpy matplotlib

Requerimientos YOLOv5

git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
