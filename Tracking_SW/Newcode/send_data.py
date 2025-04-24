import serial

def send_command(angle):
    print(f"Sending angle: {angle}")
    # COM_PORT = "COM3"
    # ser = serial.Serial(COM_PORT, 115200, timeout=1)

    # while True:
    # key = input("Input ")
    # ser.write(f"{angle}\n".encode())
        #response = ser.readline().decode().strip()
        #print("ESP32 Response:", response)