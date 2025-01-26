from typing import Union
import time

from busio import UART
import adafruit_logging as logging
from ch9329 import CH9329, Keycode as KC

import settings

logger = logging.getLogger()


class MouseState:
    def __init__(self, x: int, y: int, wheel: int):
        self.x = x
        self.y = y
        self.wheel = wheel


class PcUSB:
    def __init__(self):
        uart = UART(tx=settings.CH9329_TX, rx=settings.CH9329_RX, baudrate=9600)
        self.ch9329 = CH9329(uart)
        self._current_mouse_state = MouseState(0, 0, 0)

    def setup(self):
        pass

    def type_key_sequence(self, keycodes: list[int]):
        for keycode in keycodes:
            self.ch9329.keyboard_tap(keycode)
            time.sleep(0.1)

    def type_key(self, keycode: Union[int, list[int]]):
        if isinstance(keycode, list):
            self.ch9329.keyboard_tap(*keycode)
        else:
            self.ch9329.keyboard_tap(keycode)

    def type_text(self, text: str):
        logger.info(f"not implemented")
        # self.keyboard_layout.write(text)
        pass

    def handle_key_button(self, keycode: int, is_push: bool):
        if is_push:
            self.ch9329.keyboard_press(keycode)
        else:
            self.ch9329.keyboard_release(keycode)

    def apply_mouse_move(self, state: MouseState):
        if state.x != 0 or state.y != 0 or state.wheel != 0:
            self.ch9329.mouse_move(x=state.x, y=state.y, wheel=state.wheel)
        self._current_mouse_state = state

    def handle_mouse_button(self, button: int, is_push: bool):
        if is_push:
            self.ch9329.mouse_press(button)
        else:
            self.ch9329.mouse_release(button)


def test():
    from ui import UI
    from matrix_leds import MatrixLED
    from ui import UI, PointerAction

    ui = UI()
    matrix_led = MatrixLED()
    pc_usb = PcUSB()

    ui.setup()
    matrix_led.setup()
    pc_usb.setup()

    logger.info("pc usb test start")

    matrix_led.put_all((0x30, 0x00, 0x00), False)
    matrix_led.putxy(0, 2, (0x00, 0x30, 0x00), False)
    matrix_led.putxy(1, 2, (0x00, 0x30, 0x00), False)
    matrix_led.putxy(2, 2, (0x00, 0x00, 0x20), False)
    matrix_led.putxy(3, 2, (0x00, 0x00, 0x20), False)
    matrix_led.write()

    wheel_pressed = False

    while True:
        actions = ui.scan()
        for action in actions.buttons:
            if action.sw_no == 1 and action.is_push:
                logger.info("push H")
                pc_usb.type_key([72])
            if action.sw_no == 2 and action.is_push:
                logger.info("push J")
                pc_usb.type_key([74])
            if action.sw_no == 3 and action.is_push:
                logger.info("push K")
                pc_usb.type_key([75])
            if action.sw_no == 4 and action.is_push:
                logger.info("push L")
                pc_usb.type_key([76])
            if action.sw_no == 9:
                if action.is_push:
                    logger.info("push mouse left")
                else:
                    logger.info("release mouse left")
                # pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, action.is_push)
            if action.sw_no == 10:
                if action.is_push:
                    logger.info("push mouse right")
                else:
                    logger.info("release mouse right")
                # pc_usb.handle_mouse_button(Mouse.RIGHT_BUTTON, action.is_push)
            if action.sw_no == 11:
                wheel_pressed = action.is_push

        action = actions.pointer
        if action.x != 0 or action.y != 0:
            if wheel_pressed:
                logger.info(f"wheel {-action.y}")
                pc_usb.apply_mouse_move(MouseState(0, 0, -action.y))
            else:
                logger.info(f"mouse {action.x},{-action.y}")
                pc_usb.apply_mouse_move(MouseState(action.x, -action.y, 0))

        time.sleep(0.01)
