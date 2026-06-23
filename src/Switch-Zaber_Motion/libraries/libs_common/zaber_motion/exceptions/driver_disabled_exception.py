# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .command_failed_exception import CommandFailedException


class DriverDisabledException(CommandFailedException):
    """
    Thrown when a device cannot carry out a movement command because the motor driver is disabled.
    """
