# Standard libraries
from collections import namedtuple
import json
import threading
from time import sleep

# Third-party libraries
import serial
import serial.tools.list_ports

BAUDRATE = 115200
READ_TIMEOUT_SECS = 5.0

DESIRED_CONFIG_PATH = 'desired_config.json'

DATA_START = b'<<<'
DATA_END = b'>>>'

Device = namedtuple('Device', ['serial_number', 'ser'])


class PuaraSerialException(Exception):
    pass


class SerialManager:
    def __init__(self):
        self.devices = {}
        self.scanner = threading.Thread(target=self.scan_thread, daemon=True)
        self.scanner.start()
        with open(DESIRED_CONFIG_PATH, 'r') as f:
            self.desired_config = json.loads(f.read())

    def scan_thread(self):
        while True:
            for port in serial.tools.list_ports.comports():
                serial_number = port.serial_number
                if serial_number not in self.devices:
                    print(f'found new serial device {serial_number}')
                    ser = serial.Serial()
                    ser.port, ser.baudrate, ser.timeout = port.device, BAUDRATE, READ_TIMEOUT_SECS
                    ser.open()
                    device = Device(serial_number, ser)
                    self.devices[serial_number] = device
                    threading.Thread(target=self.configure_device, args=[device]).start()
                else: # Reconnecting a device
                    if not self.devices[serial_number].ser.is_open:
                        print(f'reconnecting serial device {serial_number}')
                        self.devices[serial_number].ser.open()
            sleep(1)

    def configure_device(self, device):
        serial_number = device.serial_number
        print(f'waiting for {serial_number} to be ready')
        self.wait_for_device_ready(device)
        print(f'{serial_number} is ready')
        config_data = self.get_config_data(device)
        try:
            config_json = json.loads(config_data)
        except json.JSONDecodeError:
            print(f"couldn't parse JSON from {config_data}")
        needs_config = False
        for k, desired_v in self.desired_config.items():
            if not config_json[k] == desired_v:
                needs_config = True
                print(f'value of {k} does not match | desired: "{desired_v}" device: "{config_json[k]}"')
        if needs_config:
            print(f'configuring {serial_number}')
            device.ser.write(f'sendconfig {json.dumps(self.desired_config)}'.encode('utf-8'))
            # TODO(p42ul): Replace this with an ACK from the device side.
            sleep(3)
            device.ser.write(b'writeconfig')
            sleep(3)
            device.ser.write(b'reboot')
            print(f'rebooting {serial_number}')
            self.configure_device(device)
        else:
            print(f'{device.serial_number} is configured properly!')
            print(f'rebooting {serial_number} one more time to load new config')
            device.ser.write(b'reboot')

    def wait_for_device_ready(self, device):
        ser = device.ser
        expected = b'pong'
        while True:
            ser.write(b'ping')
            data = ser.read_until(expected=expected)
            if expected in data:
                break
            sleep(READ_TIMEOUT_SECS)

    def get_config_data(self, device) -> str:
        serial_number, ser = device
        ser.write(b'readconfig')
        start_data = ser.read_until(expected=DATA_START)
        if DATA_START not in start_data:
            raise PuaraSerialException(f'received {start_data} in response to "readconfig" from {serial_number} on {ser.port}')
        config_data = ser.read_until(expected=DATA_END)
        if DATA_END not in config_data:
            raise PuaraSerialException(f'"{DATA_END}" not received in time from {serial_number} on {ser.port}')
        config_data = config_data.decode('utf-8', 'backslashreplace')
        config_data = config_data.strip(str(DATA_END, 'utf-8'))
        return config_data

    def print_available_ports(self):
        for port in serial.tools.list_ports.comports():
            print(f'{port}: hwid {port.hwid} vid {port.vid} pid {port.pid}')


def main():
    sm = SerialManager()
    sm.scanner.join()


if __name__ == '__main__':
    main()