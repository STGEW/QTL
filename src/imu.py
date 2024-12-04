from machine import Pin, I2C
import utime


PIN_IMU_SDA = 21
PIN_IMU_SCL = 22
IMU_BUS_FREQ = 100000

IMU_ADDR = 0x68

ADDR_PWR_MGMT_1 = 0x6B
WAKE_UP_B = b'\x00'

ADDR_ACC_CONF = 0x1C

# Pre-defined ranges
ACC_RNG_2G = b'\x00'
ACC_RNG_4G = b'\x08'
ACC_RNG_8G = b'\x10'
ACC_RNG_16G = b'\x18'

ACC_SCLR_2G = 16384.0
ACC_SCLR_4G = 8192.0
ACC_SCLR_8G = 4096.0
ACC_SCLR_16G = 2048.0

ADDR_GYRO_CONF = 0x1B

GYR_RNG_250DEG = b'\x00'
GYR_RNG_500DEG = b'\x08'
GYR_RNG_1000DEG = b'\x10'
GYR_RNG_2000DEG = b'\x18'

GYR_SCLR_250DEG = 131.0
GYR_SCLR_500DEG = 65.5
GYR_SCLR_1000DEG = 32.8
GYR_SCLR_2000DEG = 16.4

# the count of bytes should be read for accel, gyro
ACCEL_GYRO_SEQ_B = 6

ADDR_ACC_XOUT0 = 0x3B
ADDR_TEMP_XOUT0 = 0x41
ADDR_GYRO_XOUT0 = 0x43


class IMU:

    def __init__(self):

        # buff for accel, gyro
        self.buff_ag = bytearray(6)
        # buff for temp
        self.buff_temp = bytearray(2)

        self._bus = I2C(
            scl=Pin(PIN_IMU_SCL),
            sda=Pin(PIN_IMU_SDA),
            freq=IMU_BUS_FREQ)

        self.data = {
            'acc': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'gyro': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'temp': 0.0
        }

        # FINDME
        # return

        # wake up
        self.write(
            ADDR_PWR_MGMT_1,
            WAKE_UP_B)

        utime.sleep_ms(5)

        # setup accel
        self.write(
            ADDR_ACC_CONF,
            ACC_RNG_2G)

        # setup gyro
        self.write(
            ADDR_GYRO_CONF,
            GYR_RNG_500DEG)

    def read(self):
        # # FINDME
        # self.data['acc']['x'] = -9.8/3
        # self.data['acc']['y'] = -9.8/3
        # self.data['acc']['z'] = -9.8/3

        # self.data['gyro']['x'] = 0.0
        # self.data['gyro']['y'] = 0.0
        # self.data['gyro']['z'] = 0.0

        # return self.data
        self.read_accel()
        self.read_gyro()
        self.read_temp()
        return self.data

    def read_accel(self):
        self.read_ag(ADDR_ACC_XOUT0, self.data['acc'])
        self.data['acc']['x'] = 9.80665 * self.data['acc']['x'] / ACC_SCLR_2G
        self.data['acc']['y'] = 9.80665 * self.data['acc']['y'] / ACC_SCLR_2G
        self.data['acc']['z'] = -1 * 9.80665 * self.data['acc']['z'] / ACC_SCLR_2G

    def read_gyro(self):
        self.read_ag(ADDR_GYRO_XOUT0, self.data['gyro'])
        self.data['gyro']['x'] = self.data['gyro']['x'] / GYR_SCLR_500DEG
        self.data['gyro']['y'] = self.data['gyro']['y'] / GYR_SCLR_500DEG
        self.data['gyro']['z'] = self.data['gyro']['z'] / GYR_SCLR_500DEG

    def read_temp(self):
        self._bus.readfrom_mem_into(
            IMU_ADDR, ADDR_TEMP_XOUT0, self.buff_temp)
        self.data['temp'] = self.cont_bytes_to_signed_int(
            self.buff_temp)
        self.data['temp'] = (self.data['temp'] / 340) + 36.53
        return self.data['temp']

    def read_ag(self, reg_addr, res):
        '''
        Agruments:
            reg_addr,
            res 
        Read a 6 bytes sequence from the register with address
        "reg_addr" into the internal buffer. And write it into the 
        "res" dictionaly
        '''
        self._bus.readfrom_mem_into(
            IMU_ADDR, reg_addr, self.buff_ag)
        res['x'] = self.cont_bytes_to_signed_int(self.buff_ag[0:2])
        res['y'] = self.cont_bytes_to_signed_int(self.buff_ag[2:4])
        res['z'] = self.cont_bytes_to_signed_int(self.buff_ag[4:6])

    def cont_bytes_to_signed_int(self, b):
        val = int.from_bytes(b, "big")

        if (val < 0x8000):
            # normal positive value
            return val
        else:
            # if the value is bigger than 0x8000 (32768)
            # that means it's a negative value
            return -((65535 - val) + 1)

    def write(self, addr, buff):
        '''
        Write to module
        '''
        self._bus.writeto_mem(
            IMU_ADDR,
            addr,
            buff)
