from machine import Pin, SPI
import time
import ili934x
import _thread
from servo_driver import Servo
import uart_driver as UDR

servo = Servo(15)  # set servo to pin 15
MAX_SERVO_ANGLE = 180
MIN_SERVO_ANGLE = 0

# Define SPI Pins for ESP32 Feather V2
TFT_MOSI = 13  # Data (MOSI)
TFT_SCK = 14  # Clock (SCK)
TFT_CS = 5  # Chip Select (CS)
TFT_RST = 4  # Reset (RST)
TFT_DC = 33  # Data/Command (DC)
max_baud = 40000000
min_baud = 20000000
spi = SPI(1, baudrate=min_baud, polarity=0, phase=0, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI))  # initialize SPI
display = ili934x.ILI9341(spi, cs=Pin(5), dc=Pin(33), rst=Pin(4), w=320, h=240, r=0)  # initialize display

print("LCD Initialized Successfully!")

locked = 0  # [binary] locked/locked lost (from laptop)
servo_movement = MAX_SERVO_ANGLE//2
recording = 0  # [binary] recording active
system_temp = 72  # [analog range] Temperature from analog thermostat circuit
system_runtime = 0  # [s] time run

# Color List
WHITE = ili934x.color565(255, 255, 255)
BLACK = ili934x.color565(0, 0, 0)
RED = ili934x.color565(255, 0, 0)
GREEN = ili934x.color565(0, 255, 0)
BLUE = ili934x.color565(0, 0, 255)

### Coordinate syst. ###
b_start = 10
b_start_h = 40
b_width = 215
b_height = 10
b_sep = 30
right_al = b_width - 60
###

###
BAUD = 9600
RX_PIN = 7
###

def draw_gui():
    display.text("System Status", 80, 10, WHITE)
    
    # Create black bars
    for bar in range(0, 5):
        display.fill_rectangle(b_start, b_start_h + (b_sep * bar), b_width, b_height, BLACK)
        
    display.text("Locked:", b_start, 40, WHITE)
    display.text("Servo:", b_start, 70, WHITE)
    display.text("Recording:", b_start, 100, WHITE)
    display.text("Sys Temp:", b_start, 130, WHITE)
    display.text("Runtime:", b_start, 160, WHITE)

def update_display():
    print("update_display thread active")
    global servo_movement
    system_runtime = 0
    while True:
        display.text("Locked" if locked else "Unlocked", right_al, 40, GREEN if locked else RED)
        display.text(f"{servo_movement}", right_al, 70, WHITE)
        display.text("ON" if recording else "OFF", right_al, 100, GREEN if recording else RED)
        display.text(f"{system_temp}F", right_al, 130, WHITE)
        display.text(f"{system_runtime}s", right_al, 160, WHITE)
        system_runtime += 1  # simulate runtime increasing
        time.sleep(1)
        
def update_servo(angle):
    global servo_movement  # access the global variable
    curr_angle = servo_movement
    servo.set_angle(angle, curr_angle)

def update_command(uart):
    print("update_command thread active")
    global servo_movement
    while True:
        try:
            command = UDR.uart_com(uart)
            if command is None:
                continue  # when no commands
            
            command = command.strip() # remove spaces (just incase)
            
            if command.isdigit():  # valid number check
                command = int(command)
                if MIN_SERVO_ANGLE <= command <= MAX_SERVO_ANGLE:
                    update_servo(command)
            else:
                print(f"Invalid command received: {command}") # for bad commands
                
        except Exception as e:
            print(f"Error in update_command: {e}") # error catcher
            
# Initialize GUI
draw_gui()
time.sleep(2) # decrease boot errors?
_thread.start_new_thread(update_display, ())

# Initialize UART
uart = UDR.uart_init(BAUD,RX_PIN)
_thread.start_new_thread(update_command, (uart,))

update_servo(MAX_SERVO_ANGLE//2) # start pos.