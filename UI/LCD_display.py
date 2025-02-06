from machine import Pin, SPI
import time
import ili934x

# Define SPI Pins for ESP32 Feather V2
TFT_MOSI = 13  # Data (MOSI)
TFT_SCK  = 14  # Clock (SCK)
TFT_CS   = 5   # Chip Select (CS)
TFT_RST  = 4   # Reset (RST)
TFT_DC   = 33  # Data/Command (DC)

spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI)) # initialize SPI
display = ili934x.ILI9341(spi, cs=Pin(5), dc=Pin(33), rst=Pin(4)) # initialize display

print("LCD Initialized Successfully!")

# Set up default values for the display
puck_position = (150, 120)  # Example puck position (x, y)  (get rid of this later)
frame_rate = 30  # Example frame rate in FPS                (get rid of this later)
battery_level = 85  # Example battery level in percentage   (get rid of this later)

# 

# Function to update the GUI with new information
def update_gui():
    # Display puck position
    display.text(f"Puck Position: X={puck_position[0]} Y={puck_position[1]}", 10, 20, color=ili934x.color565(255, 255, 255))
    display.pixel(puck_position[0], puck_position[1], color=ili934x.color565(255,255,255))
    #display.fill_rectangle(puck_position[0], puck_position[1], puck_position[0],puck_position[1], color=ili934x.color565(255,255,255)) [has bugs]
    # Display frame rate
    display.text(f"Frame Rate: {frame_rate} FPS", 10, 40, color=ili934x.color565(255, 255, 255))

    # Display battery level
    display.text(f"Battery: {battery_level}%", 10, 60, color=ili934x.color565(255, 255, 255))

# Main loop to simulate updates
while True:
    update_gui()
    time.sleep(0.5)  # Update every second

    # Simulate changes to the values
    puck_position = (puck_position[0] + 1, puck_position[1] + 1)  # Move puck position
    if frame_rate < 60:
        frame_rate += 1  # Increase frame rate for simulation
    if battery_level > 0:
        battery_level -= 1  # Simulate battery draining