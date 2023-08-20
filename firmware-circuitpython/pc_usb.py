import usb_hid
from adafruit_hid.keyboard import Keyboard, Keycode
from adafruit_hid.mouse import Mouse
import time


class MouseState:
    def __init__(self, x: int, y: int, wheel: int):
        self.x = x
        self.y = y
        self.wheel = wheel


class PcUSB:
    def __init__(self):
        self.keyboard = Keyboard(usb_hid.devices)  # type: ignore
        self.mouse = Mouse(usb_hid.devices)  # type: ignore
        self._current_mouse_state = MouseState(0, 0, 0)

    def setup(self):
        pass

    def key_types(self, keycodes: list[int]):
        for keycode in keycodes:
            self.keyboard.send(keycode)
            time.sleep(0.001)

    def key_type(self, keycode: list[int]):
        self.keyboard.send(*keycode)

    def handle_key_button(self, keycode: int, is_push: bool):
        if is_push:
            self.keyboard.press(keycode)
        else:
            self.keyboard.release(keycode)

    def apply_mouse_move(self, state: MouseState):
        if state.x != 0 or state.y != 0 or state.wheel != 0:
            self.mouse.move(x=state.x, y=state.y, wheel=state.wheel)
        self._current_mouse_state = state

    def handle_mouse_button(self, button: int, is_push: bool):
        if is_push:
            self.mouse.press(button)
        else:
            self.mouse.release(button)


def test():
    from matrix_buttons import MatrixButtons
    from matrix_leds import MatrixLED
    from pointer import Pointer, PointerAction

    matrix_buttons = MatrixButtons()
    matrix_led = MatrixLED()
    pointer = Pointer()
    pc_usb = PcUSB()

    matrix_buttons.setup()
    matrix_led.setup()
    pointer.setup()
    pc_usb.setup()

    print("pc usb test start")

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
                print("push H")
                pc_usb.key_type([Keycode.H])
            if action.sw_no == 2 and action.is_push:
                print("push J")
                pc_usb.key_type([Keycode.J])
            if action.sw_no == 3 and action.is_push:
                print("push K")
                pc_usb.key_type([Keycode.K])
            if action.sw_no == 4 and action.is_push:
                print("push L")
                pc_usb.key_type([Keycode.L])
            if action.sw_no == 9:
                if action.is_push:
                    print("push mouse left")
                else:
                    print("release mouse left")
                pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, action.is_push)
            if action.sw_no == 10:
                if action.is_push:
                    print("push mouse right")
                else:
                    print("release mouse right")
                pc_usb.handle_mouse_button(Mouse.RIGHT_BUTTON, action.is_push)
            if action.sw_no == 11:
                wheel_pressed = action.is_push

        action = pointer.scan()
        if action.x != 0 or action.y != 0:
            if wheel_pressed:
                print(f"wheel {-action.y}")
                pc_usb.apply_mouse_move(MouseState(0, 0, -action.y))
            else:
                print(f"mouse {action.x},{-action.y}")
                pc_usb.apply_mouse_move(MouseState(action.x, -action.y, 0))

        time.sleep(0.01)
