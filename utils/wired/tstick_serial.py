"""Wired T-Stick Serial Tool.
Usage:
  tstick_serial.py <port> <baudRate> [--info]
  tstick_serial.py -h | --help
  tstick_serial.py -v | --version
Options:
  --info        Show info about the T-Stick.
  -h --help     Show this screen.
  -v --version  Show version.
"""


# Standard libraries
import time
import threading

# Third-party libraries
from docopt import docopt
import serial

# Local libraries
from tstick_lexer import TStickLexer
from tstick_parser import TStick172Parser
from tstick_osc import OSCSender


READ_SIZE = 16

class TStickSerial:
    def __init__(self, serial_port, baudrate, read_size, recv_func, send_char=b's'):
        self.ser = serial.Serial(serial_port, baudrate)
        self.read_size = read_size
        self.recv_func = recv_func
        self.send_char = send_char
        threading.Thread(target=self.read_serial_thread, daemon=True).start()
        threading.Thread(target=self.send_start_thread, daemon=True).start()

    def read_serial_thread(self):
        while True:
            data = self.ser.read(self.read_size)
            self.recv_func(data)

    def send_start_thread(self):
        while True:
            if self.send_char is not None:
                self.ser.write(self.send_char)
            time.sleep(1)


def main(args):
    serial_port, baudrate = args["<port>"], args["<baudRate>"]
    if args['--info']:
        send_char = b'i'
    else:
        send_char = b's'
    lexer = TStickLexer()
    parser = TStick172Parser()
    sender = OSCSender('TStick_172', '127.0.0.1', 1234)
    lexer.subscribe(parser.parse)
    parser.subscribe(sender.send)
    # All the work is done in threads, so just sleep after this.
    _ = TStickSerial(serial_port, baudrate, READ_SIZE, lexer.enqueue, send_char)
    while True:
        time.sleep(1)

if __name__ == '__main__':
    args = docopt(__doc__, version="Wired T-Stick Serial Tool 0.1")
    main(args)