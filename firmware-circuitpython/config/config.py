from adafruit_hid.keycode import Keycode
from led_color import *
from model import *
from action_codes import (
    CM_SEND_IR,
    CM_TYPE_KEY,
    KC_MOUSE_L,
    KC_MOUSE_R,
    KC_MOUSE_W,
)

from . import ir_pulse

KC_TV_POWER: KeyAssign = (CM_SEND_IR, ir_pulse.TV_POWER)
KC_TV_CHANGE_INPUT: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CHANGE_INPUT)
KC_TV_CURSOR_LEFT: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_LEFT)
KC_TV_CURSOR_RIGHT: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_RIGHT)
KC_TV_CURSOR_UP: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_UP)
KC_TV_CURSOR_DOWN: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_DOWN)
KC_TV_CURSOR_OK: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_OK)
KC_TV_CURSOR_BACK: KeyAssign = (CM_SEND_IR, ir_pulse.TV_CURSOR_BACK)

KC_CTRL_W: KeyAssign = [(CM_TYPE_KEY, [Keycode.W, Keycode.CONTROL])]
KC_ENTER: KeyAssign = [(CM_TYPE_KEY, Keycode.ENTER)]
KC_ESC: KeyAssign = [(CM_TYPE_KEY, Keycode.ESCAPE)]

LAYER1: Layer = [
    [KC_TV_POWER, KC_TV_CURSOR_BACK, KC_TV_CURSOR_UP, KC_TV_CURSOR_OK],
    [KC_TV_CHANGE_INPUT, KC_TV_CURSOR_LEFT, KC_TV_CURSOR_DOWN, KC_TV_CURSOR_RIGHT],
    [KC_MOUSE_L, KC_MOUSE_R, KC_CTRL_W, KC_ESC],
]

LAYER1_LED: LayerLED = [
    [L_RED, L_YELLOW, L_WHITE, L_PURPLE],
    [L_GREEN, L_WHITE, L_WHITE, L_WHITE],
    [L_CYAN, L_CYAN, L_GREEN, L_GREEN],
]

LAYERS: Layers = [LAYER1]
LAYERS_LED: LayersLED = [LAYER1_LED]
