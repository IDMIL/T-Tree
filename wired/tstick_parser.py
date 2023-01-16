# Standard libraries
from collections import namedtuple
import queue

# Local libraries
from tstick_lexer import Message

Signal = namedtuple("Signal", ["name", "data"])


class TStickParser:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish_signal(self, name, data):
        signal = Signal(name, data)
        for callback in self.subscribers:
            callback(signal)

    def decode_slip(self, data):
        hi, lo = data[0], data[1]
        return hi*256 + lo

    def decode_touch(self, touch_byte):
        out = []
        mask = 0b10000000
        while mask:
            bit = touch_byte & mask
            if bit:
                out.append(1)
            else:
                out.append(0)
            mask = mask >> 1
        return out

    def parse(self, message: Message):
        raise NotImplementedError

class TStick172Parser(TStickParser):
    def parse(self, message: Message):
        if message.name == "touch":
            touch = self.decode_touch(message.data[1]) + self.decode_touch(message.data[0])
            self.publish_signal("raw/capsense", touch)
        elif message.name == "periodic":
            if len(message.data) != 10:
                return
            accel_x = self.decode_slip(message.data[0:2])
            accel_y = self.decode_slip(message.data[2:4])
            accel_z = self.decode_slip(message.data[4:6])
            fsr_data = self.decode_slip(message.data[6:8])
            piezo_data = self.decode_slip(message.data[8:10])
            self.publish_signal("raw/accl", [accel_x, accel_y, accel_z])
            self.publish_signal("raw/fsr", fsr_data)
            self.publish_signal("piezo", piezo_data)