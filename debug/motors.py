MOTOR_FILE_PATH = '../data/motor.txt'


class Motors:

    def __init__(self):
        with open(MOTOR_FILE_PATH, 'w') as f:
            f.write("")

    def apply(self, motor_values):
        MOTOR_FILE_PATH.write(" ".join(motor_values))
