import serial

def send_command(angle):
    COM_PORT = "COM3"
    ser = serial.Serial(COM_PORT, 115200, timeout=1)

    # while True:
    # key = input("Input ")
    ser.write(f"{angle}\n".encode())
        #response = ser.readline().decode().strip()
        #print("ESP32 Response:", response)


def lcd_set(status):
    if status == "locked_on":
        send_command(200)
    elif status == "locked_off":
        send_command(300)
    elif status == "recording_on":
        send_command(400)
    elif status  == "recodirng_off":
        send_command(500)
    
