# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .command_failed_exception import CommandFailedException


class BadDataException(CommandFailedException):
    """
    Thrown when a parameter of a command is judged to be out of range by the receiving device.
    """
