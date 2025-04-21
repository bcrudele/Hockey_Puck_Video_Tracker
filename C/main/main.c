// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 4/14/2025
// Description: Main File

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "uart.h"
#include "servo.h"
#include "lcd.c" // make this a header

#define BLINK_GPIO 27 // ON LED

// ledger:
// 200 -> lock ON
// 300 -> lock OFF
// 400 -> recording ON
// 500 -> recording OFF

void app_main(void) {
    // LED:
    gpio_reset_pin(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(BLINK_GPIO, 1); // turn on LED?

    // UART:
    uart_config();

    // SERVO:
    mcpwm_cmpr_handle_t comp = servo_init();

    // LCD:
    system_runtime.hours = 0;
    system_runtime.minutes = 0;
    system_runtime.seconds = -1;
    lcd();

    while (true) {
        int command = atoi(uart_com());
        
        if (command <= 180 && command >= 0) {
             set_servo(comp, command);
             servo_movement = command;
        }
        else {
            switch (command)
            {
            case 200: lock = true; break;
            case 300: lock = false; break;
            case 400: recording = true; break;
            case 500: recording = false; break;
            
            default: break;
            }
        }
    }
}