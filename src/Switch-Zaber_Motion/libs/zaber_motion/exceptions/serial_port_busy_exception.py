# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .connection_failed_exception import ConnectionFailedException


class SerialPortBusyException(ConnectionFailedException):
    """
    Thrown when a serial port cannot be opened because it is in use by another application.
    """
