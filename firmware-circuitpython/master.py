import time
from typing import cast, Any, TypeAlias, Union
from adafruit_hid.mouse import Mouse
import adafruit_logging as logging
from ir import IR
from matrix_buttons import MatrixButtons, ButtonAction
from matrix_leds import MatrixLED, LEDColor
from pointer import Pointer
from pc_usb import MouseState, PcUSB
import led_color
from action_codes import *
from model import *

logger = logging.getLogger()

POINTER_WORK_DURATION_NS = 100_000


class Master:
    def __init__(self):
        self.ir = IR()
        self.matrix_buttons = MatrixButtons()
        self.matrix_led = MatrixLED()
        self.pointer = Pointer()
        self.pc_usb = PcUSB()

        self._pointer_work_time_ns = 0
        self._is_wheel_mode = False

    def setup(self):
        self.ir.setup()
        self.matrix_buttons.setup()
        self.matrix_led.setup()
        self.pointer.setup()
        self.pc_usb.setup()

        self._load_config()

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
        self.layer = cast("list[KeyAssign]", layer)

        self._set_layer_led(no)

    def _set_layer_led(self, no: int):
        for y, row in enumerate(self.layers_led[no]):
            for x, l in enumerate(row):
                if l is not None:
                    self.matrix_led.putxy(x, y, l, False)
                else:
                    self.matrix_led.putxy(x, y, led_color.L_BLACK, False)
        self.matrix_led.write()

    def _handle_action(self, action: Action, btn: ButtonAction):
        if isinstance(action, int):
            code = action
            args: Any = None
        else:
            code = action[0]
            args = action[1]
        if code == CM_DELAY:
            logger.info(f"DELAY duration(ms):{args[0]}")
            time.sleep(args)
        if code == CM_TYPE_KEY:
            logger.info(f"TYPE_KEY key:{args}")
            try:
                self.pc_usb.type_key(args)
            except Exception as e:
                logger.info(f"TYPE_KEY failed: {e}")
        if code == CM_TYPE_TEXT and btn.is_push:
            logger.info(f"TYPE_TEXT text:{args}")
            self.pc_usb.type_text(cast(str, args))
        if code == CM_SEND_IR and btn.is_push:
            logger.info(f"SEND_IR len:{len(args)}")
            self.ir.send(args)
        if code == CM_LED_XY:
            logger.info(
                f"LED_XY x:{args[0]} y:{args[1]} color:({args[2]},{args[3]},{args[4]})"
            )
            x, y, g, r, b = args
            self.matrix_led.putxy(x, y, (g, r, b))
        if code == CM_MOUSE_LEFT:
            logger.info(f"MOUSE_LEFT push:{btn.is_push}")
            self.pc_usb.handle_mouse_button(Mouse.LEFT_BUTTON, btn.is_push)
        if code == CM_MOUSE_RIGHT:
            logger.info(f"MOUSE_RIGHT push:{btn.is_push}")
            self.pc_usb.handle_mouse_button(Mouse.RIGHT_BUTTON, btn.is_push)
        if code == CM_MOUSE_WHEEL:
            logger.info(f"MOUSE_WHEEL push:{btn.is_push}")
            self._is_wheel_mode = btn.is_push

    def _handle_matrix_buttons(self):
        button_actions = self.matrix_buttons.scan()
        for button_action in button_actions:
            if button_action.sw_no - 1 >= len(self.layer):
                logger.info(f"unknown button no: {button_action.sw_no}")
                continue
            action = self.layer[button_action.sw_no - 1]
            if button_action.is_push:
                logger.info(f"pushed sw:{button_action.sw_no}")
            else:
                logger.info(f"released sw:{button_action.sw_no}")
            if action is None:
                logger.info(f"no action")
                continue
            if isinstance(action, list):
                for a in action:
                    self._handle_action(a, button_action)
            else:
                self._handle_action(action, button_action)

    def _handle_pointer(self):
        now = time.monotonic_ns()

        if self._pointer_work_time_ns + POINTER_WORK_DURATION_NS > now:
            return

        self._pointer_work_time_ns = now

        p = self.pointer.scan()
        if p is None:
            return

        if self._is_wheel_mode:
            if p.y > 0:
                w = 1
            elif p.y < 0:
                w = -1
            else:
                return
            self.pc_usb.apply_mouse_move(MouseState(0, 0, w))
            return

        self.pc_usb.apply_mouse_move(MouseState(2 * p.x, -2 * p.y, 0))

    def _loop(self):
        self._handle_matrix_buttons()
        self._handle_pointer()

    def run(self):
        while True:
            self._loop()
            time.sleep(0.001)
