# Standard libraries
import time
import threading

# Local libraries
from tstick_parser import TStickParser

# Third-party libraries
from pythonosc.udp_client import SimpleUDPClient
import serial

OSC_IP = '127.0.0.1'
OSC_PORT = 1337

READ_SIZE = 16
BAUDRATE = 57600
DEFAULT_PORT = 'COM5'

def create_parser_callback(client):
    def callback(message):
        client.send_message(f'/wiredtstick/{message.name}', message.data)
    return callback

def read_serial_thread(ser, parser):
    while True:
        data = ser.read(READ_SIZE)
        parser.enqueue_data(data)

def main():
    osc_client = SimpleUDPClient(OSC_IP, OSC_PORT)
    parser = TStickParser()
    parser.subscribe(create_parser_callback(osc_client))
    ser = serial.Serial(DEFAULT_PORT, BAUDRATE)
    threading.Thread(target=read_serial_thread, args=[ser, parser], daemon=True).start()
    while True:
        # Continually write 's' so that the T-Stick keeps sending data.
        ser.write(b's')
        time.sleep(1)

if __name__ == '__main__':
    main()