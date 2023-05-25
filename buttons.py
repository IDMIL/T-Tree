# Standard libraries
import os
from signal import pause
from subprocess import Popen

# Third-party libraries
from gpiozero import Button, LED

path_prefix = '/home/paul/T-Tree/buttons'


class ArcadeButton:
    def __init__(self, button_pin, led_pin, command=None):
        self.button = Button(button_pin)
        self.led = LED(led_pin)
        self.command = command
        self.button.when_pressed = self.when_pressed
        self.button.when_released = self.when_released

    def when_pressed(self):
        self.led.on()
        if self.command:
            Popen(self.command)

    def when_released(self):
        self.led.off()


def main():
    green = ArcadeButton(5, 12, ['aplay', os.path.join(path_prefix, 'triangle.wav')])
    yellow = ArcadeButton(6, 16, ['aplay', os.path.join(path_prefix, 'guitar.wav')])
    blue = ArcadeButton(13, 20, ['aplay', os.path.join(path_prefix, 'cowbell.wav')])
    red = ArcadeButton(19, 21,  ['aplay', os.path.join(path_prefix, '808.wav')])
    pause()


if __name__ == '__main__':
    main()
