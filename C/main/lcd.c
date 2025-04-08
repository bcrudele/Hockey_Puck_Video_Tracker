/* SPI Master example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
// #include "decode_image.h"
// #include "pretty_effect.h"
#include "esp_timer.h"
#include "esp_log.h"

// static const char *TAG = "timer_example";

// static int64_t timer_interval_us = 1000000; // 1 second in microseconds
// static int system_runtime = 0;

// static void timer_callback(void *arg) {
//     system_runtime++;
//     ESP_LOGI(TAG, "my_var: %d", system_runtime);
// }

/*
 This code displays some fancy graphics on the 320x240 LCD on an ESP-WROVER_KIT board.
 This example demonstrates the use of both spi_device_transmit as well as
 spi_device_queue_trans/spi_device_get_trans_result and pre-transmit callbacks.

 Some info about the ILI9341/ST7789V: It has an C/D line, which is connected to a GPIO here. It expects this
 line to be low for a command and high for data. We use a pre-transmit callback here to control that
 line: every transaction has as the user-definable argument the needed state of the D/C line and just
 before the transaction is sent, the callback will set this line to the correct state.
*/

#define LCD_HOST    HSPI_HOST

#define PIN_NUM_MISO 25  // NOT NEEDED 
#define PIN_NUM_MOSI 13
#define PIN_NUM_CLK  14
#define PIN_NUM_CS   5

#define PIN_NUM_DC   33
#define PIN_NUM_RST  4
#define PIN_NUM_BCKL 1 // NOT NEEDED 

//To speed up transfers, every SPI transfer sends a bunch of lines. This define specifies how many. More means more memory use,
//but less overhead for setting up / finishing transfers. Make sure 240 is dividable by this.
#define PARALLEL_LINES 40  // this has to be the GUI_HEIGHT (240) // VARIABLES (include hello world)
#define GUI_WIDTH 180       // backdrop for the numbers & text
#define GUI_HEIGHT 240
#define GUI_X 0
#define GUI_Y 0
#define GUI_VARS 5
#define GUI_VAR_OFFSET 100
#define GUI_NAME_OFFSET 10

// 0x1234 turns into 0x3412
#define BORDER_COLOR 0x0F0F
#define TEXT_COLOR 0xFFFF
#define BACKGROUND_COLOR 0x0000
#define TEXT_BG_COLOR 0x8608
#define GREEN         0xe007
#define RED           0x00f8
#define BLUE          0x1f00

/*
 The LCD needs a bunch of command/argument values to be initialized. They are stored in this struct.
*/
typedef struct {
    uint8_t cmd;
    uint8_t data[16];
    uint8_t databytes; //No of data in data; bit 7 = delay after set; 0xFF = end of cmds.
} lcd_init_cmd_t;

typedef enum {
    LCD_TYPE_ILI = 1,
    LCD_TYPE_ST,
    LCD_TYPE_MAX,
} type_lcd_t;

struct runtime_struct {
    int hours;
    int minutes;
    int seconds;
};

