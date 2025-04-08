// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Main File

#include <stdio.h>
#include <stdlib.h>
#include "uart.h"
#include "servo.h"
#include "lcd.c" // make this a header

void app_main(void) {
    uart_config();
    mcpwm_cmpr_handle_t comp = servo_init();
    system_runtime.hours = 0;
    system_runtime.minutes = 0;
    system_runtime.seconds = -1;
    lcd();
    while (true) {
        char* command = uart_com();
        printf("%s", command);
        set_servo(comp, atoi(command));
        servo_movement = atoi(command);
    }
}