import time
import array
import json
import socketpool
import wifi
import usb_hid
import pulseio
import adafruit_irremote
import digitalio
import board
from adafruit_httpserver import Server, Request, Response
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


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

def setup_button():
    global btn
    btn = digitalio.DigitalInOut(board.IO0)
    btn.switch_to_input(pull=digitalio.Pull.UP)

def setup_keyboard():
    global kbd, typed
    kbd = Keyboard(usb_hid.devices)
    typed = False

def handle_button_as_keyboard():
    global typed
    if typed != btn.value and not btn.value:
        print("type A")
        kbd.send(Keycode.A)
    typed = btn.value


def setup_api():
    global api
    pool = socketpool.SocketPool(wifi.radio)
    api = Server(pool, None, debug=True)

    @api.route("/api/hello", methods="GET")
    def hello(request: Request):
        res = {"success": True}
        return Response(request, json.dumps(res))

    api.start(str(wifi.radio.ipv4_address))

def handle_api():
    global api
    api.poll()


def main():
    import matrix_buttons
    matrix_buttons.test()
    return
    print("\n initializing")

    setup_button()
    setup_keyboard()
    setup_api()

    print("start main loop")
    while True:
        handle_button_as_keyboard()
        handle_api()
        time.sleep(0.01)

if __name__ == "__main__":
    main()