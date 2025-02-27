// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Main File

#include <stdio.h>
#include <stdlib.h>
#include "uart.h"
#include "servo.h"

void app_main(void) {
    uart_config();
    mcpwm_cmpr_handle_t comp = servo_init();
    while (true) {
        char* command = uart_com();
        printf("%s", command);
        set_servo(comp, atoi(command));
    }
}