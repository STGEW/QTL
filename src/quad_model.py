import logging
from math import atan, sqrt

from consts import MOTOR_MAX_VAL
from consts import THROTTLE_IDLE_VAL
from consts import THROTTLE_CUT_OFF_THRESH
from consts import DISABLE_MOTOR_VALUE


logger = logging.getLogger(__name__)


class QuadModel:

    P_ANGLE_ROLL = 2
    P_ANGLE_PITCH = 2
    I_ANGLE_ROLL = 0

    I_ANGLE_PITCH = 0
    D_ANGLE_ROLL = 0
    D_ANGLE_PITCH = 0

    P_RATE_ROLL = 0.75
    I_RATE_ROLL = 0.012
    D_RATE_ROLL = 0.0085

    P_RATE_PITCH = 0.75
    I_RATE_PITCH = 0.012
    D_RATE_PITCH = 0.0085

    P_RATE_YAW = 4.2
    I_RATE_YAW = 2.8
    D_RATE_YAW = 0

    
    def __init__(self):
        self._angle_roll = 0.0
        self._angle_pitch = 0.0

        self._prev_err_angle_roll = 0.0
        self._prev_iterm_angle_roll = 0.0

        self._prev_err_angle_pitch = 0.0
        self._prev_iterm_angle_pitch = 0.0

        self._prev_err_rate_roll = 0.0
        self._prev_iterm_rate_roll = 0.0

        self._prev_err_rate_pitch = 0.0
        self._prev_iterm_rate_pitch = 0.0

        self._prev_err_rate_yaw = 0.0
        self._prev_iterm_rate_yaw = 0.0

    def convert(self, inputs, imu_vals, dt):
        """
        inputs - values from RC
        imu_vals - 
        dt - how much time left since last call
        """
        dt = dt / 10**9
        logger.info(f'Model. Target motor values: "{inputs}" dt: "{dt}"')
        targ_angle_roll = 0.1 * (inputs['1'] - 1500)
        targ_angle_pitch = 0.1 * (inputs['2'] - 1500)
        targ_throttle = inputs['3']
        target_rate_yaw = 0.15 * (inputs['4'] - 1500)

        logger.info(f'Model. Step 1')
        logger.info(f'Model. Target angle roll: "{targ_angle_roll}"')
        logger.info(f'Model. Target angle pitch: "{targ_angle_pitch}"')
        logger.info(f'Model. Target throttle: "{targ_throttle}"')
        logger.info(f'Model. Target rate yaw: "{target_rate_yaw}"')


        acc_x = imu_vals['acc']['x']
        acc_y = imu_vals['acc']['y']
        acc_z = imu_vals['acc']['z']

        gyro_x = imu_vals['gyro']['x']
        gyro_y = imu_vals['gyro']['y']
        gyro_z = imu_vals['gyro']['z']

        self._angle_roll = atan(acc_y/sqrt(acc_x*acc_x+acc_z*acc_z))*1/(3.142/180);
        self._angle_pitch = -atan(acc_x/sqrt(acc_y*acc_y+acc_z*acc_z))*1/(3.142/180);

        logger.info(f'Model. Step 2')
        logger.info(f'Model. Current angle roll: "{self._angle_roll}"')
        logger.info(f'Model. Current angle pitch: "{self._angle_pitch}"')

        err_angle_roll = targ_angle_roll - self._angle_roll
        err_angle_pitch = targ_angle_pitch - self._angle_pitch

        logger.info(f'Model. Step 3')
        logger.info(f'Model. Error angle roll: "{err_angle_roll}"')
        logger.info(f'Model. Error angle pitch: "{err_angle_pitch}"')

        logger.info(f'Model. Step 4. Running PIDs for...')
        ret = self.pid_equation(
            err_angle_roll,
            self.P_ANGLE_ROLL,
            self.I_ANGLE_ROLL,
            self.D_ANGLE_ROLL,
            self._prev_err_angle_roll,
            self._prev_iterm_angle_roll,
            dt)
        desired_rate_roll = ret[0]
        self._prev_err_angle_roll = ret[1]
        self._prev_iterm_angle_roll = ret[2]

        logger.info(f'Model. PID for error angle roll')
        logger.info(f'Model. Desired rate roll: "{desired_rate_roll}"')
        logger.info(f'Model. Prev err angle roll: "{self._prev_err_angle_roll}"')
        logger.info(f'Model. Prev iterm angle roll: "{self._prev_iterm_angle_roll}"')

        ret = self.pid_equation(
            err_angle_pitch,
            self.P_ANGLE_PITCH,
            self.I_ANGLE_PITCH,
            self.D_ANGLE_PITCH,
            self._prev_err_angle_pitch,
            self._prev_iterm_angle_pitch,
            dt)
        desired_rate_pitch = ret[0]
        self._prev_err_angle_pitch = ret[1]
        self._prev_iterm_angle_pitch = ret[2]

        logger.info(f'Model. PID for error angle pitch')
        logger.info(f'Model. Desired rate pitch: "{desired_rate_pitch}"')
        logger.info(f'Model. Prev err angle pitch: "{self._prev_err_angle_pitch}"')
        logger.info(f'Model. Prev iterm angle pitch: "{self._prev_iterm_angle_pitch}"')

        error_rate_roll = desired_rate_roll - gyro_x
        error_rate_pitch = desired_rate_pitch - gyro_y
        error_rate_yaw = target_rate_yaw - gyro_z

        logger.info(f'Model. Step 5. Error rates:')
        logger.info(f'Model. Error rate roll: "{error_rate_roll}"')
        logger.info(f'Model. Error rate pitch: "{error_rate_pitch}"')
        logger.info(f'Model. Error rate yaw: "{error_rate_yaw}"')

        logger.info(f'Model. Step 6. Running PIDs for error rates')
        res = self.pid_equation(
            error_rate_roll,
            self.P_RATE_ROLL,
            self.I_RATE_ROLL,
            self.D_RATE_ROLL,
            self._prev_err_rate_roll,
            self._prev_iterm_rate_roll,
            dt)
        target_roll = res[0]
        self._prev_err_rate_roll = res[1]
        self._prev_iterm_rate_roll = res[2]

        logger.info(f'Model. PID for error rate roll')
        logger.info(f'Model. Target roll: "{target_roll}"')
        logger.info(f'Model. Prev err rate roll: "{self._prev_err_rate_roll}"')
        logger.info(f'Model. Prev iterm rate roll: "{self._prev_iterm_rate_roll}"')

        res = self.pid_equation(
            error_rate_pitch,
            self.P_RATE_PITCH,
            self.I_RATE_PITCH,
            self.D_RATE_PITCH,
            self._prev_err_rate_pitch,
            self._prev_iterm_rate_pitch,
            dt)
        target_pitch = res[0]
        self._prev_err_rate_pitch = res[1]
        self._prev_iterm_rate_pitch = res[2]

        logger.info(f'Model. PID for error rate pitch')
        logger.info(f'Model. Target pitch: "{target_pitch}"')
        logger.info(f'Model. Prev err rate pitch: "{self._prev_err_rate_pitch}"')
        logger.info(f'Model. Prev iterm rate pitch: "{self._prev_iterm_rate_pitch}"')

        res = self.pid_equation(
            error_rate_yaw,
            self.P_RATE_YAW,
            self.I_RATE_YAW,
            self.D_RATE_YAW,
            self._prev_err_rate_yaw,
            self._prev_iterm_rate_yaw,
            dt)
        target_yaw = res[0]
        self._prev_err_rate_yaw = res[1]
        self._prev_iterm_rate_yaw = res[2]

        logger.info(f'Model. PID for error rate yaw')
        logger.info(f'Model. Target yaw: "{target_yaw}"')
        logger.info(f'Model. Prev err rate yaw: "{self._prev_err_rate_yaw}"')
        logger.info(f'Model. Prev iterm rate yaw: "{self._prev_iterm_rate_yaw}"')


        motor_values = {
            '1': targ_throttle - target_roll - target_pitch - target_yaw,
            '2': targ_throttle - target_roll + target_pitch + target_yaw,
            '3': targ_throttle + target_roll + target_pitch - target_yaw,
            '4': targ_throttle + target_roll - target_pitch + target_yaw
        }

        logger.info(f'Model. Step 7. Calculating motor values')
        logger.info(f"Model. Motor 1: {motor_values['1']}")
        logger.info(f"Model. Motor 2: {motor_values['2']}")
        logger.info(f"Model. Motor 3: {motor_values['3']}")
        logger.info(f"Model. Motor 4: {motor_values['4']}")

        # limit it within values
        for i in range(1, 5):
            j = str(i)
            if motor_values[j] > MOTOR_MAX_VAL:
                motor_values[j] = MOTOR_MAX_VAL - 1
            elif motor_values[j] < THROTTLE_IDLE_VAL:
                motor_values[j] = THROTTLE_IDLE_VAL

        logger.info(f'Model. Step 8. After limiting motor values')
        logger.info(f"Model. Motor 1: {motor_values['1']}")
        logger.info(f"Model. Motor 2: {motor_values['2']}")
        logger.info(f"Model. Motor 3: {motor_values['3']}")
        logger.info(f"Model. Motor 4: {motor_values['4']}")

        # cut off all motors
        if inputs['2'] < THROTTLE_CUT_OFF_THRESH:
            for i in range(1, 5):
                j = str(i)
                motor_values[j] = DISABLE_MOTOR_VALUE

        logger.info(f'Model. Step 9. After motor cut off threshold')
        logger.info(f"Model. Motor 1: {motor_values['1']}")
        logger.info(f"Model. Motor 2: {motor_values['2']}")
        logger.info(f"Model. Motor 3: {motor_values['3']}")
        logger.info(f"Model. Motor 4: {motor_values['4']}")

        return motor_values


    def pid_equation(
            self, Error,
            P, I, D,
            PrevError, PrevIterm,
            dt):
        Pterm = P * Error
        Iterm = PrevIterm + ( I * (Error + PrevError) * (dt/2))
        if Iterm > 400:
            Iterm = 400
        elif Iterm < -400:
            Iterm = -400
        Dterm = D *( (Error - PrevError)/dt)
        PIDOutput = Pterm + Iterm + Dterm
        if PIDOutput > 400:
            PIDOutput = 400
        elif PIDOutput < -400:
            PIDOutput = -400
        return PIDOutput, Error, Iterm
