STATE_HEADER = 1
STATE_BODY = 2
STATE_CHECKSUM = 3

RC_NONE = 0
RC_SUCCESS = 1
RC_CS_ERR = 2

NUM_CH = 10

HEADER_BYTE = 0x20
# 0xffff - HEADER_BYTE
CS_INIT = 0xffdf
# body is 29 bytes, however 1 byte is skipped
# parsing of the data should be done starting from
# 1-st byte, not 0
BODY_SIZE = 29
CS_SIZE = 2


class IBUS:

    def __init__(self, uart, br=115200):
        """
        u_2 = UART(
            2,
            baudrate=115200,
            timeout=0)
        """
        self._uart = uart
        self._state = STATE_HEADER
        self.ch = {}
        for i in range(NUM_CH):
            self.ch[i] = 0
        self._i = 0
        self._cur_cs = CS_INIT
        self._exp_cs = 0x00
        self._buff_body = bytearray(BODY_SIZE)
        self._buff_cs = bytearray(CS_SIZE)
        self._b = 0x00

    def read(self):
        """
        Should be called regularly
        Return:
            (code, parsed_data) - a values read from the RC
            
        """
        
        while self._uart.any():
            self._b = self._uart.read(1)
            self._b = self._b[0]
            # print('state: {} self._b: {}'.format(
            #     self._state,
            #     self._b.to_bytes(1, 'little')))
            if self._state == STATE_HEADER:
                
                if self._b == HEADER_BYTE:
                    self._state = STATE_BODY
                    self._i = 0
                    self._cur_cs = CS_INIT
            elif self._state == STATE_BODY:
                self._buff_body[self._i] = self._b
                self._cur_cs -= self._b
                self._i += 1
                if self._i == BODY_SIZE:
                    self._state = STATE_CHECKSUM
                    self._i = 0
            elif self._state == STATE_CHECKSUM:
                self._buff_cs[self._i] = self._b
                self._i += 1
                if self._i == CS_SIZE:
                    self._exp_cs = self._buff_cs[0] | (self._buff_cs[1] << 8)
                    self._state = STATE_HEADER
                    # compare checksum
                    if self._cur_cs == self._exp_cs:
                        return (
                            RC_SUCCESS,
                            self._parse_channels())
                    else:
                        return (RC_CS_ERR, None)

        return (RC_NONE, None)

    def _parse_channels(self):
        for i in range(NUM_CH):
            j = 2 * i + 1
            # print('Channel i: {} pos in buff: {} first byte: {} second byte: {}'.format(
            #     i,
            #     2 * i,
            #     self._buff_body[2 * i].to_bytes(1, 'little'),
            #     self._buff_body[2 * i + 1].to_bytes(1, 'little')))
            self.ch[i] = self._buff_body[j] | (self._buff_body[j + 1] << 8)
        return self.ch
