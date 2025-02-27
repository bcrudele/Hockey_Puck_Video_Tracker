// Libraries licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Controls UART communication between PC & MCU
// Source: https://github.com/espressif/esp-idf/tree/v5.2.5, https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html

#include "uart.h"

char* uart_com() {
    uint8_t data[BUF_SIZE];
    // wait for bytes:
    while (true) {
        int len = uart_read_bytes(UART_PORT_NUM, data, BUF_SIZE, 100 / portTICK_PERIOD_MS); // "100/portTick..." recommended by docs.
        if (len > 0) {
            data[len] = '\0';
            char* com = (char*)data;
            // printf("RX: %s\n", com);
            return com;
        };
    }
}

void uart_config() {
    // Config UART
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT
    };

    uart_param_config(UART_PORT_NUM, &uart_config);
    uart_set_pin(UART_PORT_NUM, UART_TX_PIN, UART_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    uart_driver_install(UART_PORT_NUM, BUF_SIZE * 2, 0, 0, NULL, 0);
}

// This contains the command use UART!!
// void app_main(void) {
//     uart_config();
//     while (true) {
//         char* command = uart_com();
//         printf("%s", command);
//     }
// }