void draw_rectangle(uint16_t *buffer, int x, int y, int width, int height, uint16_t color) {
    for (int j = 0; j < height; j++) {
        for (int i = 0; i < width; i++) {
            int display_y = y + j;
            if (display_y >= 0 && display_y < 240 && x + i >=0 && x + i < 320) {
                buffer[display_y % PARALLEL_LINES * 320 + x + i] = color;
            }
        }
    }
}
void draw_char(uint16_t *buffer, int x, int y, char c, uint16_t color, int font_size) {
    if (c >= '0' && c <= '9') {
        static const uint8_t digits[][7] = {
            {0x1F, 0x11, 0x11, 0x11, 0x1F, 0x00, 0x00}, // 0
            {0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x00}, // 1
            {0x1F, 0x01, 0x1F, 0x10, 0x1F, 0x00, 0x00}, // 2
            {0x1F, 0x01, 0x1F, 0x01, 0x1F, 0x00, 0x00}, // 3
            {0x09, 0x09, 0x1F, 0x01, 0x01, 0x00, 0x00}, // 4
            {0x1F, 0x10, 0x1F, 0x01, 0x1F, 0x00, 0x00}, // 5
            {0x1F, 0x10, 0x1F, 0x11, 0x1F, 0x00, 0x00}, // 6
            {0x1F, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00}, // 7
            {0x1F, 0x11, 0x1F, 0x11, 0x1F, 0x00, 0x00}, // 8
            {0x1F, 0x11, 0x1F, 0x01, 0x1F, 0x00, 0x00}  // 9
        };

        const uint8_t *digit = digits[c - '0'];
        for (int row = 0; row < 7 * font_size; row++) {
            for (int col = 0; col < 5 * font_size; col++) {
                if ((digit[row / font_size] >> (4 - (col / font_size))) & 1) {
                    for (int pixel_row = 0; pixel_row < font_size; pixel_row++) {
                        for (int pixel_col = 0; pixel_col < font_size; pixel_col++) {
                            int pixel_x = x + col;
                            int pixel_y = y + row;
                            if (pixel_x >= 0 && pixel_x < 320 && pixel_y >= 0 && pixel_y < 240) {
                                buffer[(pixel_y % PARALLEL_LINES) * 320 + pixel_x] = color;
                            }
                        }
                    }
                }
            }
        }
    } else if (c >= 'A' && c <= 'Z') { // Add support for uppercase letters
        static const uint8_t letters[][7] = {
            {0x0E, 0x11, 0x1F, 0x11, 0x11, 0x00, 0x00}, // A
            {0x1F, 0x11, 0x1F, 0x11, 0x1F, 0x00, 0x00}, // B
            {0x1E, 0x11, 0x11, 0x11, 0x1E, 0x00, 0x00}, // C
            {0x1E, 0x11, 0x11, 0x11, 0x1E, 0x00, 0x00}, // D
            {0x1F, 0x10, 0x1F, 0x10, 0x1F, 0x00, 0x00}, // E
            {0x1F, 0x10, 0x1F, 0x10, 0x10, 0x00, 0x00}, // F
            {0x1E, 0x11, 0x17, 0x11, 0x1E, 0x00, 0x00}, // G
            {0x11, 0x11, 0x1F, 0x11, 0x11, 0x00, 0x00}, // H
            {0x1F, 0x04, 0x04, 0x04, 0x1F, 0x00, 0x00}, // I
            {0x0F, 0x02, 0x02, 0x02, 0x1E, 0x00, 0x00}, // J
            {0x11, 0x12, 0x14, 0x18, 0x11, 0x00, 0x00}, // K
            {0x10, 0x10, 0x10, 0x10, 0x1F, 0x00, 0x00}, // L
            {0x11, 0x1B, 0x15, 0x11, 0x11, 0x00, 0x00}, // M
            {0x11, 0x19, 0x15, 0x13, 0x11, 0x00, 0x00}, // N
            {0x1F, 0x11, 0x11, 0x11, 0x1F, 0x00, 0x00}, // O
            {0x1F, 0x11, 0x1F, 0x10, 0x10, 0x00, 0x00}, // P
            {0x1E, 0x11, 0x15, 0x12, 0x1D, 0x00, 0x00}, // Q
            {0x1F, 0x11, 0x1F, 0x18, 0x14, 0x00, 0x00}, // R
            {0x1E, 0x10, 0x1E, 0x01, 0x1E, 0x00, 0x00}, // S
            {0x1F, 0x04, 0x04, 0x04, 0x04, 0x00, 0x00}, // T
            {0x11, 0x11, 0x11, 0x11, 0x1E, 0x00, 0x00}, // U
            {0x11, 0x11, 0x0A, 0x04, 0x04, 0x00, 0x00}, // V
            {0x11, 0x11, 0x15, 0x15, 0x0A, 0x00, 0x00}, // W
            {0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00, 0x00}, // X
            {0x11, 0x0A, 0x04, 0x04, 0x04, 0x00, 0x00}, // Y
            {0x1F, 0x08, 0x04, 0x02, 0x1F, 0x00, 0x00}  // Z
        };

        const uint8_t *letter = letters[c - 'A'];
        for (int row = 0; row < 7 * font_size; row++) {
            for (int col = 0; col < 5 * font_size; col++) {
                if ((letter[row / font_size] >> (4 - (col / font_size))) & 1) {
                    for (int pixel_row = 0; pixel_row < font_size; pixel_row++) {
                        for (int pixel_col = 0; pixel_col < font_size; pixel_col++) {
                            int pixel_x = x + col;
                            int pixel_y = y + row;
                            if (pixel_x >= 0 && pixel_x < 320 && pixel_y >= 0 && pixel_y < 240) {
                                buffer[(pixel_y % PARALLEL_LINES) * 320 + pixel_x] = color;
                            }
                        }
                    }
                }
            }
        }
    }
}

