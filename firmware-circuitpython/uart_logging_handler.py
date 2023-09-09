from typing import Any, cast
import board
from busio import UART
from adafruit_logging import Handler, LogRecord
import adafruit_logging as logging


class UartSTDIOHandler(Handler):
    """Send logging output to a serial port."""

    def __init__(self, uart: UART):
        """Create an instance.

        :param uart: the busio.UART instance to which to write messages
        """
        self._uart = uart
        self.level = logging.INFO

    def format(self, record: LogRecord):
        """Generate a string to log.

        :param record: The record (message object) to be logged
        """
        return super().format(record) + "\r\n"

    def emit(self, record: LogRecord):
        """Generate the message and write it to the UART.

        :param record: The record (message object) to be logged
        """
        self._uart.write(bytes(self.format(record), "utf-8"))
        print(f"{record.created}: {record.levelname} - {record.msg}")


def setup():
    uart = UART(board.TX, board.RX, baudrate=115200)
    logger = logging.getLogger()
    logger.addHandler(cast(Any, UartSTDIOHandler(uart)))
    logger.setLevel(logging.INFO)  # type: ignore
    logger.info("------ initialized --------")
    logger.info("logger setup done")
