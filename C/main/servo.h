// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Header for servo_driver.c

#include "freertos/FreeRTOS.h"         
#include "freertos/task.h"             
#include "driver/mcpwm_prelude.h"

static inline uint32_t map_value(int);
mcpwm_cmpr_handle_t servo_init(void);
void set_servo(mcpwm_cmpr_handle_t, int);

// Servo Params.
#define SERVO_MIN_PULSEWIDTH_US 500   // 0 degress
#define SERVO_MAX_PULSEWIDTH_US 2500  // 180 degrees
#define SERVO_MIN_DEGREE        0     // min servo angle
#define SERVO_MAX_DEGREE        180   // max servo angle
#define SERVO_PULSE_GPIO             15        // PWM Output PIN
#define SERVO_TIMEBASE_RESOLUTION_HZ 1000000   // Timer resolution -> 1MHz, which means 1 tick -> 1us
#define SERVO_TIMEBASE_PERIOD        20000     // Total period of the PWM signal (common: 20ms)

// Servo config struct:
/*
typedef struct {
    int group_id;                        !< Specify from which group to allocate the MCPWM timer
    mcpwm_timer_clock_source_t clk_src;  !< MCPWM timer clock source
    uint32_t resolution_hz;              !< Counter resolution in Hz, ranges from around 300KHz to 80MHz.
                                              The step size of each count tick equals to (1 / resolution_hz) seconds
    mcpwm_timer_count_mode_t count_mode; !< Count mode
    uint32_t period_ticks;               !< Number of count ticks within a period
    int intr_priority;                   !< MCPWM timer interrupt priority,
                                              if set to 0, the driver will try to allocate an interrupt with a relative low priority (1,2,3)
    struct {
        uint32_t update_period_on_empty: 1; Whether to update period when timer counts to zero
        uint32_t update_period_on_sync: 1;  !< Whether to update period on sync event
    } flags;                                !< Extra configuration flags for timer
} mcpwm_timer_config_t;
*/