# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .command_failed_exception import CommandFailedException


class BadCommandException(CommandFailedException):
    """
    Thrown when a device receives an invalid command.
    """
