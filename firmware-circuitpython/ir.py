from typing import Optional
import time
import array
import pulseio
import settings


class IR:
    def __init__(self):
        pass

    def setup(self):
        self.pulseout = pulseio.PulseOut(settings.IR_OUT_PIN)  # type: ignore

        self.pulsein = pulseio.PulseIn(settings.IR_IN_PIN, maxlen=120, idle_state=True)
        self.pulsein.pause()

    def send(self, pulse: list[int]):
        data = array.array("H", pulse)
        print("ir send start")
        for _ in range(3):
            self.pulseout.send(array.array("H", data))
            time.sleep(0.025)
        print("ir send done")

    def receive_ir(self) -> list[int]:
        timeout = 10
        pulses = []
        start = time.monotonic()
        is_received = False
        self.pulsein.clear()
        self.pulsein.resume()
        print("ir listen start")
        while not is_received and (time.monotonic() - start) < timeout:
            time.sleep(0.1)
            while self.pulsein:
                pulse = self.pulsein.popleft()
                pulses.append(pulse)
                is_received = True
        self.pulsein.pause()

        if pulses is None:
            print("cannot receive pulses")
        else:
            print("Heard", len(pulses), "Pulses:", pulses)
        print("ir receive done")

        return pulses


def test_setup():
    global ir
    if ir is None:
        ir = IR()
        ir.setup()


def test_send():
    global ir
    test_setup()
    data = "2403,642,1170,645,588,621,1167,648,588,621,1191,624,588,621,588,621,1167,648,588,621,588,624,585,624,588"
    pulse = [int(x) for x in data.split(",")]
    ir: IR
    print("send ir test start")
    while True:
        print("ir send")
        ir.send(pulse)
        time.sleep(3)


def test_receive():
    global ir
    test_setup()
    ir: IR
    print("receive ir test start")
    pulse = ir.receive_ir()
    print("receive:", pulse)
