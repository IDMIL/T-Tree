# Standard libraries
from collections import namedtuple
from enum import Enum


Message = namedtuple("Message", ["name", "data"])

# Mappings for the Soprano T-Stick 2G 012.
class Codes:
    codes = {
        0: "info", # Two bytes, indicating serial number and firmware revision
        1: "touch", # Six bytes, for six different areas of t-Stick?
        2: "jab", # ?
        3: "tap", # ?
        # Between 5 and 11 bytes.
        # First three are X/Y/Z of acceleration,
        # then an optional 6 bytes for gyro (rotation) data,
        # then one byte for pressure and one byte for piezo.
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
    def parse(self, data: bytes):
        self.state = ParserState.UNKNOWN
        messages = []
        message = None
        for bite in data:
            if self.state == ParserState.UNKNOWN:
                if bite == Codes.delimiter:
                    self.state = ParserState.AWAITING_INFO
            elif self.state == ParserState.AWAITING_INFO:
                if bite in Codes.codes:
                    message = Message(Codes.codes[bite], [])
                else:
                    message = Message("unknown", [])
                self.state = ParserState.AWAITING_DATA
            elif self.state == ParserState.AWAITING_DATA:
                if bite != Codes.delimiter:
                    message.data.append(bite)
                elif bite == Codes.escape:
                    self.state = ParserState.ESCAPED
                else:
                    messages.append(message)
                    message = None
                    self.state = ParserState.AWAITING_INFO
            elif self.state == ParserState.ESCAPED:
                message.data.append(bite)
                self.state = ParserState.AWAITING_DATA
        return messages
