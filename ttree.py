# Standard libraries
from dataclasses import dataclass
from glob import glob
from string import Template
from time import sleep
from typing import Optional
import logging
import shlex
import subprocess

# Third-party libraries
from colour import Color

# Local libraries
from buttons import ArcadeButton, TTree_Buttons
from puara_serial_manager import puara_serial_manager

STARTING_PORT = 8000
NUM_BRANCHES = 4

PATCH_DIR = '/home/paul/T-Tree/patches'

PD_INVOCATION = Template('pd -nogui -send "port ${port}" -send "name ${name}" -send "pd dsp 1" -open "${patch}"')

@dataclass
class Branch:
    index: int
    port: int
    paired_to: Optional[str]
    patch_index: int
    arcade: ArcadeButton
    patch_proc: Optional[subprocess.Popen]

class TTree:
    def __init__(self):
        self.branches = self.create_branches()
        self.patches = self.find_patches()

    def create_branches(self, num_branches=NUM_BRANCHES, starting_port=STARTING_PORT):
        return tuple(Branch(index=i,
                            port=starting_port+i,
                            paired_to=None,
                            patch_index=-1,
                            arcade=TTree_Buttons[i],
                            patch_proc=None) for i in range(num_branches))

    def find_patches(self):
        return glob(f'{PATCH_DIR}/*.pd')

    def launch_pd(self, port, name, patch):
        invocation = PD_INVOCATION.substitute(port=port, name=name, patch=patch)
        logging.debug(f'running {invocation}')
        invocation = shlex.split(invocation)
        return subprocess.Popen(invocation, stderr=subprocess.DEVNULL)

    def change_patch(self, branch_index):
        branch = self.branches[branch_index]
        if branch.patch_proc:
            branch.patch_proc.kill()
        branch.patch_index = (branch.patch_index + 1) % len(self.patches)
        branch.patch_proc = self.launch_pd(branch.port, branch.paired_to, self.patches[branch.patch_index])


if __name__ == '__main__':
    ttree = TTree()
    green = ttree.branches[0]
    green.paired_to = 'TStick_191'
    green.arcade.button.when_pressed = lambda _: ttree.change_patch(0)
    sleep(60)