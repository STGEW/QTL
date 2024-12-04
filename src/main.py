from machine import UART

from time import ticks_diff
from time import ticks_us
from time import sleep

import math
import os
from utils import log

from rc import RC, RC_SUCCESS
from escs import ESCs
from imu import IMU

from pid import PIDController

LOOP_PERIOD_USEC = 10000

# minimal throttle level when PIDs are working
# applied throttle can never be less than that value
MIN_PID_THROTTLE = 10.0
MAX_THROTTLE = 100.0

# IBUS UART NUMBER - 2
u_2 = UART(
    2,
    baudrate=115200,
    timeout=0)

KP = 7.5
KI = 0.1
KD = 0.5

class MainLoop:

    def __init__(self):
        self.init_uart()

        self.roll_pid = PIDController(kp=KP, ki=KI, kd=KD)
        self.pitch_pid = PIDController(kp=KP, ki=KI, kd=KD)
        self.yaw_pid = PIDController(kp=KP, ki=KI, kd=KD)

        self.imu = IMU()
        self.imu_v = None

        # current angle values
        self.angles = {
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0
        }

        # angle target values
        self.targets = {
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0
        }

        # alpha means how much we should prefer gyro in comparison to accel
        # isn't used right now
        self.alpha = {
            'roll': 0.4,
            'pitch': 0.4,
            'yaw': 0.4
        }

        self.rc = RC(u_2)
        # variable to store RC values
        self.rc_v = None

        self.ESCs = ESCs()
        self.motor_values = {
            1: 0,
            2: 0,
            3: 0,
            4: 0
        }

        self.loop_last_t_us = ticks_us()

        # diff in secs between loop calls
        self.dt_sec = None

        # initially we apply 0s to all motors.
        # that is must have for proper work of the ESCs
        # to understand why it's important one can read datasheet
        self.ESCs.apply(
            self.motor_values)
        sleep(4)

    def start(self):
        '''
        Start main loop execution. Will be executed forever
        '''
        while True:
            cur_t = ticks_us()
            dt_usec = ticks_diff(cur_t, self.loop_last_t_us)
            self.dt_sec = dt_usec / 1000000.0
            # print('dt_usec: {}'.format(dt_usec))
            if dt_usec > LOOP_PERIOD_USEC:
                self.loop()
                self.loop_last_t_us = ticks_us()

    def init_uart(self):
        # os.dupterm(u_0, 0)
        pass

    def loop(self):
        rc_res = self.read_rc()
        if not rc_res:
            return

        self.process_switches()
        # self.apply_throttle_directly_to_motors()
        self.use_controller()

    def process_switches(self):
        '''
        process data from switches
        '''
        # TBD
        if self.rc_v[4] < 1500:
            log('Switch will disable motors')
            for i in range(1, 5):
                self.motor_values[i] = 0
            self.ESCs.apply(self.motor_values)

    def read_rc(self):
        # ibus should be read every 7 ms
        ret_code, self.rc_v = self.rc.read()
        if ret_code == RC_SUCCESS:
            # update time tick
            log('RC inputs values - 0:{}; '
                '1:{}; 2:{}; 3:{}; '
                '4:{}; 5:{}; 6:{}; '
                '7:{}; 8:{}; 9:{}'.format(
                    self.rc_v[0],
                    self.rc_v[1], self.rc_v[2], self.rc_v[3],
                    self.rc_v[4], self.rc_v[5], self.rc_v[6],
                    self.rc_v[7], self.rc_v[8], self.rc_v[9])
            )
            return True
        return False

    def use_controller(self):

        # print('----------------------------------')
        self.calculate_targets()
        self.read_IMU()
        self.calculate_angles()
        # skip that step for a moment, we can enable it and play around
        # after PID coefficients would be tuned
        # self.apply_complimentary_filters()
        self.do_pids()
        self.calculate_throttles()
      
        # step 1 - check if input throttle is less then boundary
        if self.disable_motors():
            return
        self.ESCs.apply(
            self.motor_values)

    ####################################
    # USED IN CONTROLLER
    ####################################
    def disable_motors(self):
        '''
        If target throttle is less than 1050, we'll disable all the motors
        '''

        if RC.get_throttle(self.rc_v) > 1050:
            return False

        # log("Disabling motors")
        # disabling motors
        for i in range(1, 5):
            self.motor_values[i] = 0
            self.ESCs.apply(
                self.motor_values)

        # reset all the PIDs
        self.roll_pid.reset()
        self.pitch_pid.reset()
        self.yaw_pid.reset()

        return True

    def calculate_targets(self):
        '''
        define a way how we setup target values from our RC
        '''
        # TBD - here we should debug the way how we understand
        # currentl let's hardcode it with 0s
        self.targets['pitch'] = 0.0
        self.targets['roll'] = 0.0
        self.targets['yaw'] = 0.0
        log('Target angles - p:{:.2f}; r:{:.2f}; y:{:.2f}'.format(
            self.targets['pitch'],  self.targets['roll'], self.targets['yaw']
        ))
        return
        self.targets['pitch'] = 0.001 * RC.centralize(self.rc_v[1])
        self.targets['roll'] = 0.001 * RC.centralize(self.rc_v[0])
        self.targets['yaw'] = 0.001 * RC.centralize(self.rc_v[3])

    def read_IMU(self):
        self.imu_v = self.imu.read()
        acc = self.imu_v['acc']
        gyro = self.imu_v['gyro']
        log('Temp - t:{:.2f}'.format(
                self.imu_v['temp']))

        log('IMU values - a_x:{:.2f}; a_y:{:.2f}; a_z:{:.2f}; '
            'g_x:{:.2f}; g_y:{:.2f}; g_z:{:.2f}'.format(
                acc['x'], acc['y'], acc['z'],
                gyro['x'], gyro['y'], gyro['z']))

    def calculate_angles(self):
        '''
        Converts imu values into angles roll and pitch
        '''
        acc_x = self.imu_v['acc']['x']
        acc_y = self.imu_v['acc']['y']
        acc_z = self.imu_v['acc']['z']
        
        # these methods return angle in range -PI...PI
        self.angles['roll'] = math.atan2(acc_y, -acc_z)
        self.angles['pitch'] = math.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2))
        log(
            'Current and target angles - r_c:{:.2f}; p_c:{:.2f}; r_t:{:.2f}; p_t:{:.2f}; y_t:{:.2f}'.format(
            self.angles['roll'],
            self.angles['pitch'],
            self.targets['roll'],
            self.targets['pitch'],
            self.targets['yaw']
            ))

    def apply_complimentary_filters(self):
        '''
        apply complimentary filter to the data
        '''
        self.angles['roll'] = self.compl_filter(
            self.angles['roll'], self.angles['roll'], 'x', self.dt_sec)
        self.angles['pitch'] = self.compl_filter(
            self.angles['pitch'], self.angles['pitch'], 'y', self.dt_sec)

    def compl_filter(self, angle, a, axis, dt):
        # apply complimentary filter
        # angle=alpha×(angle+gyro_rate×Δt)+(1−alpha×)×accel_angle
        return a * (angle + self.imu_v['gyro'][axis] * dt) + (1 - a) * angle

    def do_pids(self):
        '''
        targets - dict of target values for pitch, roll, yaw angles
        '''
        # Calculate PID outputs for each axis
        b = {
            'roll': self.roll_pid.update(
                self.targets['roll'], self.angles['roll'], self.dt_sec),
            'pitch': self.roll_pid.update(
                self.targets['pitch'], self.angles['pitch'], self.dt_sec),
            'yaw': self.roll_pid.update(
            self.targets['yaw'], self.angles['yaw'], self.dt_sec)
        }

        throt = RC.get_throttle(self.rc_v)
        throt = RC.throt_to_perc(throt)
        log('Throttle in percents {:.2f}'.format(throt))
        
        # these values shouldn't be applied to self.ESCs directly
        # because they at some cases can be > 100% and < 0% 
        self.motor_values[1] = (throt
            - b['roll']
            - b['pitch']
            + b['yaw'])
        self.motor_values[2] = (throt
            - b['roll']
            + b['pitch']
            - b['yaw'])
        self.motor_values[3] = (throt
            + b['roll']
            + b['pitch']
            + b['yaw'])
        self.motor_values[4] = (throt
            + b['roll']
            - b['pitch']
            - b['yaw'])

    def calculate_throttles(self):
        '''
        This method is responsible for applying our logic to throttles
        Up to this point we have throtthle values after PIDs,
        but they can be < 0 and > 100
        The logic consist of 3 steps.
        1) apply shift from bottom boundary
        2) apply shift from top boundary
        3) fix motor values if they are lower than boundary

        The result of that call is aligned self.motor_values which can be
        applied to self.ESCs
        '''
        # 1 step we should check if there are values < MIN_ACTIVE_THROTTLE

        # find the shift
        shift = 0.0
        for i in range(1, 5):
            if MIN_PID_THROTTLE - self.motor_values[i] > shift:
                shift = MIN_PID_THROTTLE - self.motor_values[i]
        log('Shift value is: {:.2f}'.format(
            shift))

        # apply the shift
        for i in range(1, 5):
            self.motor_values[i] += shift
        log(
            'Motors after applying adding shift. '
            'M1: {:.2f}; M2: {:.2f}; M3: {:.2f}; M4: {:.2f}'.format(
                self.motor_values[1], self.motor_values[2],
                self.motor_values[3], self.motor_values[4]))

        # 2 step - check if we exceeded MAX_THROTTLE value
        shift = 0.0
        for i in range(1, 5):
            if self.motor_values[i] - MAX_THROTTLE > shift:
                shift = self.motor_values[i] - MAX_THROTTLE
        log('Shift value is: {:.2f}'.format(shift))
    
        # apply the shift
        for i in range(1, 5):
            self.motor_values[i] -= shift
        log('Motors after applying substracting shift. '
            'M1: {:.2f}; M2: {:.2f}; M3: {:.2f}; M4: {:.2f}'.format(
                self.motor_values[1], self.motor_values[2],
                self.motor_values[3], self.motor_values[4]))
    
        # final check
        log('Check if we have values lower than {:.2f}'.format(
            MIN_PID_THROTTLE))
        for i in range(1, 5):
            if self.motor_values[i] < MIN_PID_THROTTLE:
                self.motor_values[i] = MIN_PID_THROTTLE

        log('Motor values are - M1:{:.2f}; M2:{:.2f}; M3:{:.2f}; M4:{:.2f}'.format(
            self.motor_values[1],
            self.motor_values[2],
            self.motor_values[3],
            self.motor_values[4]))

    def apply_throttle_directly_to_motors(self):
        '''
        Call if you want to apply the whole throttle lvl directly to all 4 motors
        without any controller
        '''
        throt = RC.get_throttle(self.rc_v)
        throt = RC.throt_to_perc(throt)
        log('Motor power will be: {:.2f}'.format(
            throt))
        for i in range(1, 5):
            self.motor_values[i] = throt

        self.ESCs.apply(
            self.motor_values)


def main():
    main_loop = MainLoop()
    main_loop.start()

main()
