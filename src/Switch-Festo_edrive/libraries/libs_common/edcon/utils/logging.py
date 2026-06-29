"""Contains class which contains logging methods."""
import logging
from rich.logging import RichHandler


class Logging:
    """Class that contains common functions for logging."""

    logger = logging.getLogger('edcon')
    def __init__(self, logging_level=logging.INFO, filename=None):
        logging.basicConfig(format='%(message)s',
                            datefmt="[%X]",
                            handlers=[RichHandler()])

        Logging.logger.setLevel(logging_level)
        Logging.logger.propagate = False

        if filename:
            self.enable_file_logging(filename, logging_level)
        else:
            self.enable_stream_logging(logging_level)

    def enable_stream_logging(self, logging_level):
        """Enables logging to stream using the provided log level with rich log formatting."""
        handler = RichHandler()
        handler.setLevel(logging_level)
        formatter = logging.Formatter(fmt='%(message)s', datefmt="[%X]")
        handler.setFormatter(formatter)
        Logging.logger.addHandler(handler)

    def enable_file_logging(self, filename, logging_level):
        """Enables logging to a file using the provided filename and log level."""
        handler = logging.FileHandler(filename)
        handler.setLevel(logging_level)
        formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                      datefmt="[%X]")
        handler.setFormatter(formatter)
        Logging.logger.addHandler(handler)
