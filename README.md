# QTL
A simple self made quadrotor


# Upload files
pip install adafruit-ampy
pip install esptool

esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin


ampy -p /dev/ttyUSB0 -b 115200 put escs.py && \
ampy -p /dev/ttyUSB0 -b 115200 put main.py && \
ampy -p /dev/ttyUSB0 -b 115200 put imu.py && \
ampy -p /dev/ttyUSB0 -b 115200 put tcp_logger.py && \
ampy -p /dev/ttyUSB0 -b 115200 put pid.py && \
ampy -p /dev/ttyUSB0 -b 115200 put rc.py && \
ampy -p /dev/ttyUSB0 -b 115200 put utils.py && \
ampy -p /dev/ttyUSB0 -b 115200 ls

ampy -p /dev/ttyUSB0 -b 115200 rm escs.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm main.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm imu.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm tcp_logger.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm pid.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm rc.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm utils.py && \
ampy -p /dev/ttyUSB0 -b 115200 ls


# TBD:
Roll - gyro X
Pitch - gyro Y
Yaw - gyro Z

3 0
2 1
1000-2000



 M4 (27), M3 () M2 (12), M1(13)
 _ _ _ _
|_|_|_|_|
|_|_|_|_|
|_|_|_|_|


minicom -D /dev/ttyUSB0 -b 115200 -C /tmp/serial_log.txt

