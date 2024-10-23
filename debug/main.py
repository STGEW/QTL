import logging
import time

from i2c import I2C
from motors import Motors
from mpu_6050_driver import MPU6050
from rc import RC
from quad_model import QuadModel


logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('/tmp/main.log')

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


i2c_imu = I2C(
    1,
    scl=None,
    sda=None,
    freq=400000)
imu = MPU6050(i2c_imu)
rc = RC()
model = QuadModel()
motors = Motors()

logger.info("TEST")


def loop(dt):
    inputs = rc.read()
    logger.info(f"Inputs: '{inputs}'")
    imu_vals = imu.read_calib()
    logger.info(f"IMU values: '{imu_vals}'")
    mot = model.convert(inputs, imu_vals, dt)


def main():
    counter = 1

    last_t = time.time_ns()

    while True:
        logger.info("----------------------")
        logger.info(f"Counter: '{counter}'")
        dt = time.time_ns() - last_t
        last_t = time.time_ns()
        loop(dt)
        counter += 1


main()
