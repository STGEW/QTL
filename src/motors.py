from machine import PWM
from consts import PIN_MOTORS, ESC_FREQ


class Motors:
    
    def __init__(self):
        self.esc = {}
        for i in range(1, 5):
            pin = PIN_MOTORS[i]
            self.esc[i] = PWM(pin, freq=ESC_FREQ)

    def apply(self, motor_values):
        '''
        Motor values should be from 0 to 100% power

        '''
        for i in range(1, 5):
            v = motor_values[i]
            v_mcs = int(1000 + 1000 * v / 100)
            v_ns = 1000 * v_mcs
            print(f"Motor: {i} will have value mcsec: {v_mcs} nsec: {v_ns}")
            self.esc[i].duty_ns(v_ns)
            
