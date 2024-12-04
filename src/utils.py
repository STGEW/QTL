import socket
import time
from tcp_logger import TCPLogger

UNDER_DEBUG = True


DATA_DIR = 'data_full_throttle'

network_logger = TCPLogger()

def log(*args, **kwargs):
    if UNDER_DEBUG:
        print(*args, **kwargs)
        network_logger.print(*args, **kwargs)
