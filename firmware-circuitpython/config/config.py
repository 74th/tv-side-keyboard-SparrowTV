from adafruit_hid.keycode import Keycode
from action_codes import (
    CM_SEND_IR,
    CM_TYPE_KEY,
    KC_MOUSE_L,
    KC_MOUSE_R,
    KC_MOUSE_W,
)

from . import ir_pulse

KC_TV_POWER = [(CM_SEND_IR, ir_pulse.TV_POWER)]
KC_CTRL_W = [(CM_TYPE_KEY, Keycode.W, Keycode.CONTROL)]

LAYER1 = [
    [KC_TV_POWER, None, None, None],
    [KC_CTRL_W, None, None, None],
    [None, None, None, None],
    [KC_MOUSE_L, KC_MOUSE_R, KC_MOUSE_W, None],
]

LAYER1_LED = [
    [],
    [],
    [],
]

LAYERS = [LAYER1]
LAYERS_LED = [LAYER1_LED]
