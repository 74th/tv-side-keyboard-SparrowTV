import master
import uart_logging_handler
import adafruit_logging as logging

logger = logging.getLogger()


def main():
    uart_logging_handler.setup()
    logger.info("start initialize")
    m = master.Master()
    m.setup()
    logger.info("done")
    logger.info("start running")
    m.run()


if __name__ == "__main__":
    main()
