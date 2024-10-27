import serial
import time

# Configura la conexión serial
ser = serial.Serial(
    port='COM8',  # Reemplaza 'COM3' por el puerto serial de tu dispositivo
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Función para encender el LED
def encender_led():
    ser.write(b'1')  # Envía el valor '1' para encender el LED

# Función para apagar el LED
def apagar_led():
    ser.write(b'0')  # Envía el valor '0' para apagar el LED

# Programa principal
while True:
    encender_led()
    print("LED encendido")
    ser.flush()  # Asegura que se envíen todos los datos
    
    # Espera 2 segundos
    time.sleep(2)

    apagar_led()
    print("LED apagado")
    ser.flush()  # Asegura que se envíen todos los datos
    
    # Espera 2 segundos
    time.sleep(2)
