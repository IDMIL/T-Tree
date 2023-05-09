# Standard libraries
from signal import pause

# Third-party libraries
from gpiozero import Button, LED


class ArcadeButton:
    def __init__(self, button_pin, led_pin):
        self.button = Button(button_pin)
        self.led = LED(led_pin)
        self.button.when_pressed = self.led.on
        self.button.when_released = self.led.off


def main():
    green = ArcadeButton(5, 12)
    yellow = ArcadeButton(6, 16)
    blue = ArcadeButton(13, 20)
    red = ArcadeButton(19, 21)

    pause()


if __name__ == '__main__':
    main()
