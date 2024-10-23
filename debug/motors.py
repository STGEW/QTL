import logging
from consts import DATA_DIR

MOTOR_FILE_PATH = f'../{DATA_DIR}/motor.txt'

logger = logging.getLogger(__name__)


class Motors:

    def __init__(self):
        with open(MOTOR_FILE_PATH, 'w') as f:
            f.write("")

    def apply(self, motor_values):
        l = " ".join(motor_values)
        MOTOR_FILE_PATH.write(l)
        logger.info(f'Target motor values: "{l}"')
