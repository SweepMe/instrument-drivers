"""Class definition containing telegram 102 execution functions."""

from edcon.profidrive.telegram102 import Telegram102
from edcon.edrive.velocity_telegram_handler import VelocityTelegramHandler
from edcon.edrive.parameter_handler import ParameterHandler

class Telegram102Handler(VelocityTelegramHandler):
    """Basic class for executing telegram 1."""

    def __init__(self, com, skip_validation = False) -> None:
        if not skip_validation:
            ParameterHandler(com).validate("P0.3030101.0.0", 102)
        super().__init__(Telegram102(), com)

    def velocity_info_string(self) -> str:
        """Returns string containing velocity information

        Returns:
            str: String containing velocity information
        """
        return f"Velocity [Target, Current]: " \
            f"[{int(self.telegram.nsoll_b)}, {int(self.telegram.nist_b)}]"

    def _prepare_velocity_task_bits(self, velocity: int):
        """Prepares the telegram bits for velocity task"""
        super()._prepare_velocity_task_bits(velocity)
        self.telegram.nsoll_b.value = velocity
