# Standard libraries
import time
import threading

# Local libraries
from tstick_lexer import TStickLexer

# Third-party libraries
import serial

READ_SIZE = 16
BAUDRATE = 57600
DEFAULT_PORT = 'COM15'

class TStickSerial:
    def __init__(self, serial_port, baudrate, read_size, lexer):
        self.ser = serial.Serial(serial_port, baudrate)
        self.read_size = read_size
        self.lexer = lexer
        threading.Thread(target=self.read_serial_thread, daemon=True).start()
        threading.Thread(target=self.send_start_thread, daemon=True).start()

    def read_serial_thread(self):
        while True:
            data = self.ser.read(self.read_size)
            self.lexer.enqueue_data(data)

    def send_start_thread(self):
        while True:
            # Continually write 's' so that the T-Stick keeps sending data.
            self.ser.write(b's')
            time.sleep(1)

def main():
    lexer = TStickLexer()
    lexer.subscribe(print)
    # All the work is done in threads, so just sleep after this.
    _ = TStickSerial(DEFAULT_PORT, BAUDRATE, READ_SIZE, lexer)
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()