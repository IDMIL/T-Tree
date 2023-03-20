# Standard libraries
from collections import namedtuple
from enum import Enum
from time import sleep
import queue
import threading

Message = namedtuple("Message", ["name", "data"])

# Mappings for the Soprano T-Stick 2G 012.
class SlipMappings:
    codes = {
        0: "info", # Two bytes, indicating serial number and firmware revision
        1: "touch", # Six bytes, for six different areas of t-Stick?
        2: "jab", # ?
        3: "tap", # ?
        # 10 bytes: 2 each for Y/P/R, then 2 for pressure, 2 for piezo
        4: "periodic",
    }
    delimiter = 100
    escape = 101


class LexerState(Enum):
    UNKNOWN = 0
    AWAITING_CODE = 1
    AWAITING_DATA = 2
    ESCAPED = 3

class TStickLexer:
    def __init__(self):
        self.state = LexerState.UNKNOWN
        self.data_q = queue.SimpleQueue()
        self.subscribers = []
        threading.Thread(target=self.lex_thread, daemon=True).start()

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish_message(self, message: Message):
        for callback in self.subscribers:
            callback(message)

    def enqueue(self, data: bytes):
        self.data_q.put(data)

    def lex_thread(self):
        message = None
        while True:
            if self.data_q.empty():
                sleep(0.01)
                continue
            for bite in self.data_q.get():
                if self.state == LexerState.UNKNOWN:
                    if bite == SlipMappings.delimiter:
                        self.state = LexerState.AWAITING_CODE
                elif self.state == LexerState.AWAITING_CODE:
                    if bite in SlipMappings.codes:
                        message = Message(SlipMappings.codes[bite], [])
                    else:
                        message = Message("unknown", [])
                    self.state = LexerState.AWAITING_DATA
                elif self.state == LexerState.AWAITING_DATA:
                    if bite == SlipMappings.escape:
                        self.state = LexerState.ESCAPED
                    elif bite != SlipMappings.delimiter:
                        message.data.append(bite)
                    else: # delimiter
                        self.publish_message(message)
                        message = None
                        self.state = LexerState.AWAITING_CODE
                elif self.state == LexerState.ESCAPED:
                    message.data.append(bite)
                    self.state = LexerState.AWAITING_DATA