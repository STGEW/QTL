import logging
from consts import DATA_DIR


IMU_FILE_PATH = f'../{DATA_DIR}/imu.txt'


logger = logging.getLogger(__name__)


class MPU6050:

    def __init__(self, i2c):
        self.data = []
        with open(IMU_FILE_PATH, 'r') as f:
            self.data = [line.strip() for line in f]

    def calibrate(self):
        pass

    def read_calib(self):
        if self.data:
            l = self.data.pop(0)
            logging.info(f"Data line: '{l}'")
            values = l.split(' ')
            logging.info(f"Values: '{values}'")
            values = [float(v) for v in values]
            d = {
                'temp': 36.6,
                'gyro': {
                    'x': values[0],
                    'y': values[1],
                    'z': values[2]
                },
                'acc': {
                    'x': values[3],
                    'y': values[4],
                    'z': values[5]  
                }
            }
            logger.info(f"IMU data: '{d}'")
            return d
        else:
            raise ValueError("No more data from IMU available")
