# Local libraries
from tstick_parser import Signal

# Third-party libraries
from pythonosc.udp_client import SimpleUDPClient


class OSCSender:
    def __init__(self, name, ip, port):
        self.name = name
        self.client = SimpleUDPClient(ip, port)

    def send(self, signal: Signal):
        self.client.send_message(f'/{self.name}/{signal.name}', signal.data)
