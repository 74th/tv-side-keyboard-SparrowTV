from typing import Any, cast
from busio import UART
from adafruit_logging import Handler, LogRecord
import adafruit_logging as logging


class STDIOHandler(Handler):
    """Send logging output to a serial port."""

    def __init__(self):
        """Create an instance.

        :param uart: the busio.UART instance to which to write messages
        """
        self.level = logging.INFO  # type: ignore

    def format(self, record: LogRecord):
        """Generate a string to log.

        :param record: The record (message object) to be logged
        """
        return super().format(record)

    def emit(self, record: LogRecord):
        """Generate the message and write it to the UART.

        :param record: The record (message object) to be logged
        """
        print(self.format(record))


def setup():
    logger = logging.getLogger()
    logger.addHandler(cast(Any, STDIOHandler()))
    logger.setLevel(logging.INFO)  # type: ignore
    logger.info("------ initialized --------")
    logger.info("logger setup done")
