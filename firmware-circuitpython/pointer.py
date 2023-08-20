import time
from busio import I2C
import settings


class PointerAction:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Pointer:
    def __init__(self):
        pass

    def setup(self):
        self.i2c = I2C(settings.I2C_SCL_PIN, settings.I2C_SDA_PIN)
        self.i2c.try_lock()
        addresses = self.i2c.scan()
        self.i2c.unlock()
        if settings.POINTER_DEVICE_ADDR not in addresses:
            raise Exception("pointer device not found")

    def scan(self) -> PointerAction:
        buf = bytearray(5)
        if not self.i2c.try_lock():
            print("i2c lock failed")
            return PointerAction(0, 0)
        try:
            self.i2c.readfrom_into(settings.POINTER_DEVICE_ADDR, buf)
        except Exception as e:
            print(f"i2c read failed: {e}")
        finally:
            self.i2c.unlock()
        x = buf[1] - buf[0]
        y = buf[2] - buf[3]
        return PointerAction(x, y)


def test():
    pointer = Pointer()
    pointer.setup()
    print("pointer test start")
    while True:
        action = pointer.scan()
        print(f"x={action.x}, y={action.y}")
        time.sleep(0.5)