# Standard libraries
from collections import namedtuple
from enum import Enum
from time import sleep
import queue
import threading

Message = namedtuple("Message", ["name", "data"])

# Mappings for the Soprano T-Stick 2G 012.
class Codes:
    data = {
        0: "info", # Two bytes, indicating serial number and firmware revision
        1: "touch", # Six bytes, for six different areas of t-Stick?
        2: "jab", # ?
        3: "tap", # ?
        # 10 bytes: 2 each for Y/P/R, then 2 for pressure, 2 for piezo
        4: "periodic",
    }
    delimiter = 100
    escape = 101


class ParserState(Enum):
    UNKNOWN = 0
    AWAITING_INFO = 1
    AWAITING_DATA = 2
    ESCAPED = 3


class TStickParser:
    def __init__(self):
        self.state = ParserState.UNKNOWN
        self.data_q = queue.SimpleQueue()
        self.subscribers = []
        threading.Thread(target=self.parse_thread, daemon=True).start()

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish_message(self, message: Message):
        for callback in self.subscribers:
            callback(message)

    def enqueue_data(self, data: bytes):
        self.data_q.put(data)

    def parse_thread(self):
        message = None
        while True:
            if self.data_q.empty():
                sleep(0.01)
                continue
            for bite in self.data_q.get():
                if self.state == ParserState.UNKNOWN:
                    if bite == Codes.delimiter:
                        self.state = ParserState.AWAITING_INFO
                elif self.state == ParserState.AWAITING_INFO:
                    if bite in Codes.data:
                        message = Message(Codes.data[bite], [])
                    else:
                        message = Message("unknown", [])
                    self.state = ParserState.AWAITING_DATA
                elif self.state == ParserState.AWAITING_DATA:
                    if bite != Codes.delimiter:
                        message.data.append(bite)
                    elif bite == Codes.escape:
                        self.state = ParserState.ESCAPED
                    else:
                        self.publish_message(message)
                        message = None
                        self.state = ParserState.AWAITING_INFO
                elif self.state == ParserState.ESCAPED:
                    message.data.append(bite)
                    self.state = ParserState.AWAITING_DATA