void draw_number(uint16_t *buffer, int x, int y, int number, uint16_t color, int font_size) {
    char num_str[16];
    sprintf(num_str, "%d", number);
    int num_len = strlen(num_str);
    for (int i = 0; i < num_len; i++) {
        draw_char(buffer, x + i * 6 * font_size, y, num_str[i], color, font_size);
    }
}

void draw_text(uint16_t *buffer, int x, int y, const char *text, uint16_t color, int font_size) {
    int text_len = strlen(text);
    for (int i = 0; i < text_len; i++) {
        draw_char(buffer, x + i * 6 * font_size, y, text[i], color, font_size);
    }
}

DRAM_ATTR static const lcd_init_cmd_t ili_init_cmds[]={
    /* Power contorl B, power control = 0, DC_ENA = 1 */
    {0xCF, {0x00, 0x83, 0X30}, 3},
    /* Power on sequence control,
     * cp1 keeps 1 frame, 1st frame enable
     * vcl = 0, ddvdh=3, vgh=1, vgl=2
     * DDVDH_ENH=1
     */
    {0xED, {0x64, 0x03, 0X12, 0X81}, 4},
    /* Driver timing control A,
     * non-overlap=default +1
     * EQ=default - 1, CR=default
     * pre-charge=default - 1
     */
    {0xE8, {0x85, 0x01, 0x79}, 3},
    /* Power control A, Vcore=1.6V, DDVDH=5.6V */
    {0xCB, {0x39, 0x2C, 0x00, 0x34, 0x02}, 5},
    /* Pump ratio control, DDVDH=2xVCl */
    {0xF7, {0x20}, 1},
    /* Driver timing control, all=0 unit */
    {0xEA, {0x00, 0x00}, 2},
    /* Power control 1, GVDD=4.75V */
    {0xC0, {0x26}, 1},
    /* Power control 2, DDVDH=VCl*2, VGH=VCl*7, VGL=-VCl*3 */
    {0xC1, {0x11}, 1},
    /* VCOM control 1, VCOMH=4.025V, VCOML=-0.950V */
    {0xC5, {0x35, 0x3E}, 2},
    /* VCOM control 2, VCOMH=VMH-2, VCOML=VML-2 */
    {0xC7, {0xBE}, 1},
    /* Memory access contorl, MX=MY=0, MV=1, ML=0, BGR=1, MH=0 */
    {0x36, {0x28}, 1},
    /* Pixel format, 16bits/pixel for RGB/MCU interface */
    {0x3A, {0x55}, 1},
    /* Frame rate control, f=fosc, 70Hz fps */
    {0xB1, {0x00, 0x10}, 2},
    /* Enable 3G, disabled */
    {0xF2, {0x08}, 1},
    /* Gamma set, curve 1 */
    {0x26, {0x01}, 1},
    /* Positive gamma correction */
    {0xE0, {0x1F, 0x1A, 0x18, 0x0A, 0x0F, 0x06, 0x45, 0X87, 0x32, 0x0A, 0x07, 0x02, 0x07, 0x05, 0x00}, 15},
    /* Negative gamma correction */
    {0XE1, {0x00, 0x25, 0x27, 0x05, 0x10, 0x09, 0x3A, 0x78, 0x4D, 0x05, 0x18, 0x0D, 0x38, 0x3A, 0x1F}, 15},
    /* Column address set, SC=0, EC=0xEF */
    {0x2A, {0x00, 0x00, 0x00, 0xEF}, 4},
    /* Page address set, SP=0, EP=0x013F */
    {0x2B, {0x00, 0x00, 0x01, 0x3f}, 4},
    /* Memory write */
    {0x2C, {0}, 0},
    /* Entry mode set, Low vol detect disabled, normal display */
    {0xB7, {0x07}, 1},
    /* Display function control */
    {0xB6, {0x0A, 0x82, 0x27, 0x00}, 4},
    /* Sleep out */
    {0x11, {0}, 0x80},
    /* Display on */
    {0x29, {0}, 0x80},
    {0, {0}, 0xff},
};

