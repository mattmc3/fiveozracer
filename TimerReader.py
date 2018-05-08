import serial
import logging
from FiveOzRacer import Derby


def main():
    ser = serial.Serial(
        port='/dev/cu.usbserial',
        baudrate=1200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS,
        timeout=0)

    print("connected to: " + ser.portstr)
    count = 1
    buffer = ""

    while True:
        for line in ser.read():
            # strip off the first bit
            bin_num = '0b0' + bin(line)[3:]
            int_data = int(bin_num, 2)
            timer_result = chr(int_data)
            buffer += timer_result

            if buffer.endswith("\n"):
                write(buffer)
                buffer = ""

            print(chr(int_data), end="")
            count += 1

    ser.close()


def write(s):
    logger = logging.getLogger('fozr.TimerReader')
    logger.setLevel(logging.INFO)

    derby = Derby()
    derby.load()
    derby.log_timer_data(s)


if __name__ == "__main__":
    main()
