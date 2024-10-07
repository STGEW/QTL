from consts import MOTOR_MAX_VAL
from consts import THROTTLE_IDLE_VAL
from consts import THROTTLE_CUT_OFF_THRESH
from consts import DISABLE_MOTOR_VALUE


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

    def convert(self, inputs, imu_vals):
        """
        inputs are values from RC
        """
        targ_angle_roll = 0.1 * (inputs['1'] - 1500)
        targ_angle_pitch = 0.1 * (inputs['2'] - 1500)
        targ_throttle = inputs['3']
        target_rate_yaw = 0.15 * (inputs['4'] - 1500)

        acc_x = imu_vals['acc']['x']
        acc_y = imu_vals['acc']['y']
        acc_z = imu_vals['acc']['z']

        gyro_x = imu_vals['gyro']['x']
        gyro_y = imu_vals['gyro']['y']
        gyro_z = imu_vals['gyro']['z']

        self._angle_roll = atan(acc_y/sqrt(acc_x*acc_x+acc_z*acc_z))*1/(3.142/180);
        self._angle_pitch = -atan(acc_x/sqrt(acc_y*acc_y+acc_z*acc_z))*1/(3.142/180);

        err_angle_roll = targ_angle_roll - self._angle_roll
        err_angle_pitch = targ_angle_pitch - self._angle_pitch

        ret = pid_equation(
            err_angle_roll,
            self.P_ANGLE_ROLL,
            self.I_ANGLE_ROLL,
            self.D_ANGLE_ROLL,
            self._prev_err_angle_roll,
            self._prev_iterm_angle_roll)
        desired_rate_roll = ret[0]
        self._prev_err_angle_roll = ret[1]
        self._prev_iterm_angle_roll = ret[2]

        ret = pid_equation(
            err_angle_pitch,
            self.P_ANGLE_PITCH,
            self.I_ANGLE_PITCH,
            self.D_ANGLE_PITCH,
            self._prev_err_angle_pitch,
            self._prev_iterm_angle_pitch)
        desired_rate_pitch = ret[0]
        self._prev_err_angle_pitch = ret[1]
        self._prev_iterm_angle_pitch = ret[2]

        error_rate_roll = desired_rate_roll - gyro_x
        error_rate_pitch = desired_rate_pitch - gyro_y
        error_rate_yaw = target_rate_yaw - gyro_z

        res = pid_equation(
            error_rate_roll,
            self.P_RATE_ROLL,
            self.I_RATE_ROLL,
            self.D_RATE_ROLL,
            self._prev_err_rate_roll,
            self._prev_iterm_rate_roll)
        target_roll = res[0]
        self._prev_err_rate_roll = res[1]
        self._prev_iterm_rate_roll = res[2]

        res = pid_equation(
            error_rate_pitch,
            self.P_RATE_PITCH,
            self.I_RATE_PITCH,
            self.D_RATE_PITCH,
            self._prev_err_rate_pitch,
            self._prev_iterm_rate_pitch)
        target_pitch = res[0]
        self._prev_err_rate_pitch = res[1]
        self._prev_iterm_rate_pitch = res[2]

        res = pid_equation(
            error_rate_yaw,
            self.P_RATE_YAW,
            self.I_RATE_YAW,
            self.D_RATE_YAW,
            self._prev_err_rate_yaw,
            self._prev_iterm_rate_yaw)
        target_yaw = res[0]
        self._prev_err_rate_yaw = res[1]
        self._prev_iterm_rate_yaw = res[2]

        motor_values = {
            '1': targ_throttle - target_roll - target_pitch - target_yaw,
            '2': targ_throttle - target_roll + target_pitch + target_yaw,
            '3': targ_throttle + target_roll + target_pitch - target_yaw,
            '4': targ_throttle + target_roll - target_pitch + target_yaw
        }

        # limit it within values
        for i in range(1, 5):
            j = str(i)
            if motor_values[j] > MOTOR_MAX_VAL:
                motor_values[j] = MOTOR_MAX_VAL - 1
            elif motor_values[j] < THROTTLE_IDLE_VAL:
                motor_valuesp[j] = THROTTLE_IDLE_VAL

        # cut off all motors
        if inputs['2'] < THROTTLE_CUT_OFF_THRESH:
            for i in range(1, 5):
                j = str(i)
                motor_values[j] = DISABLE_MOTOR_VALUE

        return motor_values


    def pid_equation(Error, P, I, D, PrevError, PrevIterm):
        Pterm = P * Error
        Iterm = PrevIterm +( I * (Error + PrevError) * (t/2))
        if Iterm > 400:
            Iterm = 400
        elif Iterm < -400:
            Iterm = -400
        Dterm = D *( (Error - PrevError)/t)
        PIDOutput = Pterm + Iterm + Dterm
        if PIDOutput > 400:
            PIDOutput = 400
        elif PIDOutput < -400:
            PIDOutput = -400
        return PIDOutput, Error, Iterm
