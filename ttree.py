from collections import namedtuple
from typing import Optional

class Branch(namedtuple):
    index: int
    port: int
    paired_to: Optional[str]

def create_branches(num_branches=4, starting_port=8000):
    return (Branch(i, starting_port+i, None) for i in range(num_branches))