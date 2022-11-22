# Standard library
from time import sleep
import threading

# Third-party libraries
from colour import Color
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# Local libraries
from led_ring import LEDRing, RealLED, FakeLED

IP = '0.0.0.0'
PORT = 1234

class OscLed:
    def __init__(self, ring: LEDRing):
        self.ring = ring
        server = self._create_osc_server()
        threading.Thread(target=server.serve_forever, daemon=True).start()

    def _create_osc_server(self):
        dispatcher = Dispatcher()
        dispatcher.map('/led_ring', self.led_ring_handler)
        return BlockingOSCUDPServer((IP, PORT), dispatcher)

    def led_ring_handler(self, _, *args):
        if len(args) != 4 or type(args[0]) is not int or type(args[1]) is not float or type(args[2]) is not float or type(args[3]) is not float:
            print(f'invalid args received: {args}')
            return
        c = Color()
        c.set_rgb(args[1:])
        ring_num = args[0]
        self.ring.set_ring(ring_num, c)


def main():
    osc_led = OscLed(FakeLED())
    print(f'Running OSC server at {IP}:{PORT}. Press Ctrl+C to quit.')
    while True:
        sleep(1)

if __name__ == '__main__':
    main()