# QTL
A simple self made quadrotor


# Upload files
ampy -p /dev/ttyUSB0 -b 115200 put consts.py && \
ampy -p /dev/ttyUSB0 -b 115200 put main.py && \
ampy -p /dev/ttyUSB0 -b 115200 put motors.py && \
ampy -p /dev/ttyUSB0 -b 115200 put mpu_6050_driver.py && \
ampy -p /dev/ttyUSB0 -b 115200 put quad_model.py && \
ampy -p /dev/ttyUSB0 -b 115200 put rc.py && \
ampy -p /dev/ttyUSB0 -b 115200 ls

# TBD:
1) debug RC class separately
2) debug I2C class