# Standard libraries
from collections import namedtuple
import logging
import threading
from time import sleep

# Third-party libraries
import serial
import serial.tools.list_ports

BAUDRATE = 115200
READ_TIMEOUT_SECS = 5.0

Device = namedtuple('Device', ['ser', 'ping_thread'])


class SerialManager:
    def __init__(self):
        self.devices = {}
        self.scanner = threading.Thread(target=self.scan_thread, daemon=True)
        self.scanner.start()

    def scan_thread(self):
        while True:
            for port in serial.tools.list_ports.comports():
                serial_number = port.serial_number
                if serial_number not in self.devices:
                    print(f'found new serial device {serial_number}')
                    device = serial.Serial()
                    device.port, device.baudrate, device.timeout = port.device, BAUDRATE, READ_TIMEOUT_SECS
                    device.open()
                    pinger = threading.Thread(target=self.ping_thread, args=[device])
                    pinger.start()
                    device = Device(device, pinger)
                    self.devices[serial_number] = device
                else: # Reconnecting a device
                    if not self.devices[serial_number].ser.is_open:
                        print(f'reconnecting serial device {serial_number}')
                        self.devices[serial_number].ser.open()
            sleep(1)

    def print_ports(self):
        for port, device in self.devices.items():
            print(f'{port}: {device.get_settings()}')

    def print_available_ports(self):
        for port in serial.tools.list_ports.comports():
            print(f'{port}: hwid {port.hwid} vid {port.vid} pid {port.pid}')

    def ping_thread(self, ser):
        while True:
            ser.write(b'ping')
            print(f'waiting for pong from {ser.name}')
            data = ser.read_until(expected=b'pong')
            if not b'pong' in data:
                print(f'device {ser.port} timed out during ping')
            sleep(READ_TIMEOUT_SECS)



def main():
    sm = SerialManager()
    sm.scanner.join()


if __name__ == '__main__':
    main()