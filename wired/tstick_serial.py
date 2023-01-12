# Standard libraries
import time
import threading

# Local libraries
from tstick_parser import TStickParser

# Third-party libraries
import serial

READ_SIZE = 16
BAUDRATE = 57600
DEFAULT_PORT = 'COM5'

def read_serial_thread(ser, parser):
    while True:
        data = ser.read(READ_SIZE)
        # for bite in data:
        #     print(hex(bite), end='', flush=True)
        parser.enqueue_data(data)

def main():
    parser = TStickParser()
    parser.subscribe(print)
    print(f'Opening serial port {DEFAULT_PORT} at baud rate {BAUDRATE}...')
    ser = serial.Serial(DEFAULT_PORT, BAUDRATE, timeout=3)
    print('Serial connection established.')
    threading.Thread(target=read_serial_thread, args=[ser, parser], daemon=True).start()
    while True:
        input('Press enter to send start byte...')
        ser.write(b's')
        print('Start byte written.')

if __name__ == '__main__':
    main()