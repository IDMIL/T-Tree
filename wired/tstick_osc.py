# Local libraries
from tstick_parser import TStickParser

# Third-party libraries
from pythonosc.udp_client import SimpleUDPClient
import serial

READ_SIZE = 16
BAUDRATE = 57600
DEFAULT_PORT = 'COM5'

def create_callback(client):
    def callback(message):
        client.send_message(f'/wiredtstick/{message.name}', message.data)
    return callback


def main():
    ip = "127.0.0.1"
    port = 1337
    client = SimpleUDPClient(ip, port)  # Create client
    parser = TStickParser()
    parser.subscribe(create_callback(client))
    ser = serial.Serial(DEFAULT_PORT, BAUDRATE)
    ser.write(b's')
    while True:
        parser.enqueue_data(ser.read(READ_SIZE))

if __name__ == '__main__':
    main()