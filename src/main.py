from consts import UNDER_DEBUG

from machine import UART, Pin, I2C

from time import ticks_diff, ticks_us, sleep
import os

from consts import LOOP_PERIOD_USEC
from consts import PIN_MOTORS

from ibus_parser import IBUS, RC_SUCCESS
# from quad_model import QuadModel
from motors import Motors
from mpu_6050_driver import MPU6050


u_2 = UART(
    2,
    baudrate=115200,
    timeout=0)

# u_0 = UART(
#     0,
#     baudrate=115200)

# imu = MPU6050()
ibus = IBUS(u_2)
# model = QuadModel()
motors = Motors()


def init_uart():
    # os.dupterm(u_0, 0)
    pass


def init():
    print(f'Run init')
    init_uart()
    # print(f'Check UART')
    # if not UNDER_DEBUG:
    #     print('Start calibrate IMU')
    #     # imu.calibrate()
    #     print('IMU calibration is finished')
    # print('Start 2 sec sleep')
    # sleep(2)
    # for i in range(1, 5):
    #     j = str(i)
    #     esc[j].duty(0)
    # print('Start 10 sec sleep')
    # sleep(10)
    # print('Stop 10 sec sleep')

def loop():
    last_t = ticks_us()
    # original case
    # rc_v = rc.read()
    # print('RC inputs values. '
    #     '1: "{}" 2: "{}" 3: "{}" '
    #     '4: "{}" 5: "{}" 6: "{}"'.format(
    #         rc_v["1"], rc_v["2"], rc_v["3"],
    #         rc_v["4"], rc_v["5"], rc_v["6"])
    # )

    # modified case
    # ibus should be read every 7 ms
    rc_ret_code, rc_v = ibus.read()
    if rc_ret_code == RC_SUCCESS:
        print('RC inputs values. 0: "{}"'
            '1: "{}" 2: "{}" 3: "{}" '
            '4: "{}" 5: "{}" 6: "{}" '
            '7: "{}" 8: "{}" 9: "{}"'
            .format(
                rc_v[0],
                rc_v[1], rc_v[2], rc_v[3],
                rc_v[4], rc_v[5], rc_v[6],
                rc_v[7], rc_v[8], rc_v[9])
        )

        motor_values = {}
        m = 100 * ((rc_v[2] - 1000) / 1000)
        print('Motor power will be: {}'.format(m))
        for i in range(1, 5):
            motor_values[i] = m

        motors.apply(motor_values)

    # i_v = imu.read()
    # print('IMU values. temp: "{:.2f}" '
    #     'acc x: "{:.2f}" y: "{:.2f}" z: "{:.2f}" '
    #     'gyro x: "{:.2f}" y: "{:.2f}" z: "{:.2f}"'.format(
    #         i_v['temp'],
    #         i_v['acc']['x'], i_v['acc']['y'], i_v['acc']['z'],
    #         i_v['gyro']['x'], i_v['gyro']['y'], i_v['gyro']['z'])
    # )
    # mot = model.convert(inputs, imu_vals)
    # set motors values to targets
   
    # print(f'Motor values: {mot[0]} {mot[1]} {mot[2]} {mot[3]}')
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
