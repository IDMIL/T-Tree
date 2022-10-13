# Standard libraries
import threading
from time import sleep

# Third-party libraries
import serial
import serial.tools.list_ports

BAUDRATE = 115200


def scan_ports():
    ports = None
    while True:
        ports = serial.tools.list_ports.comports()

class SerialManager:
    def __init__(self):
        self.ports = {}
        threading.Thread(target=self.scan_thread).start()

    def scan_thread(self):
        while True:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                if port not in self.ports:
                    device = serial.Serial()
                    device.port, device.baudrate = port, BAUDRATE
                    device.open()
                    self.ports[port] = device
            sleep(1)


def main():
    sm = SerialManager()


if __name__ == '__main__':
    main()