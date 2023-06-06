"""CircuitPython Essentials NeoPixel example"""
import time
import board
from rainbowio import colorwheel
import neopixel
import neopixel_spi

pixel_pin = board.D18
num_pixels = 4*9

pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), num_pixels, pixel_order=neopixel_spi.GRB, bit0=0b10000000)

pixels.fill( (0,0,0) )
pixels.show()
