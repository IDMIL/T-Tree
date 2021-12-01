from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from led_utils import set_ring


def default_handler(address, *args):
    print(f'DEFAULT {address}: {args}')

def led_ring_handler(address, *args):
    if len(args) != 4 or type(args[0]) is not float or type(args[1]) is not float or type(args[2]) is not float or type(args[3]) is not float:
        print(f'invalid args received: {args}')
        return
    rgb = tuple(int(a*255) for a in args[1:])
    ring_num = int(args[0])
    set_ring(ring_num, rgb)


dispatcher = Dispatcher()
dispatcher.map('/led_ring', led_ring_handler)
dispatcher.set_default_handler(default_handler)

ip = '0.0.0.0'
port = 1234

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever
