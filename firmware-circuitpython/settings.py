import board

IR_OUT_PIN = board.IO14
IR_IN_PIN = board.IO12

BUTTON_MATRIX_COL_PINS = [
    board.IO1,
    board.IO2,
    board.IO3,
    board.IO4,
]
BUTTON_MATRIX_ROW_PINS = [
    board.IO5,
    board.IO6,
    board.IO7,
]

I2C_SDA_PIN = board.IO13
I2C_SCL_PIN = board.IO15

MATRIX_LED_PIN = board.IO16
STAMP_LED_PIN = board.IO21

MATRIX_MAP = [[1,5,9,2],
              [6,10,3,7],
              [11,4,8,12]
              ]