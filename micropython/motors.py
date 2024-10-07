from consts import PIN_MOTORS


class Motors:
    
    def __init__(self):
        pass

    def apply(self, motor_values):
        for i in range(1, 5):
            j = str(i)
            print(f"Pin: {PIN_MOTORS[j]} will have value: {motor_values[j]}")
