# Standard libraries
from importlib import import_module
from typing import NamedTuple, Optional

from puara_serial_manager import puara_serial_manager

class Branch(NamedTuple):
    index: int
    port: int
    paired_to: Optional[str]

def create_branches(num_branches=4, starting_port=8000):
    return (Branch(i, starting_port+i, None) for i in range(num_branches))



if __name__ == '__main__':
    print(puara_serial_manager.DATA_START)