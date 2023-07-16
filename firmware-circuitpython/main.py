import usb_hid
import time
import array
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import pulseio
import adafruit_irremote
import digitalio
import board



def test_keyboard():
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)

    btn = digitalio.DigitalInOut(board.IO0)
    btn.switch_to_input(pull=digitalio.Pull.UP)

    btn_status = [True for _ in range(1)]

    while True:
        time.sleep(1)
        print(btn.value)
        if btn_status[0] != btn.value and not btn.value:
            kbd.send(Keycode.A)
        btn_status[0] = btn.value

def test_ir():
    pulsein = pulseio.PulseIn(board.IO7, maxlen=120, idle_state=True)
    ir_decoder = adafruit_irremote.GenericDecode()
    pulseout = pulseio.PulseOut(board.IO1)

    while True:
        pulsein.clear()
        print()
        time.sleep(1)
        print("read start")
        pulsein.resume()
        receive_data = ir_decoder.read_pulses(pulsein)
        pulsein.pause()
        print("Heard", len(receive_data), "Pulses:", receive_data)
        # send_data = array.array("H", [2450])
        # for p in receive_data:
        #     send_data.append(p)
        #     send_data.append(650)
        time.sleep(1)
        print("send")
        pulseout.send(array.array('H', receive_data))
        print("----------------------------")

def test_send_ir():
    btn = digitalio.DigitalInOut(board.IO0)

    btn.switch_to_input(pull=digitalio.Pull.UP)
    pulseout = pulseio.PulseOut(board.IO1)

    led = digitalio.DigitalInOut(board.IO5)
    led.switch_to_output(False)

    btn_status = [True for _ in range(1)]

    data = array.array("H", [2403, 642, 1170, 645, 588, 621, 1167, 648, 588, 621, 1191, 624, 588, 621, 588, 621, 1167, 648, 588, 621, 588, 624, 585, 624, 588])

    while True:
        time.sleep(0.1)
        if btn_status[0] != btn.value and not btn.value:
            print("send")
            for _ in range(3):
                led.value = True
                pulseout.send(array.array('H', data))
                time.sleep(0.025)
            print("send done")
            time.sleep(1)
            led.value = False


# test_keyboard()
# test_ir()
test_send_ir()