/* Send a command to the LCD. Uses spi_device_polling_transmit, which waits
 * until the transfer is complete.
 *
 * Since command transactions are usually small, they are handled in polling
 * mode for higher speed. The overhead of interrupt transactions is more than
 * just waiting for the transaction to complete.
 */
void lcd_cmd(spi_device_handle_t spi, const uint8_t cmd, bool keep_cs_active)
{
    esp_err_t ret;
    spi_transaction_t t;
    memset(&t, 0, sizeof(t));       //Zero out the transaction
    t.length=8;                     //Command is 8 bits
    t.tx_buffer=&cmd;               //The data is the cmd itself
    t.user=(void*)0;                //D/C needs to be set to 0
    if (keep_cs_active) {
      t.flags = SPI_TRANS_CS_KEEP_ACTIVE;   //Keep CS active after data transfer
    }
    ret=spi_device_polling_transmit(spi, &t);  //Transmit!
    assert(ret==ESP_OK);            //Should have had no issues.
}

/* Send data to the LCD. Uses spi_device_polling_transmit, which waits until the
 * transfer is complete.
 *
 * Since data transactions are usually small, they are handled in polling
 * mode for higher speed. The overhead of interrupt transactions is more than
 * just waiting for the transaction to complete.
 */
void lcd_data(spi_device_handle_t spi, const uint8_t *data, int len)
{
    esp_err_t ret;
    spi_transaction_t t;
    if (len==0) return;             //no need to send anything
    memset(&t, 0, sizeof(t));       //Zero out the transaction
    t.length=len*8;                 //Len is in bytes, transaction length is in bits.
    t.tx_buffer=data;               //Data
    t.user=(void*)1;                //D/C needs to be set to 1
    ret=spi_device_polling_transmit(spi, &t);  //Transmit!
    assert(ret==ESP_OK);            //Should have had no issues.
}

//This function is called (in irq context!) just before a transmission starts. It will
//set the D/C line to the value indicated in the user field.
void lcd_spi_pre_transfer_callback(spi_transaction_t *t)
{
    int dc=(int)t->user;
    gpio_set_level(PIN_NUM_DC, dc);
}

uint32_t lcd_get_id(spi_device_handle_t spi)
{
    // When using SPI_TRANS_CS_KEEP_ACTIVE, bus must be locked/acquired
    spi_device_acquire_bus(spi, portMAX_DELAY);

    //get_id cmd
    lcd_cmd(spi, 0x04, true);

    spi_transaction_t t;
    memset(&t, 0, sizeof(t));
    t.length=8*3;
    t.flags = SPI_TRANS_USE_RXDATA;
    t.user = (void*)1;

    esp_err_t ret = spi_device_polling_transmit(spi, &t);
    assert( ret == ESP_OK );

    // Release bus
    spi_device_release_bus(spi);

    return *(uint32_t*)t.rx_data;
}

