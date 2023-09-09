import time
import digitalio
import adafruit_logging as logging
import settings

logger = logging.getLogger()


class ButtonAction:
    def __init__(self, sw_no: int, is_push: bool):
        self.sw_no = sw_no
        self.is_push = is_push


class MatrixButtons:
    def __init__(self):
        self.col_pins: list[digitalio.DigitalInOut] = []
        self.row_pins: list[digitalio.DigitalInOut] = []
        self.state: list[list[bool]] = [
            [False for _ in range(len(settings.BUTTON_MATRIX_COL_PINS))]
            for _ in range(len(settings.BUTTON_MATRIX_ROW_PINS))
        ]

    def setup(self):
        for pin_no in settings.BUTTON_MATRIX_COL_PINS:
            pin = digitalio.DigitalInOut(pin_no)
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False
            self.col_pins.append(pin)

        for pin_no in settings.BUTTON_MATRIX_ROW_PINS:
            pin = digitalio.DigitalInOut(pin_no)
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.DOWN
            self.row_pins.append(pin)

    def scan(self) -> list[ButtonAction]:
        result: list[ButtonAction] = []

        for col, _ in enumerate(self.col_pins):
            for n, col_pin in enumerate(self.col_pins):
                col_pin.value = n == col
            time.sleep(0.001)

            for row, row_pin in enumerate(self.row_pins):
                value = row_pin.value
                if self.state[row][col] != value:
                    self.state[row][col] = value
                    result.append(
                        ButtonAction(settings.MATRIX_BUTTON_MAP[row][col], value)
                    )

        return result


def test():
    matrix = MatrixButtons()
    matrix.setup()
    logger.info("button matrix test start")
    while True:
        for action in matrix.scan():
            if action.is_push:
                logger.info(f"pushed  : sw={action.sw_no}")
            else:
                logger.info(f"released: sw={action.sw_no}")
        time.sleep(0.1)
