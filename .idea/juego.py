import numpy as np
import cv2
import serial, time
# Capturando video a través de la webcam
webcam = cv2.VideoCapture(0)
if not webcam.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()
 
 
def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Coordenadas: ({x}, {y})')
 
# Set mouse callback
cv2.namedWindow("Multiple Color Detection in Real-Time")
cv2.setMouseCallback("Multiple Color Detection in Real-Time", get_coordinates)
 
 
# Bucle principal
while True:
    # Leyendo el video desde la webcam en frames de imagen
    ret, imageFrame = webcam.read()
    if not ret:
        print("Error: No se pudo leer el frame.")
        break
    # Convertir el frame a espacio de color HSV
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)
 
    # Definir rangos de color y crear máscaras
    red_lower = np.array([136, 87, 111], np.uint8)
    red_upper = np.array([180, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)
 
    green_lower = np.array([25, 100, 72], np.uint8)
    green_upper = np.array([102, 255, 255], np.uint8)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)
 
    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)
 
    # Dilation para cada color
    kernel = np.ones((5, 5), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)
 
    # Encontrar contornos y dibujar
    for color_mask, color_name, color_bgr in [
        (red_mask, "Red Colour", (0, 0, 255)),
        (green_mask, "Green Colour", (0, 255, 0)),
        (blue_mask, "Blue Colour", (255, 0, 0))
    ]:
        contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 300:
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), color_bgr, 2)
                cv2.putText(imageFrame, color_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color_bgr)
 
                # Comprobar si el contorno está en la coordenada (397, 276)
                if color_name == "Green Colour":
                    # Verificar si la coordenada está dentro del área del contorno
                    if x <= 397 <= x + w and y <= 276 <= y + h:
                        print("verde en tal coordenada")  # Imprimir en la terminal si se detecta verde en la coordenada
                        # Conexión al puerto serial
                        arduino = serial.Serial('COM8', 9600, timeout=1)
                        time.sleep(0.5)  # Espera para que se establezca la conexión
                        print("se ejecuto correctamente")
                        arduino.write(b'1')
                        #arduino.write(b'A')
                        arduino.close()
                                # Comprobar si el contorno está en la coordenada (397, 276)
                if color_name == "Red Colour":
                    # Verificar si la coordenada está dentro del área del contorno
                    if x <= 1808 <= x + w and y <= 124 <= y + h:
                        print("verde en tal coordenada")  # Imprimir en la terminal si se detecta verde en la coordenada
 
                # Comprobar si el contorno está en la coordenada (397, 276)
                if color_name == "Green Colour":
                    # Verificar si la coordenada está dentro del área del contorno
                    if x <= 397 <= x + w and y <= 276 <= y + h:
                        print("verde en tal coordenada")  # Imprimir en la terminal si se detecta verde en la coordenada
 
 
    # Mostrar el resultado
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame)
 
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
 
# Liberar recursos
webcam.release()
cv2.destroyAllWindows()
 