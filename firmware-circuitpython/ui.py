import time
from busio import I2C
import adafruit_logging as logging
import settings

logger = logging.getLogger()


class PointerAction:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class ButtonAction:
    def __init__(self, sw_no: int, is_push: bool):
        self.sw_no = sw_no
        self.is_push = is_push


class UIAction:
    def __init__(self, pointer: PointerAction, buttons: list[ButtonAction]):
        self.pointer = pointer
        self.buttons = buttons


class UI:
    def __init__(self):
        pass

    def setup(self):
        self.i2c = I2C(settings.I2C_SCL_PIN, settings.I2C_SDA_PIN)
        self.i2c.try_lock()
        addresses = self.i2c.scan()
        self.i2c.unlock()
        if settings.POINTER_DEVICE_ADDR not in addresses:
            raise Exception("pointer device not found")
        self.button_state: list[list[bool]] = [
            [False for _ in range(settings.MATRIX_COL_NUM)]
            for _ in range(settings.MATRIX_ROW_NUM)
        ]

    def scan(self) -> UIAction:
        buf = bytearray(8)
        if not self.i2c.try_lock():
            logger.info("i2c lock failed")
            return UIAction(PointerAction(0, 0), [])
        try:
            self.i2c.readfrom_into(settings.POINTER_DEVICE_ADDR, buf)
        except Exception as e:
            logger.info(f"i2c read failed: {e}")
        finally:
            self.i2c.unlock()

        pointer = self._make_pointer_action(buf)
        buttons = self._make_button_action(buf)

        return UIAction(pointer, buttons)

    def _make_pointer_action(self, buf: bytearray) -> PointerAction:
        x = buf[1] - buf[0]
        y = buf[2] - buf[3]
        return PointerAction(x, y)

    def _make_button_action(self, buf: bytearray) -> list[ButtonAction]:
        result: list[ButtonAction] = []

        for col in range(settings.MATRIX_COL_NUM):
            for row in range(settings.MATRIX_ROW_NUM):
                value = buf[5 + row] & (1 << col) != 0
                if self.button_state[row][col] != value:
                    self.button_state[row][col] = value
                    result.append(
                        ButtonAction(settings.MATRIX_BUTTON_MAP[row][col], value)
                    )

        return result


def test():
    ui = UI()
    ui.setup()
    logger.info("pointer test start")
    while True:
        action = ui.scan()
        pointer = action.pointer
        buttons = action.buttons
        logger.info(f"x={pointer.x}, y={pointer.y}")
        for action in buttons:
            if action.is_push:
                logger.info(f"pushed  : sw={action.sw_no}")
            else:
                logger.info(f"released: sw={action.sw_no}")
        time.sleep(0.5)
