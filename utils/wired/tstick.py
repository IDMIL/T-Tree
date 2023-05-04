# Standard libraries
from abc import abstractmethod, ABC

# Local libraries
from tstick_lexer import Message, TStickLexer
from tstick_parser import TStick012Parser, TStick172Parser


class TStick(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def baudrate(self):
        pass

    @abstractmethod
    def parser(self):
        pass

    @abstractmethod
    def lexer(self):
        pass

    @abstractmethod
    def baudrate(self):
        pass


class TStick_012(TStick):
    def __init__(self):
        self._parser = TStick012Parser()
        self._lexer = TStickLexer()

    def name(self):
        return 'TStick_012'

    def baudrate(self):
        return 115200

    def lexer(self):
        return self._lexer

    def parser(self):
        return self._parser

class TStick_172(TStick):
    def __init__(self):
        self._parser = TStick172Parser()
        self._lexer = TStickLexer()

    def name(self):
        return 'TStick_172'

    def baudrate(self):
        return 57600

    def lexer(self):
        return self._lexer

    def parser(self):
        return self._parser


def all_tsticks():
    return (TStick_012(), TStick_172())