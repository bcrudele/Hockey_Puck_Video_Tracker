import serial

COM_PORT = "COM4"

ser = serial.Serial(COM_PORT, 9600, timeout=1)

while True:
    key = input("Input ")
    ser.write(f"{key}\n".encode())
    response = ser.readline().decode().strip()
    print("ESP32 Response:", response)