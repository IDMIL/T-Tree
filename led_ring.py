# Standard libraries
from abc import ABC, abstractmethod, abstractproperty

# Third-party libraries
from colour import Color

NUM_RINGS = 4
LEDS_PER_RING = 8

class LEDRing(ABC):
    @abstractproperty
    def num_rings(self):
        pass

    @abstractproperty
    def leds_per_ring(self):
        pass

    @abstractmethod
    def set_ring(self, ring_num, color: Color):
        pass
    
    @abstractmethod
    def set_led(self, ring_num, led_num, color: Color):
        pass

class RealLED(LEDRing):
    def __init__(self, method='pwm'):
        import board
        import neopixel
        import neopixel_spi
        if method == 'spi':
            self.pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), NUM_RINGS*LEDS_PER_RING, pixel_order=neopixel_spi.GRB, bit0=0b10000000)
        if method == 'pwm':
            self.pixels = neopixel.NeoPixel(board.D18, NUM_RINGS*LEDS_PER_RING, brightness=1.0, auto_write=False)

    @property
    def num_rings(self):
        return NUM_RINGS

    @property
    def leds_per_ring(self):
        return LEDS_PER_RING

    def color_to_pixels(self, color: Color):
        return [c*255 for c in color.get_rgb()]
        
    def set_ring(self, ring_num, color: Color):
        if ring_num < 0 or ring_num >= NUM_RINGS or not isinstance(color, Color):
            print(f'received invalid data: ring_num: {ring_num}, color: {color}')
            return
        for i in range(LEDS_PER_RING * ring_num, LEDS_PER_RING*ring_num + LEDS_PER_RING):
            self.pixels[i] = self.color_to_pixels(color)
        self.pixels.show()

    def set_led(self, ring_num, led_num, color: Color):
        if ring_num < 0 or ring_num >= NUM_RINGS or led_num < 0 or led_num >= LEDS_PER_RING or not isinstance(color, Color):
            print(f'received invalid data: ring_num: {ring_num}, led_num: {led_num}, color: {color}')
            return
        self.pixels[ring_num*LEDS_PER_RING + led_num] = self.color_to_pixels(color)
        self.pixels.show()

class FakeLED(LEDRing):
    @property
    def num_rings(self):
        return NUM_RINGS

    @property
    def leds_per_ring(self):
        return LEDS_PER_RING

    def set_ring(self, ring_num, color: Color):
        print(f'ring {ring_num} is now {color}')

    def set_led(self, ring_num, led_num, color: Color):
        print(f'led {led_num} on ring {ring_num} is now {color}')
