# Standard libraries
import pprint

# Third-party libraries
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

ranges = {}

class MinMax:
    def __init__(self, vals: tuple):
        self.mins: tuple = list(vals)
        self.maxs: tuple = list(vals)
        self.length = len(vals)

    def update(self, vals: tuple):
        if len(vals) != self.length:
            raise ValueError('Length of MinMax tuple must match '
                f'existing data (got {len(vals)} wanted {self.length})')
        for i, val in enumerate(vals):
            if val < self.mins[i]:
                self.mins[i] = val
            if val > self.maxs[i]:
                self.maxs[i] = val

    def __str__(self):
       vals: str = ', '.join(f'{smol}:{lorge}' for smol, lorge in zip(self.mins, self.maxs))
       return f'({vals})'

    def __repr__(self) -> str:
        return self.__str__()
        

def tstick_handler(address: str, *args: tuple):
    global ranges
    if address not in ranges:
        print(f'found new T-Stick signal {address}')
        ranges[address] = MinMax(args)
    else:
        ranges[address].update(args)

def default_handler(address, *args):
    print(f"i wasn't expecting {args} from {address}")


def main():
    dispatcher = Dispatcher()
    dispatcher.map("/TStick_*/*", tstick_handler)
    dispatcher.set_default_handler(default_handler)

    ip = "0.0.0.0"
    port = 8001

    server = BlockingOSCUDPServer((ip, port), dispatcher)
    try:
        server.serve_forever()  # Blocks forever
    except KeyboardInterrupt:
        pprint.pp(ranges)

if __name__ == '__main__':
    main()