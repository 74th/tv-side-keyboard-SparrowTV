from typing import Union

# import usb_hid

from adafruit_hid.keyboard import Keycode

# from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
# from adafruit_hid.mouse import Mouse
import adafruit_logging as logging
import time

logger = logging.getLogger()


class MouseState:
    def __init__(self, x: int, y: int, wheel: int):
        self.x = x
        self.y = y
        self.wheel = wheel


class PcUSB:
    def __init__(self):
        # self.keyboard = Keyboard(usb_hid.devices)  # type: ignore
        # self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
        # self.mouse = Mouse(usb_hid.devices)  # type: ignore
        self._current_mouse_state = MouseState(0, 0, 0)

    def setup(self):
        pass

    def type_key_sequence(self, keycodes: list[int]):
        pass
        # for keycode in keycodes:
        #     self.keyboard.send(keycode)
        #     time.sleep(0.001)

    def type_key(self, keycode: Union[int, list[int]]):
        pass
        # if isinstance(keycode, list):
        #     self.keyboard.send(*keycode)
        # else:
        #     self.keyboard.send(keycode)

    def type_text(self, text: str):
        pass
        # self.keyboard_layout.write(text)

    def handle_key_button(self, keycode: int, is_push: bool):
        pass
        # if is_push:
        #     self.keyboard.press(keycode)
        # else:
        #     self.keyboard.release(keycode)

    def apply_mouse_move(self, state: MouseState):
        pass
        # if state.x != 0 or state.y != 0 or state.wheel != 0:
        #     self.mouse.move(x=state.x, y=state.y, wheel=state.wheel)
        # self._current_mouse_state = state

    def handle_mouse_button(self, button: int, is_push: bool):
        pass
        # if is_push:
        #     self.mouse.press(button)
        # else:
        #     self.mouse.release(button)


def test():
    from matrix_buttons import MatrixButtons
    from matrix_leds import MatrixLED
    from ui import UI, PointerAction

    matrix_buttons = MatrixButtons()
    matrix_led = MatrixLED()
    pointer = UI()
    pc_usb = PcUSB()

    matrix_buttons.setup()
    matrix_led.setup()
    pointer.setup()
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
        actions = matrix_buttons.scan()
        for action in actions:
            if action.sw_no == 1 and action.is_push:
                logger.info("push H")
                pc_usb.type_key([Keycode.H])
            if action.sw_no == 2 and action.is_push:
                logger.info("push J")
                pc_usb.type_key([Keycode.J])
            if action.sw_no == 3 and action.is_push:
                logger.info("push K")
                pc_usb.type_key([Keycode.K])
            if action.sw_no == 4 and action.is_push:
                logger.info("push L")
                pc_usb.type_key([Keycode.L])
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

        action = pointer.scan()
        if action.x != 0 or action.y != 0:
            if wheel_pressed:
                logger.info(f"wheel {-action.y}")
                pc_usb.apply_mouse_move(MouseState(0, 0, -action.y))
            else:
                logger.info(f"mouse {action.x},{-action.y}")
                pc_usb.apply_mouse_move(MouseState(action.x, -action.y, 0))

        time.sleep(0.01)
