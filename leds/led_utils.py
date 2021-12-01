"""CircuitPython Essentials NeoPixel example"""
import time
import board
from rainbowio import colorwheel
import neopixel

pixel_pin = board.D18
num_rings = 4
pixels_per_ring = 9

brightness = 0.3

pixels = neopixel.NeoPixel(pixel_pin, num_rings*pixels_per_ring, brightness=brightness, auto_write=False)

def set_ring(ring, rgb):
    if ring < 0 or ring >= num_rings or len(rgb) != 3:
        print(f'received invalid data: ring: {ring}, rgb: {rgb}')
        return
    for i in range(pixels_per_ring * ring, pixels_per_ring*ring + pixels_per_ring):
        pixels[i] = rgb
    pixels.show()
