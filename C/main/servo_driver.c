// Libraries Licensed and provided by Espressif Systems
// Written by: Brandon Crudele, 2/26/2025
// Description: Controls camera rotation system
// Source: https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/mcpwm.html, https://github.com/espressif/esp-idf/tree/v5.2.5 

#include "servo.h"

// Mapping function:
static inline uint32_t map_value(int angle) {
    return (angle - SERVO_MIN_DEGREE) * (SERVO_MAX_PULSEWIDTH_US - SERVO_MIN_PULSEWIDTH_US) / (SERVO_MAX_DEGREE - SERVO_MIN_DEGREE) + SERVO_MIN_PULSEWIDTH_US;
}

mcpwm_cmpr_handle_t servo_init(void) {   

    // Config timer
    mcpwm_timer_handle_t timer = NULL;
    mcpwm_timer_config_t timer_config = {
        .group_id = 0,                                  // timer select (0 to 7 in our ESP32)
        .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,         // common clk
        .resolution_hz = SERVO_TIMEBASE_RESOLUTION_HZ,  // resolution
        .count_mode = MCPWM_TIMER_COUNT_MODE_UP,        // cnt up
        .period_ticks = SERVO_TIMEBASE_PERIOD,          // 20ms period -> (50Hz)
    };
    mcpwm_new_timer(&timer_config, &timer); // create timer

    // Config operator
    mcpwm_oper_handle_t operator = NULL;
    mcpwm_operator_config_t operator_config = {
        .group_id = 0, // same as timer we set
    };
    mcpwm_new_operator(&operator_config, &operator);   // create operator
    mcpwm_operator_connect_timer(operator, timer);     // connect operator to timer

    // Config comparator
    mcpwm_cmpr_handle_t comparator = NULL;
    mcpwm_comparator_config_t comparator_config = {
        .flags.update_cmp_on_tez = true,   // update comparator when the timer reaches zero
    };

    mcpwm_new_comparator(operator, &comparator_config, &comparator); // create comparator for operator

    // Config signal generator
    mcpwm_gen_handle_t generator = NULL;
    mcpwm_generator_config_t generator_config = {
        .gen_gpio_num = SERVO_PULSE_GPIO, // set gpio pin
    };

    mcpwm_new_generator(operator, &generator_config, &generator); // create signal generator

    // PWM setup
    int angle = 90; // starting angle
    
    mcpwm_comparator_set_compare_value(comparator, map_value(angle)); // set comparative signal to 90 degrees
    mcpwm_generator_set_action_on_timer_event(generator, MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)); // when angle requested, start moving (turn on pwm)
    mcpwm_generator_set_action_on_compare_event(generator, MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, comparator, MCPWM_GEN_ACTION_LOW)); // when angle is met, stop moving (turn off pwm)
    mcpwm_timer_enable(timer);                                  // enable pwm timer
    mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP);   // start timer

    return comparator;
}

void set_servo(mcpwm_cmpr_handle_t comparator, int angle) {
    mcpwm_comparator_set_compare_value(comparator, map_value(angle)); // change comparator to get new angle
    return;
}

// This contains the command to move the servo!!
// void app_main(void) {
//     int angle = 120;
//     mcpwm_cmpr_handle_t comp = servo_init();
//     set_servo(comp, angle);
// }