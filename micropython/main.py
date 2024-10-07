from consts import UNDER_DEBUG

from machine import UART, Pin

from time import ticks_diff, ticks_us
import os

from consts import LOOP_PERIOD_USEC
from consts import PIN_IMU_SDA, PIN_IMU_SCL

from rc import RC
from quad_model import QuadModel
from motors import Motors

uart0 = UART(
    2,
    baudrate=115200)

# update pins
i2c_imu = I2C(
    1,
    scl=Pin(PIN_IMU_SCL),
    sda=Pin(PIN_IMU_SDA),
    freq=400000)
imu = MPU6050(i2c_imu)
rc = RC()
model = QuadModel()
motors = Motors()


def init_uart():
    os.dupterm(uart0, 0)
    pass


def init():
    print(f'Run init')
    init_uart()
    if not UNDER_DEBUG:
        print('Start calibrate IMU')
        imu.calibrate()
        print('IMU calibration is finished')


def loop():
    last_t = ticks_us()
    if UNDER_DEBUG:
        print("Enter RC values in format: 1_ch 2_ch 3_ch 4_ch")
        data = uart0.readline()
        v = data.split(" ")
        v = [float(k) for k in v]
        inputs = {
            '1': v[0], '2': v[1],
            '3': v[2], '4': v[3],
            '5': 0.0, '6': 0.0
        }
    else:
        inputs = rc.read()
    if UNDER_DEBUG:
        print("Enter IMU values in format: acc_x acc_y acc_z gyro_x gyro_y gyro_z")
        data = uart0.readline()
        v = data.split(" ")
        v = [float(k) for k in v]
        imu_vals = {
            'temp': 36.6,
            'acc': {'x': v[0], 'y': v[1], 'z': v[2]},
            'gyro': {'x': v[3], 'y': v[4], 'z': v[5]},
        }
    else:
        imu_vals = imu.read_calib()
    
    mot = model.convert(inputs, imu_vals)
    # set motors values to targets
   
    print(f'Motor values: {mot[0]} {mot[1]} {mot[2]} {mot[3]}')
    return last_t


def main():
    init()
    # variable to track loop call
    last_t = ticks_us()

    while True:
        cur_t = ticks_us()
        if ticks_diff(cur_t, last_t) > LOOP_PERIOD_USEC:
            last_t = loop()

main()
