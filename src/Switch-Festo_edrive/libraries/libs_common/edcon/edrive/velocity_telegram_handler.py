"""Class definition containing velocity telegram execution functions."""

from edcon.utils.logging import Logging
from edcon.edrive.telegram_handler import TelegramHandler
from edcon.utils.func_helpers import wait_for


class VelocityTelegramHandler(TelegramHandler):
    """Basic class for executing velocity telegrams."""

    def __init__(self, telegram, com) -> None:
        super().__init__(telegram, com)

        # Set default bits for velocity telegrams
        self.telegram.stw1.enable_ramp_generator = True
        self.telegram.stw1.unfreeze_ramp_generator = True

    def velocity_info_string(self) -> str:
        """Returns string containing velocity information

        Returns:
            str: String containing velocity information
        """
        return "Unknown velocity"

    def stop_motion_task(self):
        """Stops any currently active motion task"""
        Logging.logger.info("Stopping motion")
        self.telegram.stw1.setpoint_enable = False
        self.update_outputs()

    def _prepare_velocity_task_bits(self,
                                    velocity: int  # pylint: disable=unused-argument
                                    ):
        """Prepares the telegram bits for velocity task"""
        self.telegram.stw1.setpoint_enable = True

    def velocity_task(self, velocity: int, duration: float = 0.0) -> bool:
        """Perform a velocity task with the given parameters using setup mode.

        Parameters:
            velocity (int): velocity setpoint in user units (depends on parametrization).
                            The sign determines the direction of the motion.
            duration (float): Optional duration in seconds.
                              A duration of 0 starts the task and returns immediately.

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.ready_for_motion():
            Logging.logger.error("Velocity task aborted")
            return False
        Logging.logger.info("Start velocity task")

        self._prepare_velocity_task_bits(velocity)
        self.update_outputs()

        if duration == 0:
            return True

        # Wait for predefined amount of time
        if not wait_for(duration, self.fault_present,
                        self.velocity_info_string, self.fault_string):
            return False

        self.stop_motion_task()
        Logging.logger.info("=> Finished velocity task")
        return True
