from machine import Pin, PWM
import time

def map_value(value, from_min, from_max, to_min, to_max):
    return to_min + (value - from_min) * (to_max - to_min) // (from_max - from_min)

class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=50)
    
    def set_angle(self, angle, curr_angle):
        pulse_width = map_value(angle, 0, 180, 500, 2600)  # Convert to microseconds
        duty = int((pulse_width / 20000) * 1023)  # Convert to duty cycle formula
        self.pwm.duty(duty)
        time.sleep((abs(curr_angle - angle) / 180) * 3)  # sleep time based on angle (0-3 seconds)
