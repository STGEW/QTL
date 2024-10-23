from ibus_parser import IBUS
from ibus_parser import STATE_HEADER, STATE_BODY, STATE_CHECKSUM
from ibus_parser import RC_NONE, RC_SUCCESS, RC_CS_ERR

from machine import UART


u_2 = UART(
    2,
    baudrate=115200,
    timeout=0)


def generate_data(data):
    """
    Arguments:
        data - data in a format {0: 1000, 1: 2000, ... 9: 19999}
    return:
        bin_data (bytearray)
    """
    bin_data = bytearray(32)
    bin_data[0] = 0x20
    cs = 0xffdf

    for i in range(10):
        val = data[i]
        # Get the first byte
        first_byte = val & 0xFF  # Mask to get the lower 8 bits
        # Get the second byte
        second_byte = (val >> 8) & 0xFF  # Right shift 8 bits and mask to get the lower 8 bits
        # Store the bytes in your buffer (for example, in self._buff)
        cs -= first_byte
        cs -= second_byte
        idx = 1 + 2 * i

        bin_data[idx] = first_byte
        bin_data[idx + 1] = second_byte
        print('For idx: {} first byte: {} second byte: {}'.format(
            idx,
            bin_data[idx].to_bytes(1, 'little'),
            bin_data[idx + 1].to_bytes(1, 'little')))


    bin_data[30] = cs & 0xFF  # Mask to get the lower 8 bits
    bin_data[31] = (cs >> 8) & 0xFF  # Right shift by 8 and mask to get the lower 8 bits
    # print('Generated bin data: {}'.format(bin_data))
    return bin_data

def main():
    ibus = IBUS(u_2)
    data = {}

    def routine(input_data):
        gen_data = generate_data(input_data)
        for b in gen_data:
            u_2.write(b.to_bytes(1, 'little'))
            rc, read_data = ibus.read()
            print("rc: {} data: {}".format(
                rc, read_data))
        print('Original data: {}'.format(input_data))


    for i in range(10):
        data[i] = i
    routine(data)

    for i in range(10):
        data[i] = i + 20
    routine(data)

main()
