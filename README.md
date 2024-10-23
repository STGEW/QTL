# QTL
A simple self made quadrotor


# Upload files
pip install adafruit-ampy
pip install esptool

esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin


ampy -p /dev/ttyUSB0 -b 115200 put consts.py && \
ampy -p /dev/ttyUSB0 -b 115200 put main.py && \
ampy -p /dev/ttyUSB0 -b 115200 put motors.py && \
ampy -p /dev/ttyUSB0 -b 115200 put mpu_6050_driver.py && \
ampy -p /dev/ttyUSB0 -b 115200 put quad_model.py && \
ampy -p /dev/ttyUSB0 -b 115200 put ibus_parser.py && \
ampy -p /dev/ttyUSB0 -b 115200 ls

ampy -p /dev/ttyUSB0 -b 115200 rm consts.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm main.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm motors.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm mpu_6050_driver.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm mpu_6050.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm quad_model.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm rc.py && \
ampy -p /dev/ttyUSB0 -b 115200 rm ibus.py && \
ampy -p /dev/ttyUSB0 -b 115200 ls

# TBD:
1) debug RC class separately
2) debug I2C class

Roll - gyro X
Pitch - gyro Y
Yaw - gyro Z

3 0
2 1
1000-2000

1) ibus переделать
2) imu переделать
3) прочитать доки на ESC, как он вообще должен работать
4) первый ESC перегревается
5) дебаг юарт вывести куда-то на плате, чтобы можно было читать все
6) не хватает светодиодика состояния на квадрике
7) не хватает dc-dc преобразователя. Когда все включается, он сразу выдает 0 В вместо 5В. Сколько потребляют ESC, от чего они питаются

 M4 (27), M3 () M2 (12), M1(13)
 _ _ _ _
|_|_|_|_|
|_|_|_|_|
|_|_|_|_|