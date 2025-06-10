## 1ra entrega

# VisionAim
VisionAim es un programa de detección de enemigos para CS:GO para ayudar al jugador a mejorar mediante análisis estadisticos de su forma de juego.

![VID-20250513-WA0000_1](https://github.com/user-attachments/assets/7d465525-60af-4c0b-8866-206184b41589)

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

### 2da entrega

## Comparacion Modelos Entrenados
En la primera entrega ocupamos el modelo preentrenado por yolo, pero este era muy lento, tenia pocos fotogramas por segundo y tenia mucha latencia, para el segundo avance, decidimos cambiar por un modelo entrenado por nosotros con un dataset de 267 fotos especificas de CS:GO, pero debido a su bajo rendimiento decidimos cambiar a otro dataset de 10.000 fotos
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

![VID_20250610_063247_752](https://github.com/user-attachments/assets/dea7d498-481c-401f-86bc-dacb2d6eb0b5)


## 3ra entrega
En esta fase implementamos un analisis que está compuesto por 4 tipos de datos; Evento, timestamp, cx y cy. Existen 3 tipos de evento:

Detección - Cuando un enemigo entra dentro del campo de visión de YOLO

Disparo - Las veces que se presiona el click izquierdo en la ejecución

Reacción - Calculo que se realiza con los timestamp para saber cuando se demoró en llegar a una coordenada central para saber cuanto el jugador se demoró en apuntarle.

Timestamp representa el momento especifico en que se detectó al enemigo mediante un horario técnico, por último cx y cy sería las coordenadas exactas del enemigo representada en pixeles dentro de la pantalla. Esto es guardado en un archivo .csv para su posterior analisis estadístico en una siguiente fase.


## 4ta entrega
En esta fase se desarrolló una interfaz gráfica interactiva utilizando la librería Tkinter. Esta interfaz permite al usuario iniciar o detener la ejecución del sistema de detección, visualizar el estado del programa y acceder a un análisis estadístico. Además, se implementó un sistema de análisis estadístico automatizado que se activa al finalizar la sesión. Este análisis utiliza los datos registrados durante la ejecución, donde cada entrada contiene cuatro atributos clave: Evento, timestamp, cx y cy.

- Evento indica la acción registrada (por ejemplo: “Detección”, “Disparo” o “Reacción”).

- Timestamp representa el momento exacto en que ocurrió el evento, medido en segundos desde la época Unix.

- cx y cy corresponden a las coordenadas del centro del enemigo detectado en píxeles dentro del frame.

A partir de estos datos, el sistema calcula métricas como la precisión de los disparos, la tasa de error y otras estadísticas que ayudan a evaluar el desempeño durante la partida. Esta etapa también permite visualizar los datos recogidos de manera ordenada, apoyando así un análisis más profundo para futuras mejoras.

![App](https://github.com/user-attachments/assets/126273b0-68a6-41c4-85a6-8db6cf2bd595) ![AppResults](https://github.com/user-attachments/assets/15018a78-d763-41c9-ae4e-45e9b2cdae53)


