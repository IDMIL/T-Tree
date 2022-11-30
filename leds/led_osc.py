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
        dispatcher.map('/led_ring/set_ring/*', self.led_ring_handler)
        dispatcher.map('/led_ring/set_led/*/*', self.individual_led_handler)
        return BlockingOSCUDPServer((IP, PORT), dispatcher)

    def individual_led_handler(self, address, *args):
        address = address.split('/')
        try:
            led_num = int(address[-1])
            if led_num < 0 or led_num >= self.ring.leds_per_ring:
                raise ValueError
        except ValueError:
            print(f'address of led must be an int between 0 and {self.ring.leds_per_ring}. received: {address[-1]}')
            return
        try:
            ring_num = int(address[-2])
            if ring_num < 0 or ring_num >= self.ring.num_rings:
                raise ValueError
        except ValueError:
            print(f'address of ring must be an int between 0 and {self.ring.num_rings}. received: {address[-2]}')
            return
        if len(args) != 3:
            print(f'this handler requires 3 float values (r, g, b). received: {args}')
            return
        for i in range(len(args)):
            if type(args[i]) is not float or args[i] < 0.0 or args[i] > 1.0:
                print(f'(r, g, b) values must all be floats in [0, 1]. received {args}')
                return
        c = Color()
        c.set_rgb(args)
        self.ring.set_led(ring_num, led_num, c)

    def led_ring_handler(self, address, *args):
        address = address.split('/')
        try:
            ring_num = int(address[-1])
            if ring_num < 0 or ring_num >= self.ring.num_rings:
                raise ValueError
        except ValueError:
            print(f'address of ring must be an int between 0 and {self.ring.num_rings}. received: {address[-1]}')
            return
        if len(args) != 3:
            print(f'this handler requires 3 float values (r, g, b). received: {args}')
            return
        for i in range(len(args)):
            if type(args[i]) is not float or args[i] < 0.0 or args[i] > 1.0:
                print(f'(r, g, b) values must all be floats in [0, 1]. received {args}')
                return
        c = Color()
        c.set_rgb(args)
        self.ring.set_ring(ring_num, c)


def main():
    osc_led = OscLed(RealLED())
    print(f'Running OSC server at {IP}:{PORT}. Press Ctrl+C to quit.')
    while True:
        sleep(1)

if __name__ == '__main__':
    main()
