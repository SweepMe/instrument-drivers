"""Class definition containing position telegram execution functions."""

from edcon.utils.logging import Logging
from edcon.edrive.telegram_handler import TelegramHandler
from edcon.utils.func_helpers import func_sequence, wait_for, wait_until


class PositionTelegramHandler(TelegramHandler):
    """Basic class for executing position telegrams."""

    def __init__(self, telegram, com) -> None:
        super().__init__(telegram, com)
        # Set default bits for position telegrams
        self.telegram.stw1.do_not_reject_traversing_task = True
        self.telegram.stw1.no_intermediate_stop = True

    def position_info_string(self):
        """Returns string containing position information

        Returns:
            str: String containing position information
        """
        return f"Position [Target, Current]: " \
               f"[{int(self.telegram.mdi_tarpos)}, {int(self.telegram.xist_a)}]"

    def velocity_info_string(self):
        """Returns string containing velocity information

        Returns:
            str: String containing velocity information
        """
        return f"Velocity [Target, Current]: " \
               f"[{int(self.telegram.mdi_velocity)}, {int(self.telegram.nist_b)}]"

    def configure_traversing_to_fixed_stop(self, active: bool):
        """Configures the traversing to fixed stop option (drive maintains parametrized torque)

        Parameters:
            active (bool): True => activate fixed stop traveling, False => deactivate
        """
        self.telegram.stw2.traversing_fixed_stop = active

    def referenced(self):
        """Gives information if drive is referenced

        Returns:
            bool: True if drive home position is set, False otherwise
        """
        self.update_inputs()
        return self.telegram.zsw1.home_position_set

    def target_position_reached(self):
        """Gives information if drive has reached target position

        Returns:
            bool: True if drive target position is reached, False otherwise
        """
        self.update_inputs()
        return self.telegram.zsw1.target_position_reached

    def stopped(self):
        """Gives information if drive is stopped

        Returns:
            bool: True if drive is stopped, False otherwise
        """
        self.update_inputs()
        return self.telegram.zsw1.drive_stopped

    def wait_for_referencing_task_ack(self) -> bool:
        """Waits for drive to be referenced

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for referencing task to be acknowledged")
        if not self.telegram.stw1.start_homing_procedure:
            return False

        Logging.logger.info("=> Referencing task acknowledged")
        return True

    def wait_for_home_position_set(self) -> bool:
        """Waits for drive to be referenced

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for reference")

        def cond():
            self.update_inputs()
            return self.telegram.zsw1.home_position_set

        if not wait_until(cond, self.fault_present,
                          info_string=self.position_info_string,
                          error_string=self.fault_string):
            return False
        Logging.logger.info("=> Reference position set")
        return True

    def wait_for_traversing_task_ack(self) -> bool:
        """Waits for drive to be referenced

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for traversing task to be acknowledged")

        def cond():
            self.update_inputs()
            return self.telegram.zsw1.traversing_task_ack
        if not wait_until(cond, self.fault_present,
                          info_string=self.position_info_string,
                          error_string=self.fault_string):
            return False
        Logging.logger.info("=> Traversing task acknowledged")
        return True

    def wait_for_target_position(self) -> bool:
        """Waits for target position to be reached

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for target position to be reached")

        def cond():
            self.update_inputs()
            return self.telegram.zsw1.target_position_reached

        if not wait_until(cond, self.fault_present,
                          info_string=self.position_info_string,
                          error_string=self.fault_string):
            return False
        Logging.logger.info("=> Target position reached")
        return True

    def wait_for_stop(self) -> bool:
        """Waits for target position to be reached

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for drive to stop")

        def cond():
            self.update_inputs()
            return self.telegram.zsw1.drive_stopped

        if not wait_until(cond, self.fault_present,
                          info_string=self.velocity_info_string,
                          error_string=self.fault_string):
            return False
        Logging.logger.info("=> Drive stopped")
        return True

    def wait_for_referencing_execution(self) -> bool:
        """Waits for referencing to be finished

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.wait_for_referencing_task_ack():
            return False

        if not self.wait_for_home_position_set():
            return False
        self.stop_motion_task()
        Logging.logger.info("=> Finished referencing task")
        return True

    def wait_for_position_motion_execution(self) -> bool:
        """Waits for position motion to be finished

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.wait_for_traversing_task_ack():
            return False

        if not self.wait_for_target_position():
            return False
        self.stop_motion_task()
        Logging.logger.info("=> Finished position motion task")
        return True

    def trigger_record_change(self):
        """Triggers the change to the next record of the record sequence"""
        Logging.logger.info("Set record change bit")

        def toggle_func(value):
            self.telegram.stw1.change_record_no = value
            self.update_outputs()

        func_sequence(toggle_func, [True, False])

        Logging.logger.info("=> Finished record change")

    def _prepare_stop_motion_task_bits(self):
        """Prepares the telegram bits for stopping the current motion"""
        # Reset activate_traversing_task bit to prepare for next time
        self.telegram.stw1.activate_traversing_task = False

        # Reset jog bits (in case jogging motion was performed)
        self.telegram.stw1.jog1_on = False
        self.telegram.stw1.jog2_on = False

        # Reset referencing bits (in case referencing motion was performed)
        self.telegram.stw1.start_homing_procedure = False

        # Actual stop command
        self.telegram.stw1.do_not_reject_traversing_task = False

    def stop_motion_task(self):
        """Stops any currently active motion task"""
        Logging.logger.info("Stopping motion")

        self._prepare_stop_motion_task_bits()
        self.update_outputs()

        self.telegram.stw1.do_not_reject_traversing_task = True

        self.wait_for_stop()

    def pause_motion_task(self):
        """Pauses any currently active motion task"""
        Logging.logger.info("Pausing motion")
        # Reset activate_traversing_task bit to prepare for next time
        self.telegram.stw1.activate_traversing_task = False

        # Actual pause command
        self.telegram.stw1.no_intermediate_stop = False
        self.update_outputs()

        self.wait_for_stop()

    def resume_motion_task(self):
        """Resumes any currently active motion task"""
        Logging.logger.info("Resuming motion")
        self.telegram.stw1.no_intermediate_stop = True
        self.update_outputs()

    def referencing_task(self, nonblocking: bool = False) -> bool:
        """Perform the referencing sequence. If successful, the drive is referenced afterwards.

        Parameters:
            nonblocking (bool): If True, tasks returns immediately after starting the task.
                                Otherwise function awaits for finish (or fault).
        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.ready_for_motion():
            Logging.logger.error("Referencing task aborted")
            return False
        Logging.logger.info("Start referencing task using the homing method")
        self.telegram.stw1.start_homing_procedure = True
        self.update_outputs()

        if nonblocking:
            return True

        return self.wait_for_referencing_execution()

    def _prepare_position_task_bits(self, position: int, velocity: int,
                                    absolute: bool = False  # pylint: disable=unused-argument
                                    ):
        """Prepares the telegram bits for positioning task"""
        self.telegram.mdi_tarpos.value = position
        self.telegram.mdi_velocity.value = velocity
        self.telegram.stw1.activate_traversing_task = True

    def position_task(self, position: int, velocity: int, absolute: bool = False,
                      nonblocking: bool = False) -> bool:
        """Perform a position task with the given parameters

        Parameters:
            position (int): position setpoint in user units (depends on parametrization)
            velocity (int): velocity setpoint in user units (depends on parametrization)
            absolute (bool): If true, position is considered absolute,
                             otherwise relative to starting position
            nonblocking (bool): If True, tasks returns immediately after starting the task.
                                Otherwise function awaits for finish (or fault).

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.ready_for_motion():
            Logging.logger.error("Traversing task aborted")
            return False
        Logging.logger.info("Start traversing task")

        self._prepare_position_task_bits(position, velocity, absolute)
        self.update_outputs()

        if nonblocking:
            return True

        return self.wait_for_position_motion_execution()

    def _prepare_jog_task_bits(self, jog_positive: bool = True, jog_negative: bool = False,
                               incremental: bool = False  # pylint: disable=unused-argument
                               ):
        """Prepares the telegram bits for jog task"""
        self.telegram.stw1.jog1_on = jog_positive
        self.telegram.stw1.jog2_on = jog_negative

    def jog_task(self, jog_positive: bool = True, jog_negative: bool = False,
                 incremental: bool = False, duration: float = 0.0) -> bool:
        """Perform a jogging task with a given duration.
            Please note that the jogging motion stops if jog_positive and jog_negative are equal.

        Parameters:
            jog_positive (bool): If true, jog in positive direction.
            jog_negative (bool): If true, jog in negative direction.

            duration (float): Optional duration in seconds.
                              A duration of 0 starts the task and returns immediately.

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.ready_for_motion():
            Logging.logger.error("Jogging task aborted")
            return False
        Logging.logger.info("Start jogging task")

        self._prepare_jog_task_bits(jog_positive, jog_negative, incremental)
        self.update_outputs()

        if duration == 0:
            return True

        # Wait for predefined amount of time
        if not wait_for(duration, self.fault_present, self.position_info_string, self.fault_string):
            return False

        self.stop_motion_task()
        Logging.logger.info("=> Finished jogging task")
        return True
