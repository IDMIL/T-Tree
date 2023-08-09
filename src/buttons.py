# Standard libraries
from typing import NamedTuple
# Third-party libraries
from colour import Color
from gpiozero import Button, LED


class ArcadeButton(NamedTuple):
    button: Button
    led: LED
    color: Color


TTree_Buttons = (
    ArcadeButton(Button(5), LED(12), Color('green')),
    ArcadeButton(Button(6), LED(16), Color('yellow')),
    ArcadeButton(Button(13), LED(20), Color('blue')),
    ArcadeButton(Button(19), LED(21), Color('red')),
)