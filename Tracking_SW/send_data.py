import serial

def send_command(angle):
    # COM_PORT = "COM4"
    # ser = serial.Serial(COM_PORT, 115200, timeout=1)

    # # while True:
    # # key = input("Input ")
    # ser.write(f"{angle}\n".encode())
    #     #response = ser.readline().decode().strip()
    #     #print("ESP32 Response:", response)
    print("move servo")