from collections import namedtuple
from enum import Enum


Message = namedtuple('Message', ['name', 'data'])

# Mappings for the Soprano T-Stick 2G 012.
class Codes:
    codes = {
    # Two bytes, indicating serial number and firmware revision
            0: 'info',
    # Six bytes, for six different areas of t-Stick?
            1: 'touch',
    # Unused.
            2: 'jab',
    # Unused.
            3: 'tap',
    # Between 5 and 11 bytes.
    # First three are X/Y/Z of acceleration,
    # then an optional 6 bytes for gyro (rotation) data,
    # then one byte for pressure and one byte for piezo.
            4: 'periodic',
            }
    # Don't know why these were chosen as the delimiter and the escape character, respectively.
    # But here they are.
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
                    self.state = ParserState.AWAITING_DATA
            elif self.state == ParserState.AWAITING_DATA:
                if bite != Codes.delimiter:
                    message.data.append(bite)
                else:
                    messages.append(message)
                    message = None
                    self.state = ParserState.UNKNOWN
        return messages
