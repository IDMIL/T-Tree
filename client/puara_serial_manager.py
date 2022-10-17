# Standard libraries
from string import Template
from typing import NamedTuple, Optional
import json
import socket
import threading
from time import sleep
from unittest.mock import DEFAULT

# Third-party libraries
import serial
import serial.tools.list_ports

BAUDRATE = 115200
READ_TIMEOUT_SECS = 5.0

# The IP address to test the internet connection with.
TEST_IP_ADDR = '8.8.8.8'

# Ports will be assigned to devices in increasing order, starting with this.
STARTING_PORT = 8000

TEMPLATE_PATH = 'config_template.json'

DATA_START = b'<<<'
DATA_END = b'>>>'


class Device(NamedTuple):
    serial_number: str
    ser: serial.Serial
    osc_port: int
    name: Optional[str]=None

    def __str__(self):
        if self.name is None:
            return self.serial_number
        else:
            return self.name

    def named_device(self, name):
        print(f'{self} -> {name}')
        return Device(self.serial_number, self.ser, self.osc_port, name)

class PuaraSerialException(Exception):
    pass


class SerialManager:
    def __init__(self):
        self.devices = {}
        self.scanner = threading.Thread(target=self.scan_thread, daemon=True)
        self.scanner.start()
        self.osc_port = STARTING_PORT
        self.ip_addr = self.get_ip_address()
        with open(TEMPLATE_PATH, 'r') as f:
            self.config_template = Template(f.read())

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((TEST_IP_ADDR, 80))
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr

    def scan_thread(self):
        while True:
            for port in serial.tools.list_ports.comports():
                serial_number = port.serial_number
                if serial_number not in self.devices:
                    ser = serial.Serial()
                    ser.port, ser.baudrate, ser.timeout = port.device, BAUDRATE, READ_TIMEOUT_SECS
                    ser.open()
                    device = Device(serial_number, ser, self.osc_port)
                    self.devices[serial_number] = device
                    print(f'found new serial device {device}')
                    self.osc_port += 1
                    threading.Thread(target=self.configure_device, args=[device]).start()
                else: # Reconnecting a device
                    if not self.devices[serial_number].ser.is_open:
                        print(f'reconnecting serial device {serial_number}')
                        self.devices[serial_number].ser.open()
            sleep(1)

    def configure_device(self, device: Device):
        self.wait_for_device_ready(device)
        name = self.get_device_name(device)
        device = device.named_device(name)
        config_data = self.get_config_data(device)
        config_json = json.loads(config_data)
        desired_data = self.config_template.substitute(ip_addr=self.ip_addr, osc_port=device.osc_port)
        desired_json = json.loads(desired_data)
        needs_config = False
        for k, desired_v in desired_json.items():
            if not config_json[k] == desired_v:
                needs_config = True
                print(f'value of {k} does not match | desired: "{desired_v}" device: "{config_json[k]}"')
        if needs_config:
            print(f'configuring {device}')
            device.ser.write(f'sendconfig {json.dumps(desired_json)}'.encode('utf-8'))
            # TODO(p42ul): Replace this with an ACK from the device side.
            sleep(3)
            device.ser.write(b'writeconfig')
            sleep(3)
            device.ser.write(b'reboot')
            print(f'rebooting {device}')
            self.configure_device(device)
        else:
            print(f'{device} has been assigned to port {device.osc_port}')
            # Reboot the device once more to initialize the config.
            device.ser.write(b'reboot')

    def wait_for_device_ready(self, device: Device):
        ser = device.ser
        expected = b'pong'
        while True:
            ser.write(b'ping')
            data = ser.read_until(expected=expected)
            if expected in data:
                break
            sleep(READ_TIMEOUT_SECS)

    def get_response(self, device: Device, request: str) -> str:
        ser = device.ser
        ser.write(request.encode('utf-8'))
        start_data = ser.read_until(expected=DATA_START)
        if DATA_START not in start_data:
            raise PuaraSerialException(f'received {start_data} in response to "{request}" from {device} on {ser.port}')
        response_data = ser.read_until(expected=DATA_END)
        if DATA_END not in response_data:
            raise PuaraSerialException(f'"{DATA_END}" not received in time from {device} on {ser.port}')
        response_data = response_data.decode('utf-8', 'backslashreplace')
        response_data = response_data.strip(str(DATA_END, 'utf-8'))
        return response_data

    def get_config_data(self, device) -> str:
        return self.get_response(device, 'readconfig')

    def get_device_name(self, device) -> str:
        return self.get_response(device, 'whatareyou')

    def print_available_ports(self):
        for port in serial.tools.list_ports.comports():
            print(f'{port}: hwid {port.hwid} vid {port.vid} pid {port.pid}')


def main():
    sm = SerialManager()
    sm.scanner.join()


if __name__ == '__main__':
    main()