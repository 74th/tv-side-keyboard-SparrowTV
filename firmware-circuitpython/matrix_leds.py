import time
from neopixel_write import neopixel_write
import adafruit_logging as logging
import digitalio
from model import LEDColor
import settings

logger = logging.getLogger()


class MatrixLED:
    def __init__(self):
        pass

    def setup(self):
        self.led_pin = digitalio.DigitalInOut(settings.MATRIX_LED_PIN)
        self.led_pin.direction = digitalio.Direction.OUTPUT
        self.buf = bytearray(settings.MATRIX_LED_NUM * 3)
        self.clear()

    def write(self):
        neopixel_write(self.led_pin, self.buf)

    def clear(self):
        for i, _ in enumerate(self.buf):
            self.buf[i] = 0
        self.write()

    def put(self, no: int, c: LEDColor, do: bool = True):
        self.buf[no * 3] = c[0]
        self.buf[no * 3 + 1] = c[1]
        self.buf[no * 3 + 2] = c[2]
        if do:
            self.write()

    def putxy(self, x: int, y: int, c: LEDColor, do: bool = True):
        self.put(settings.MATRIX_LED_MAP[y][x], c, do)

    def put_all(self, c: LEDColor, do: bool = True):
        for i in range(settings.MATRIX_LED_NUM):
            self.put(i, c, False)
        if do:
            self.write()


def test():
    matrix_led = MatrixLED()
    matrix_led.setup()
    logger.info("led matrix test start")
    time.sleep(0.1)
    while True:
        matrix_led.put_all((0x10, 0x10, 0x10))
        for i in range(-1, settings.MATRIX_LED_NUM + 2):
            if 0 <= i < settings.MATRIX_LED_NUM:
                matrix_led.put(i, (0xF0, 0x00, 0x00), False)
            matrix_led.write()
            time.sleep(0.2)
