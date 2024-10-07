from machine import Pin

from consts import PIN_REC

class RC:

    def __init__(self):
        self.ch = {
            '1': Pin(PIN_REC['1'], Pin.IN),
            '2': Pin(PIN_REC['2'], Pin.IN),
            '3': Pin(PIN_REC['3'], Pin.IN),
            '4': Pin(PIN_REC['4'], Pin.IN),
            '5': Pin(PIN_REC['5'], Pin.IN),
            '6': Pin(PIN_REC['6'], Pin.IN)
        }

    def read(self):
        return {
            '1': self.ch_1.value(),
            '2': self.ch_2.value(),
            '3': self.ch_3.value(),
            '4': self.ch_4.value(),
            '5': self.ch_5.value(),
            '6': self.ch_6.value()
        }
