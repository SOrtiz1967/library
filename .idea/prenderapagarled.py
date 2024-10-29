import serial, time

# Conexión al puerto serial
arduino = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # Espera para que se establezca la conexión
print("se ejecuto correctamente")
arduino.write(b'5')
#arduino.write(b'A')

arduino.close()

