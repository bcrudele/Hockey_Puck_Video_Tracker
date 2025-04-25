import serial

def send_command(angle):
    COM_PORT = "COM3"
    ser = serial.Serial(COM_PORT, 115200, timeout=1)
    ser.write(f"{angle}\n".encode())


def lcd_set(status):
    if status == "locked_on":
        send_command(200)
    elif status == "locked_off":
        send_command(300)
    elif status == "recording_on":
        send_command(400)
    elif status  == "recording_off":
        send_command(500)