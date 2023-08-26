# --- General Action ---
# (CM_DELAY, 0.2)
CM_DELAY = 10

# --- Keyboard Action ---
# type key
# (CM_TYPE_KEY, Keycode.A)
# (CM_TYPE_KEY, (Keycode.W, Keycode.CONTROL))
CM_TYPE_KEY = 20
# type text
# (CM_TYPE_KEY, "hello")
CM_TYPE_TEXT = 21
# type text
# (CM_TYPE_KEY, [Keycode.A, Keycode.B, Keycode.C]
CM_TYPE_SEQUENCE = 22

# --- IR Action ---
# (CM_IR_SEND, list[int])
CM_SEND_IR = 30

# --- LED Action ---
# (CM_LED_XY, (x, y, g, r, b))
CM_LED_XY = 40

# --- Mouse Button ---
CM_MOUSE_LEFT = 50
CM_MOUSE_RIGHT = 51
CM_MOUSE_WHEEL = 52

KC_MOUSE_L = CM_MOUSE_LEFT
KC_MOUSE_R = CM_MOUSE_RIGHT
KC_MOUSE_W = CM_MOUSE_WHEEL

ACTION_CODE_NAMES = {
    CM_DELAY: "CM_DELAY",
    CM_TYPE_KEY: "CM_TYPE_KEY",
    CM_TYPE_TEXT: "CM_TYPE_TEXT",
    CM_SEND_IR: "CM_SEND_IR",
    CM_LED_XY: "CM_LED_XY",
    CM_MOUSE_LEFT: "CM_MOUSE_LEFT",
    CM_MOUSE_RIGHT: "CM_MOUSE_RIGHT",
    CM_MOUSE_WHEEL: "CM_MOUSE_WHEEL",
}

ACTION_CODES = {
    "CM_DELAY": CM_DELAY,
    "CM_TYPE_KEY": CM_TYPE_KEY,
    "CM_TYPE_TEXT": CM_TYPE_TEXT,
    "CM_SEND_IR": CM_SEND_IR,
    "CM_LED_XY": CM_LED_XY,
    "CM_MOUSE_LEFT": CM_MOUSE_LEFT,
    "CM_MOUSE_RIGHT": CM_MOUSE_RIGHT,
    "CM_MOUSE_WHEEL": CM_MOUSE_WHEEL,
}


def get_action_code_name(code: int) -> str:
    return ACTION_CODE_NAMES[code]
