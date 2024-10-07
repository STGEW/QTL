from .debug.i2c import I2C
from .debug.motors import Motors
from .debug.mpu_6050_driver import MPU6050
from .debug.rc import RC
from quad_model import QuadModel


i2c_imu = I2C(
    1,
    scl=None,
    sda=None,
    freq=400000)
imu = MPU6050(i2c_imu)
rc = RC()
model = QuadModel()
motors = Motors()


def loop():
    inputs = rc.read()
    imu_vals = imu.read_calib()
    mot = model.convert(inputs, imu_vals)


def main():
    while True:
    	loop()

main()
