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
