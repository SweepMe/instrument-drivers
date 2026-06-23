"""Class definition containing telegram 1 execution functions."""

from edcon.profidrive.telegram1 import Telegram1
from edcon.edrive.velocity_telegram_handler import VelocityTelegramHandler
from edcon.edrive.parameter_handler import ParameterHandler

class Telegram1Handler(VelocityTelegramHandler):
    """Basic class for executing telegram 1."""

    def __init__(self, com, skip_validation = False) -> None:
        if not skip_validation:
            ParameterHandler(com).validate("P0.3030101.0.0", 1)
        super().__init__(Telegram1(), com)

    def velocity_info_string(self) -> str:
        """Returns string containing velocity information

        Returns:
            str: String containing velocity information
        """
        return f"Velocity [Target, Current]: " \
            f"[{int(self.telegram.nsoll_a)}, {int(self.telegram.nist_a)}]"

    def _prepare_velocity_task_bits(self, velocity: int):
        """Prepares the telegram bits for velocity task"""
        super()._prepare_velocity_task_bits(velocity)
        self.telegram.nsoll_a.value = velocity