//Initialize the display
void lcd_init(spi_device_handle_t spi)
{
    int cmd=0;
    const lcd_init_cmd_t* lcd_init_cmds;

    //Initialize non-SPI GPIOs
    gpio_config_t io_conf = {};
    io_conf.pin_bit_mask = ((1ULL<<PIN_NUM_DC) | (1ULL<<PIN_NUM_RST) | (1ULL<<PIN_NUM_BCKL));
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pull_up_en = true;
    gpio_config(&io_conf);

    //Reset the display
    gpio_set_level(PIN_NUM_RST, 0);
    vTaskDelay(100 / portTICK_PERIOD_MS);
    gpio_set_level(PIN_NUM_RST, 1);
    vTaskDelay(100 / portTICK_PERIOD_MS);

    //detect LCD type
    uint32_t lcd_id = lcd_get_id(spi);

    printf("LCD ID: %08"PRIx32"\n", lcd_id);
    printf("LCD ILI9341 initialization.\n");
    lcd_init_cmds = ili_init_cmds;

    //Send all the commands
    while (lcd_init_cmds[cmd].databytes!=0xff) {
        lcd_cmd(spi, lcd_init_cmds[cmd].cmd, false);
        lcd_data(spi, lcd_init_cmds[cmd].data, lcd_init_cmds[cmd].databytes&0x1F);
        if (lcd_init_cmds[cmd].databytes&0x80) {
            vTaskDelay(100 / portTICK_PERIOD_MS);
        }
        cmd++;
    }

    ///Enable backlight
    // gpio_set_level(PIN_NUM_BCKL, 0); // we don't need this, we have the backlight always on
}

/* To send a set of lines we have to send a command, 2 data bytes, another command, 2 more data bytes and another command
 * before sending the line data itself; a total of 6 transactions. (We can't put all of this in just one transaction
 * because the D/C line needs to be toggled in the middle.)
 * This routine queues these commands up as interrupt transactions so they get
 * sent faster (compared to calling spi_device_transmit several times), and at
 * the mean while the lines for next transactions can get calculated.
 */
static void send_lines(spi_device_handle_t spi, int ypos, uint16_t *linedata)
{
    esp_err_t ret;
    int x;
    //Transaction descriptors. Declared static so they're not allocated on the stack; we need this memory even when this
    //function is finished because the SPI driver needs access to it even while we're already calculating the next line.
    static spi_transaction_t trans[6];

    //In theory, it's better to initialize trans and data only once and hang on to the initialized
    //variables. We allocate them on the stack, so we need to re-init them each call.
    for (x=0; x<6; x++) {
        memset(&trans[x], 0, sizeof(spi_transaction_t));
        if ((x&1)==0) {
            //Even transfers are commands
            trans[x].length=8;
            trans[x].user=(void*)0;
        } else {
            //Odd transfers are data
            trans[x].length=8*4;
            trans[x].user=(void*)1;
        }
        trans[x].flags=SPI_TRANS_USE_TXDATA;
    }
    trans[0].tx_data[0] = 0x2A;             //Column Address Set
    trans[1].tx_data[0] = 0;                //Start Col High
    trans[1].tx_data[1] = 0;                //Start Col Low
    trans[1].tx_data[2] = (320 - 1) >> 8;   //End Col High
    trans[1].tx_data[3] = (320 - 1) & 0xff; //End Col Low
    trans[2].tx_data[0] = 0x2B;             //Page address set
    trans[3].tx_data[0] = ypos >> 8;        //Start page high
    trans[3].tx_data[1] = ypos & 0xff;      //start page low
    trans[3].tx_data[2] = (ypos + PARALLEL_LINES - 1) >> 8;     //end page high
    trans[3].tx_data[3] = (ypos + PARALLEL_LINES - 1) & 0xff;   //end page low
    trans[4].tx_data[0] = 0x2C;             //memory write
    trans[5].tx_buffer = linedata;          //finally send the line data
    trans[5].length = 320 * 2 * 8 * PARALLEL_LINES;  //Data length, in bits
    trans[5].flags = 0; //undo SPI_TRANS_USE_TXDATA flag

    //Queue all transactions.
    for (x=0; x<6; x++) {
        ret=spi_device_queue_trans(spi, &trans[x], portMAX_DELAY);
        assert(ret==ESP_OK);
    }

    //When we are here, the SPI driver is busy (in the background) getting the transactions sent. That happens
    //mostly using DMA, so the CPU doesn't have much to do here. We're not going to wait for the transaction to
    //finish because we may as well spend the time calculating the next line. When that is done, we can call
    //send_line_finish, which will wait for the transfers to be done and check their status.
}


