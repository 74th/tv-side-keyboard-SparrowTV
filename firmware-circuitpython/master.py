import time
from typing import cast, Any, TypeAlias, Union
from adafruit_hid.mouse import Mouse
from ir import IR
from matrix_buttons import MatrixButtons, ButtonAction
from matrix_leds import MatrixLED, LEDColor
from pointer import Pointer
from pc_usb import PcUSB
from action_codes import *

ActionCode = int
Action: TypeAlias = "tuple[ActionCode, Any]"
Layer: TypeAlias = "list[list[Union[Action, None]]]"
LayerLED: TypeAlias = "list[list[Union[LEDColor, None]]]"


class Master:
    def __init__(self):
        self.ir = IR()
        self.matrix_buttons = MatrixButtons()
        self.matrix_led = MatrixLED()
        self.pointer = Pointer()
        self.pc_usb = PcUSB()

    def setup(self):
        self.ir.setup()
        self.matrix_buttons.setup()
        self.matrix_led.setup()
        self.pointer.setup()
        self.pc_usb.setup()

    def _load_config(self):
        from config import config

        self.layers_map = cast("list[Layer]", config.LAYERS)
        self.layers_led = cast("list[LayerLED]", config.LAYERS_LED)

        self._load_layer(0)

    def _load_layer(self, no: int):
        n = 0
        layer = []
        for row in self.layers_map[no]:
            for f in row:
                layer.append(f)
                n += 1
        self.layer = cast("list[Union[Action, None]]", layer)

    def _set_layer_led(self, no: int):
        for y, row in enumerate(self.layers_led[no]):
            for x, l in enumerate(row):
                if l is not None:
                    self.matrix_led.putxy(x, y, l, False)
        self.matrix_led.write()

    def _handle_action(self, func: Action, btn: ButtonAction):
        code = func[0]
        if code == CM_DELAY:
            time.sleep(func[1])
        if code == CM_TYPE_KEY:
            if isinstance(func[1], list):
                self.pc_usb.key_types(func[1])
            else:
                self.pc_usb.key_type(func[1])
        if code == CM_SEND_IR:
            self.ir.send(func[1])
        if code == CM_LED_XY:
            x, y, g, r, b = func[1]
            self.matrix_led.putxy(x, y, (g, r, b))
        if code == CM_MOUSE_LEFT:
            self.pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, btn.is_push)
        if code == CM_MOUSE_RIGHT:
            self.pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, btn.is_push)
        if code == CM_MOUSE_WHEEL:
            self.pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, btn.is_push)

    def _loop(self):
        button_actions = self.matrix_buttons.scan()
        for button_action in button_actions:
            if len(self.layer) >= button_action.sw_no:
                print(f"unknown button no: {button_action.sw_no}")
                continue
            action = self.layer[button_action.sw_no]
            if action is None:
                continue
            self._handle_action(action, button_action)

    def run(self):
        while True:
            self._loop()
            time.sleep(0.001)
