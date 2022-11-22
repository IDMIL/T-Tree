# Standard libraries
from abc import ABC, abstractmethod

# Third-party libraries
from colour import Color

NUM_RINGS = 3
LEDS_PER_RING = 8

class LEDRing(ABC):
    @abstractmethod
    def set_ring(self, ring_num, color: Color):
        pass
    
    @abstractmethod
    def set_led(self, ring_num, led_num, color: Color):
        pass

def RealLED(LEDRing):
    def __init__(self):
        import board
        import neopixel
        PIXEL_GPIO_PIN = board.D18
        self.pixels = neopixel.NeoPixel(PIXEL_GPIO_PIN, NUM_RINGS*LEDS_PER_RING, auto_write=False)
        
    def set_ring(self, ring_num, color: Color):
        if ring_num < 0 or ring_num >= NUM_RINGS or not isinstance(color, Color):
            print(f'received invalid data: ring_num: {ring_num}, color: {color}')
            return
        for i in range(LEDS_PER_RING * ring_num, LEDS_PER_RING*ring_num + LEDS_PER_RING):
            self.pixels[i] = color.get_rgb()
        self.pixels.show()

    def set_led(self, ring_num, led_num, color: Color):
        if ring_num < 0 or ring_num >= NUM_RINGS or led_num < 0 or led_num >= LEDS_PER_RING or not isinstance(color, Color):
            print(f'received invalid data: ring_num: {ring_num}, led_num: {led_num}, color: {color}')
            return
        self.pixels[ring_num*LEDS_PER_RING + led_num] = color.get_rgb()
        self.pixels.show()

class FakeLED(LEDRing):
    def set_ring(self, ring_num, color: Color):
        print(f'ring {ring_num} is now {color}')

    def set_led(self, ring_num, led_num, color: Color):
        print(f'led {led_num} on ring {ring_num} is now {color}')