static void send_line_finish(spi_device_handle_t spi)
{
    spi_transaction_t *rtrans;
    esp_err_t ret;
    //Wait for all 6 transactions to be done and get back the results.
    for (int x=0; x<6; x++) {
        ret=spi_device_get_trans_result(spi, &rtrans, portMAX_DELAY);
        assert(ret==ESP_OK);
        //We could inspect rtrans now if we received any info back. The LCD is treated as write-only, though.
    }
}

// Global variables for GUI updates
int servo_movement = 0;
bool lock = false;
int recording = 0;
int system_temp = 0;
struct runtime_struct system_runtime; // TIME
int frame = 0;
uint16_t *lines[2];

void timer_callback(void* arg) {
    spi_device_handle_t spi = (spi_device_handle_t)arg; // Retrieve SPI handle passed through 'arg'
    
    int spacing = GUI_HEIGHT / GUI_VARS;
    int sending_line = -1;
    int calc_line = 0;

    system_runtime.seconds++;
    if (system_runtime.seconds == 60) {
        system_runtime.minutes++;
        system_runtime.seconds = 0;
    }
    if (system_runtime.minutes == 60) {
        system_runtime.hours++;
        system_runtime.minutes = 0;
    }
    // Clear the buffer and draw GUI elements
    for (int y = 0; y < 240; y += PARALLEL_LINES) {
        if (frame < 6) {
        // Clear the buffer
        for (int i = 0; i < 320 * PARALLEL_LINES; i++) {
            lines[calc_line][i] = BACKGROUND_COLOR; // Black background
        }

        // Draw GUI background and elements
        draw_rectangle(lines[calc_line], GUI_X, GUI_Y, GUI_WIDTH, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish
        draw_rectangle(lines[calc_line], GUI_X, GUI_Y, 2, GUI_HEIGHT, BORDER_COLOR); // Left bar
        draw_rectangle(lines[calc_line], GUI_WIDTH, GUI_Y, 2, GUI_HEIGHT, BORDER_COLOR); // Right bar
        if (y == PARALLEL_LINES * 0) draw_rectangle(lines[calc_line], GUI_X, GUI_Y, GUI_WIDTH, 2, BORDER_COLOR); // Top bar
        if (y == PARALLEL_LINES * 5) draw_rectangle(lines[calc_line], GUI_X, GUI_HEIGHT-2, GUI_WIDTH, 2, BORDER_COLOR); // Bottom bar
        
        // Draw changing variables
        if (y == PARALLEL_LINES * 0) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 10, "ROLLER HOCKEY VIDEO TRACKER", TEXT_COLOR, 1);
        }
        else if (y == PARALLEL_LINES * 1) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "LOCK:", TEXT_COLOR, 2);
            if (lock) { draw_text(lines[calc_line], GUI_VAR_OFFSET, 0, "PAIRED", GREEN, 2); }
            else { draw_text(lines[calc_line], GUI_VAR_OFFSET, 0, "LOST", RED, 2); }
        }
        else if (y == PARALLEL_LINES * 2) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "SERVO:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES * 1, servo_movement, TEXT_COLOR, 2); // White number
        }
        else if (y == PARALLEL_LINES * 3) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "REC:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES * 2, recording, TEXT_COLOR, 2); // White number
        }
        else if (y == PARALLEL_LINES * 4) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "TEMP:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES * 3, system_temp, TEXT_COLOR, 2); // White number
        }
        else if (y == PARALLEL_LINES * 5) {
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "TIME:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES * 4, system_runtime.seconds, TEXT_COLOR, 2); // White number
        }
        frame++;
        // Send the lines to the display
        if (sending_line != -1) send_line_finish(spi);
        sending_line = calc_line;
        calc_line = (calc_line == 1) ? 0 : 1;
        send_lines(spi, y, lines[sending_line]);
        }
        else if (frame == 6){
            calc_line = 0;
            draw_rectangle(lines[calc_line], GUI_X+3, GUI_Y, GUI_WIDTH-3, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish

            // draw_text(lines[0], GUI_NAME_OFFSET, 0, "SERVO:", TEXT_COLOR, 2);
            // draw_number(lines[0], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES * 1, servo_movement, TEXT_COLOR, 2); // White number

            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "LOCK:", TEXT_COLOR, 2);
            if (lock) { draw_text(lines[calc_line], GUI_VAR_OFFSET, 0, "PAIRED", GREEN, 2); }
            else { draw_text(lines[calc_line], GUI_VAR_OFFSET, 0, "LOST", RED, 2); }
            send_lines(spi, PARALLEL_LINES, lines[0]); // Only send the updated line
            frame++;
        }
        else if (frame == 7) {
            
            calc_line = 1;
            draw_rectangle(lines[calc_line], GUI_X+3, PARALLEL_LINES * 1, GUI_WIDTH-3, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish
            
            //         // Update SERVO variable display (below LOCK)
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "SERVO:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + PARALLEL_LINES, servo_movement, TEXT_COLOR, 2);

            send_lines(spi, PARALLEL_LINES * 2, lines[calc_line]); // Only send the updated line
            frame++;


            vTaskDelay(pdMS_TO_TICKS(100)); // critical!
            
        }
        else if (frame == 8) {
            
            calc_line = 0;
            draw_rectangle(lines[calc_line], GUI_X+3, PARALLEL_LINES * 2, GUI_WIDTH-3, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish
            
            //         // Update SERVO variable display (below LOCK)
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "REC:", TEXT_COLOR, 2);
            if (recording) { draw_text(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 2), "ON", GREEN, 2); }
            else { draw_text(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 2), "OFF", RED, 2); }
            // draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 2), recording, TEXT_COLOR, 2); // for basic 1/0 

            send_lines(spi, PARALLEL_LINES * 3, lines[calc_line]); // Only send the updated line
            frame++;


            vTaskDelay(pdMS_TO_TICKS(100)); // critical!
            
        }
        else if (frame == 9) {
            
            calc_line = 0;
            draw_rectangle(lines[calc_line], GUI_X+3, PARALLEL_LINES * 3, GUI_WIDTH-3, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish
            
            //         // Update SERVO variable display (below LOCK)
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "TEMP:", TEXT_COLOR, 2);
            draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 3), system_temp, TEXT_COLOR, 2);

            send_lines(spi, PARALLEL_LINES * 4, lines[calc_line]); // Only send the updated line
            frame++;


            vTaskDelay(pdMS_TO_TICKS(100)); // critical!
            
        }
        else if (frame == 10) {
            
            calc_line = 0;
            draw_rectangle(lines[calc_line], GUI_X+3, PARALLEL_LINES * 4, GUI_WIDTH-3, GUI_HEIGHT, TEXT_BG_COLOR); // Blueish
            
            //         // Update SERVO variable display (below LOCK)
            draw_text(lines[calc_line], GUI_NAME_OFFSET, 0, "TIME:", TEXT_COLOR, 2);
            if (system_runtime.hours != 0) {
                if (system_runtime.seconds < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 65, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 50, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                }
                else {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 45, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                }
                if (system_runtime.minutes < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 30, GUI_Y + (PARALLEL_LINES * 4), system_runtime.minutes, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 15, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                } 
                else{
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 10, GUI_Y + (PARALLEL_LINES * 4), system_runtime.minutes, TEXT_COLOR, 2);
                }
                if (system_runtime.hours < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 4), system_runtime.hours, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET - 15, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                }
                else {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET - 30, GUI_Y + (PARALLEL_LINES * 4), system_runtime.hours, TEXT_COLOR, 2);
                }
            }
            else if (system_runtime.minutes != 0) {
                if (system_runtime.seconds < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 55, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 40, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                }
                else {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 35, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                }
                if (system_runtime.minutes < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 20, GUI_Y + (PARALLEL_LINES * 4), system_runtime.minutes, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 5, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                } 
                else{
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 4), system_runtime.minutes, TEXT_COLOR, 2);
                }
            } 
            else {
                if (system_runtime.seconds < 10) {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 15, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 4), 0, TEXT_COLOR, 2);
                }
                else {
                    draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
                }
            } 
            // else if (system_runtime.minutes != 0) {
            //     draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 25, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
            //     draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET + 0, GUI_Y + (PARALLEL_LINES * 4), system_runtime.minutes, TEXT_COLOR, 2);
            // }
            // else {
            //     draw_number(lines[calc_line], GUI_X + GUI_VAR_OFFSET, GUI_Y + (PARALLEL_LINES * 4), system_runtime.seconds, TEXT_COLOR, 2);
            // }
            draw_rectangle(lines[calc_line], GUI_X, GUI_HEIGHT-2, GUI_WIDTH, 2, BORDER_COLOR); // Bottom bar
            send_lines(spi, PARALLEL_LINES * 5, lines[calc_line]); // Only send the updated line
            frame = 6;


            vTaskDelay(pdMS_TO_TICKS(100)); // critical!
            
        }
    }

    // Update the variables
    // if (lock) { lock = false; }
    // else { lock = true; }
    // system_runtime++;
    // system_temp++;
}

