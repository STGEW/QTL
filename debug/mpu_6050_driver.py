IMU_FILE_PATH = '../data/imu.txt'


class MPU6050:

    def __init__(self, i2c):
        data = []
        with open(IMU_FILE_PATH, 'r') as f:
            for l in f.read():
                data.append(l)

    def calibrate(self):
        pass

    def read_calib(self):
        if data:
            values = data.pop(0).split(' ')
            values = [float(v) for v in values]
            data = {
                'temp': 36.6,
                'gyro': {
                    'x': values[0],
                    'y': values[1],
                    'z': values[2]
                },
                'accel': {
                    'x': values[3],
                    'y': values[4],
                    'z': values[5]  
                }
            }
            return data
        else:
            raise ValueError("No more data from IMU available")
