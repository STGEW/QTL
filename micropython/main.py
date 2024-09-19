from time import ticks_diff, ticks_us
from machine import UART, Pin
import os

from consts import UNDER_DEBUG
from consts import LOOP_PERIOD_USEC
from consts import PIN_IMU_SDA, PIN_IMU_SCL

from mpu_6050_driver import init_mpu6050
from rc import RC
from quad_model import QuadModel


uart0 = UART(2, baudrate=115200, timeout_char=100)

# update pins
i2c_imu = I2C(
    1,
    scl=Pin(PIN_IMU_SCL),
    sda=Pin(PIN_IMU_SDA),
    freq=400000)
imu = MPU6050(i2c_imu)
rc = RC()
model = QuadModel(imu)


def init_uart():
    # os.dupterm(uart0, 0)
    pass


def init():
    print(f'Run init')
    init_uart()
    print('Start calibrate IMU')
    imu.calibrate()
    print('IMU calibration is finished')


def loop():
    last_t = ticks_us()
    inputs = rc.read()

    targets = model.convert(inputs)
    # set motors values to targets
    x, y = run_joystick_task()
    if UNDER_DEBUG:
        data = uart0.readline()
        if data:
            # print(f"Read from UART data: {data}")
            x, y = data.decode('utf-8').split(' ')
            x = int(x)
            y = int(y)
    print(f'joystick: {x} {y}')
    run_rf_tx_task(x, y)
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
