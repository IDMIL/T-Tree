# Standard libraries
from dataclasses import dataclass
from functools import partial
from glob import glob
from string import Template
from time import sleep
from typing import Optional
import logging
import shlex
import subprocess
import pickle
import os

# Local libraries
from buttons import ArcadeButton, TTree_Buttons
from puara_serial_manager import puara_serial_manager as psm

STARTING_PORT = 8000
NUM_BRANCHES = 4

PATCH_DIR = '/home/paul/T-Tree/patches'

PD_INVOCATION = Template('pd -nogui -send "port ${port}" -send "name ${name}" -send "pd dsp 1" -open "${patch}"')
# PD_INVOCATION = Template('osc-utility s --port ${port}')

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


@dataclass
class Branch:
    port: int
    paired_to: Optional[str]
    patch_index: int
    arcade: ArcadeButton
    patch_proc: Optional[subprocess.Popen]

class TTree:
    def __init__(self):
        self.branches = self.create_branches()
        self.load_state()
        self.patches = self.find_patches()
        self.setup_buttons()

    def setup_buttons(self):
        for i, branch in enumerate(self.branches):
            branch.arcade.button.when_pressed = partial(self.change_patch, i)

    def create_branches(self, num_branches=NUM_BRANCHES, starting_port=STARTING_PORT):
        return tuple(Branch(port=starting_port+i,
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
        print(invocation)
        # return subprocess.Popen(invocation, stdout=subprocess.PIPE)
        return subprocess.Popen(invocation, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    def change_patch(self, branch_index):
        branch = self.branches[branch_index]
        if not branch.paired_to:
            return
        logging.debug(f'changing patch for {branch.arcade.color}')
        if branch.patch_proc:
            branch.patch_proc.kill()
        branch.patch_index = (branch.patch_index + 1) % len(self.patches)
        branch.patch_proc = self.launch_pd(branch.port, branch.paired_to, self.patches[branch.patch_index])

    def pair(self, branch_index, device_name):
        branch = self.branches[branch_index]
        branch.paired_to = device_name
        branch.patch_index = 0
        if branch.patch_proc:
            branch.patch_proc.kill()
        branch.patch_proc = self.launch_pd(branch.port, device_name, self.patches[0])
        branch.arcade.led.on()
        self.save_state('t_tree_state.pickle')

    def config_delegate(self, device_name) -> psm.Config:
        logging.debug('pairing...')
        for branch in self.branches:
            branch.arcade.led.blink()
        while sum(b.arcade.button.value for b in self.branches) <= 0:
            pass
        pressed_index = 0
        for branch in self.branches:
            branch.arcade.led.off()
        for i in range(len(self.branches)):
            if self.branches[i].arcade.button.value == 1:
                pressed_index = i
                break
        self.pair(pressed_index, device_name)
        return psm.Config('192.168.90.1', self.branches[pressed_index].port)
    
    def save_state(self, filename):
        with self.lock:
            with open(filename, 'wb') as f:
                pickle.dump(self.branches, f)

    def load_state(self):
        if os.path.exists('t_tree_state.pickle'):
            with open('t_tree_state.pickle', 'rb') as f:
                self.branches = pickle.load(f)



if __name__ == '__main__':
    ttree = TTree()
    sm = psm.SerialManager(wifi=psm.WifiNetwork('2tree', 'mappings'), config_delegate=ttree.config_delegate)
    while True:
        sleep(1)
