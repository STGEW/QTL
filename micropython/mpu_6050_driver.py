from machine import Pin, I2C
import utime


class MPU6050:
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    TEMP_OUT_H = 0x41
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    def __init__(self, i2c, i2c_addr=0x68):
        self._i2c = i2c
        self._i2c_addr = i2c_addr
        self._i2c.writeto_mem(
            self._i2c_addr,
            self.PWR_MGMT_1,
            b'\x00')

        utime.sleep_ms(100)

        self._i2c.writeto_mem(
            self._i2c_addr,
            self.SMPLRT_DIV,
            b'\x07')

        self._i2c.writeto_mem(
            self._i2c_addr,
            self.CONFIG,
            b'\x00')

        self._i2c.writeto_mem(
            self._i2c_addr,
            self.GYRO_CONFIG,
            b'\x00')

        self._i2c.writeto_mem(
            self._i2c_addr,
            self.ACCEL_CONFIG,
            b'\x00')

        # for calibration
        self.rate_calib_roll = 0.0
        self.rate_calib_pitch = 0.0
        self.rate_calib_yaw = 0.0

    def calibrate():
        # we just calculate for 4000 iterations GYRO values
        # and get average from that
        for i in range(4000):
            vals = self.read()
            self.rate_calib_roll += vals['gyro']['x']
            self.rate_calib_pitch += vals['gyro']['y']
            self.rate_calib_yaw += vals['gyro']['z']

        self.rate_calib_roll /= 4000
        self.rate_calib_pitch /= 4000
        self.rate_calib_yaw /= 4000

    def read_calib(self):
        values = self.read()
        values['gyro']['x'] -= self.rate_calib_roll
        values['gyro']['y'] -= self.rate_calib_pitch
        values['gyro']['z'] -= self.rate_calib_yaw
        return values

    def read(self):
        temp = self._read_raw(self.TEMP_OUT_H) / 340.0 + 36.53
        accel_x = self._read_raw(self.ACCEL_XOUT_H) / 16384.0
        accel_y = self._read_raw(self.ACCEL_XOUT_H + 2) / 16384.0
        accel_z = self._read_raw(self.ACCEL_XOUT_H + 4) / 16384.0
        gyro_x = self._read_raw(self.GYRO_XOUT_H) / 131.0
        gyro_y = self._read_raw(self.GYRO_XOUT_H + 2) / 131.0
        gyro_z = self._read_raw(self.GYRO_XOUT_H + 4) / 131.0
     
        return {
            'temp': temp,
            'acc': {
                'x': accel_x,
                'y': accel_y,
                'z': accel_z,
            },
            'gyro': {
                'x': gyro_x,
                'y': gyro_y,
                'z': gyro_z,
            }
        }
    
    def _read_raw(self, reg_addr):

        high = self._i2c.readfrom_mem(
            self._i2c_addr,
            reg_addr, 1)[0]

        low = self._i2c.readfrom_mem(
            self._i2c_addr,
            reg_addr + 1, 1)[0]

        value = high << 8 | low
        if value > 32768:
            value = value - 65536
        return value
