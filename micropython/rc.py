from machine import Pin

from consts import PIN_REC_CH_1, PIN_REC_CH_2, PIN_REC_CH_3
from consts import PIN_REC_CH_4, PIN_REC_CH_5, PIN_REC_CH_6



class RC:

    def __init__(self):
        self.ch_1 = Pin(PIN_REC_CH_1, Pin.IN)
        self.ch_2 = Pin(PIN_REC_CH_2, Pin.IN)
        self.ch_3 = Pin(PIN_REC_CH_3, Pin.IN)
        self.ch_4 = Pin(PIN_REC_CH_4, Pin.IN)
        self.ch_5 = Pin(PIN_REC_CH_5, Pin.IN)
        self.ch_6 = Pin(PIN_REC_CH_6, Pin.IN)

    def read(self):
        return {
            '1': self.ch_1.value(),
            '2': self.ch_2.value(),
            '3': self.ch_3.value(),
            '4': self.ch_4.value(),
            '5': self.ch_5.value(),
            '6': self.ch_6.value()
        }
