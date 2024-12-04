from machine import PWM


ESC_FREQ = 50
PIN_ESCs = {
    1: 13,
    2: 12,
    3: 14,
    4: 27
}


class ESCs:
    
    def __init__(self):
        self.esc = {}
        for i in range(1, 5):
            pin = PIN_ESCs[i]
            self.esc[i] = PWM(pin, freq=ESC_FREQ)

    def apply(self, motor_values):
        '''
        Motor values should be from 0 to 100% power

        '''
        for i in range(1, 5):
            v = motor_values[i]
            v_mcs = int(1000 + 1000 * v / 100)
            v_ns = 1000 * v_mcs
            # print("Motor: {} will have value mcsec: {} v_ns: {}".format(
            #     i, v_mcs, v_ns))
            self.esc[i].duty_ns(v_ns)
            
