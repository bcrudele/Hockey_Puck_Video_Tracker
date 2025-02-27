// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Header for uart_driver.c

#include <stdio.h>
#include "driver/uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define UART_PORT_NUM UART_NUM_1  // Using UART1
#define UART_TX_PIN   8           // TX pin (not needed)
#define UART_RX_PIN   7           // RX pin
#define UART_BAUD     115200      // Baud rate
#define BUF_SIZE      256         // Buffer size for UART

void uart_config(void);
char* uart_com(void);

// UART Struct: 
/*
typedef struct {
    int baud_rate;                      !< UART baud rate
    uart_word_length_t data_bits;       !< UART byte size
    uart_parity_t parity;               !< UART parity mode
    uart_stop_bits_t stop_bits;         !< UART stop bits
    uart_hw_flowcontrol_t flow_ctrl;    !< UART HW flow control mode (cts/rts)
    uint8_t rx_flow_ctrl_thresh;        !< UART HW RTS threshold
    uart_sclk_t source_clk;             !< UART source clock selection
} uart_config_t;
*/
