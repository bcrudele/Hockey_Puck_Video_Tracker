import machine
from machine import Pin, UART               

def uart_test(RX_PIN):
    # See what UARTs are active
    try:
        uart0 = machine.UART(0)
        print("UART0 is available")
    except:
        print("UART0 is in use by the system")

    try:
        uart1 = machine.UART(1, baudrate=9600, rx=RX_PIN)
        print("UART1 is available")
    except:
        print("UART1 is in use by the system")

def uart_init(BAUD, RX_PIN):
    uart = machine.UART(1, baudrate=BAUD, rx=RX_PIN)
    print("ESP32 ready. Send '1' to turn ON LED, '0' to turn OFF.")
    return uart

def uart_com(uart):
    if uart.any():  # Check if data is available to read
        command = uart.read(1)  # Read 1 byte
        
        # Check if a valid byte was received
        if command:
            # Convert the byte to a string
            command_str = chr(command[0])  # Convert byte to character
            
            print(f"Received: {command_str}")
            # uart.write() may need later "LED ON"
            
            return command_str