// Setup the periodic timer
void setup_periodic_timer(spi_device_handle_t spi) {
    esp_timer_handle_t timer_handle;
    esp_timer_create_args_t timer_args = {
        .callback = timer_callback,
        .arg = (void*)spi,  // Pass 'spi' to the timer callback
        .name = "gui_update_timer"
    };

    ESP_ERROR_CHECK(esp_timer_create(&timer_args, &timer_handle));
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer_handle, 1000000));  // 1 second interval (1000000 microseconds)
}

void lcd(void)
{
    spi_device_handle_t spi;
    spi_bus_config_t buscfg={
        .miso_io_num=PIN_NUM_MISO,
        .mosi_io_num=PIN_NUM_MOSI,
        .sclk_io_num=PIN_NUM_CLK,
        .quadwp_io_num=-1,
        .quadhd_io_num=-1,
        .max_transfer_sz=PARALLEL_LINES*320*2+8
    };
    spi_device_interface_config_t devcfg={
        // .clock_speed_hz=26*1000*1000,        //Clock out at 26 MHz (overclock not needed for this project)
        .clock_speed_hz=10*1000*1000,           //Clock out at 10 MHz
        .mode=0,                                //SPI mode 0
        .spics_io_num=PIN_NUM_CS,               //CS pin
        .queue_size=7,                          //We want to be able to queue 7 transactions at a time
        .pre_cb=lcd_spi_pre_transfer_callback,  //Specify pre-transfer callback to handle D/C line
    };
    
    // Initialize the SPI bus
    spi_bus_initialize(LCD_HOST, &buscfg, SPI_DMA_CH_AUTO);

    // Attach the LCD to the SPI bus
    spi_bus_add_device(LCD_HOST, &devcfg, &spi);

    // Initialize the LCD
    lcd_init(spi);

    // allocate memory for line buffers,
    for (int i = 0; i < 2; i++) {
        if (lines[i] == NULL) {
            lines[i] = heap_caps_malloc(320 * PARALLEL_LINES * sizeof(uint16_t), MALLOC_CAP_DMA);
            assert(lines[i] != NULL);
        }
    }
    
    setup_periodic_timer(spi); // setup timer to update screen at 1 Hz
}
