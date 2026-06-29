"""Class definition containing telegram 111 execution functions."""

import time
from edcon.utils.logging import Logging
from edcon.edrive.diagnosis import diagnosis_name, diagnosis_remedy
from edcon.edrive.position_telegram_handler import PositionTelegramHandler
from edcon.profidrive.telegram111 import Telegram111
from edcon.utils.func_helpers import wait_for, wait_until
from edcon.edrive.parameter_handler import ParameterHandler

class Telegram111Handler(PositionTelegramHandler):
    """Basic class for executing telegram 111."""

    def __init__(self, com, skip_validation = False) -> None:
        if not skip_validation:
            ParameterHandler(com).validate("P0.3030101.0.0", 111)
        super().__init__(Telegram111(), com)

    def fault_string(self) -> str:
        """Returns string containing fault reason

        Returns:
            str: String containing the fault reason
        """
        return self.await_fault_code()

    def configure_hardware_limit_switch(self, active: bool):
        """Configures the hardware limit switch

        Parameters:
            active (bool): True => activate limit, False => deactivate limit
        """
        self.telegram.pos_stw2.activate_hardware_limit_switch = active

    def configure_software_limit_switch(self, active: bool):
        """Configures the software limit switch

        Parameters:
            active (bool): True => activate limit, False => deactivate limit
        """
        self.telegram.pos_stw2.activate_software_limit_switch = active

    def configure_measuring_probe(self, falling_edge: bool = False, measuring_probe: str = 'first'):
        """
        Configures the measuring probes.
        Be aware that only one probe is configurable simultaneously.
        In order to configure both probes:
            1. Configure probe 'first'
            2. Send using update_outputs()
            3. Configure probe 'second'

        Parameters:
            falling_edge (bool): Determines whether to trigger on rising or falling edge
            measuring_probe (str): One of ['first', 'second'], determines the probe to configure
        """
        assert measuring_probe in ['first', 'second']
        self.telegram.pos_stw2.falling_edge_of_measuring_probe = falling_edge
        self.telegram.pos_stw2.measuring_probe2_is_activated = measuring_probe == 'second'

    def configure_continuous_update(self, active: bool):
        """
        Configures the continuous update option i.e. setpoints are immediately updated without need
        of starting a new traversing task

        Parameters:
            active (bool): True => activate continuous update, False => deactivate continuous update
        """
        self.telegram.pos_stw1.continuous_update = active

    def configure_tracking_mode(self, active: bool):
        """Configures the tracking mode i.e. setpoint continuously tracks the current value

        Parameters:
            active (bool): True => activate tracking mode, False => deactivate tracking mode
        """
        self.telegram.pos_stw2.activate_tracking_mode = active

    def _prepare_stop_motion_task_bits(self):
        """Prepares the telegram bits for stopping the current motion"""
        super()._prepare_stop_motion_task_bits()
        # Reset referencing bits (in case referencing motion was performed)
        self.telegram.pos_stw2.set_reference_point = False

    def _prepare_position_task_bits(self, position: int, velocity: int, absolute: bool = False):
        """Prepares the telegram bits for positioning task"""
        super()._prepare_position_task_bits(position, velocity, absolute)
        self.telegram.pos_stw1.activate_mdi = True
        self.telegram.pos_stw1.absolute_position = absolute

    def _prepare_jog_task_bits(self, jog_positive: bool = True, jog_negative: bool = False,
                               incremental: bool = False):
        """Prepares the telegram bits for jog task task"""
        super()._prepare_jog_task_bits(jog_positive, jog_negative, incremental)
        self.telegram.pos_stw2.incremental_jogging = incremental

    def fix_stop_reached(self):
        """Gives information if drive has reached fix stop

        Returns:
            bool: True if drive is at fix stop, False otherwise
        """
        self.update_inputs()
        return self.telegram.pos_zsw2.fixed_stop_reached

    def clamping_torque_reached(self):
        """Gives information if drive has reached clamping torque

        Returns:
            bool: True if drive torque reached the clamping torque, False otherwise
        """
        self.update_inputs()
        return self.telegram.pos_zsw2.fixed_stop_clamping_torque_reached

    def current_position(self):
        """Read the current position

        Returns:
            int: Current position in user units
        """
        self.update_inputs()
        return self.telegram.xist_a.value

    def current_fault_code(self) -> int:
        """Read the current fault code position

        Returns:
            int: Current fault code
        """
        self.update_inputs()
        return int(self.telegram.fault_code)

    def await_fault_code(self, timeout=0.5):
        """Waits for fault code to be available and produces log afterwards.

        Returns:
            bool: True if succesful, False otherwise
        """
        fault_code = 0
        start_time = time.time()
        while not fault_code:
            fault_code = self.current_fault_code()
            time.sleep(0.01)
            if time.time() - start_time > timeout:
                return f"Fault reason could not be determined within {timeout} s"

        fault_desc = f"Cancelled due to fault: {diagnosis_name(fault_code)} ({fault_code})"
        for i, remedy in enumerate(diagnosis_remedy(fault_code)):
            fault_desc += f"\nPossible remedy {str(i+1)}: {remedy}"
        return fault_desc

    def wait_for_referencing_task_ack(self) -> bool:
        """Waits for drive to be referenced

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Wait for referencing task to be acknowledged")

        def cond():
            self.update_inputs()
            return self.telegram.pos_zsw1.homing_active
        if not wait_until(cond, self.fault_present,
                          info_string=self.position_info_string,
                          error_string=self.fault_string):
            return False

        Logging.logger.info("=> Referencing task acknowledged")
        return True

    def set_current_position_task(self, nonblocking: bool = False) -> bool:
        """Perform the referencing sequence. If successful, the drive is referenced afterwards.

        Parameters:
            nonblocking (bool): If True, tasks returns immediately after starting the task.
                                Otherwise function awaits for finish (or fault).
        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Start homing task using current position")
        self.telegram.pos_stw2.set_reference_point = True
        self.update_outputs()

        if nonblocking:
            return True

        return self.wait_for_referencing_execution()

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

        self.telegram.mdi_velocity.value = abs(velocity)
        self.telegram.pos_stw1.activate_mdi = True
        self.telegram.pos_stw1.absolute_position = True
        self.telegram.pos_stw1.activate_setup = True
        self.telegram.pos_stw1.positioning_direction0 = velocity > 0
        self.telegram.pos_stw1.positioning_direction1 = velocity < 0
        self.telegram.stw1.activate_traversing_task = True
        self.update_outputs()

        if duration == 0:
            return True

        if not self.wait_for_traversing_task_ack():
            return False

        # Wait for predefined amount of time
        if not wait_for(duration, self.fault_present,
                        self.velocity_info_string, self.fault_string):
            return False

        self.stop_motion_task()
        Logging.logger.info("=> Finished velocity task (using unlimited positioning)")
        return True

    def record_task(self, record_number: int, nonblocking: bool = True) -> bool:
        """Perform a preconfigured record task by providing the corresponding record number

        Parameters:
            record_number (int): The record number determining the record table entry that should be
                                 executed.
            nonblocking (bool): If True, tasks returns immediately after starting the task.
                                Otherwise function awaits for finish (or fault).

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.ready_for_motion():
            Logging.logger.error("Record task aborted")
            return False
        Logging.logger.info("Start record task")

        self.telegram.pos_stw1.record_table_selection0 = record_number & 1 > 0
        self.telegram.pos_stw1.record_table_selection1 = record_number & 2 > 0
        self.telegram.pos_stw1.record_table_selection2 = record_number & 4 > 0
        self.telegram.pos_stw1.record_table_selection3 = record_number & 8 > 0
        self.telegram.pos_stw1.record_table_selection4 = record_number & 16 > 0
        self.telegram.pos_stw1.record_table_selection5 = record_number & 32 > 0
        self.telegram.pos_stw1.record_table_selection6 = record_number & 64 > 0
        self.telegram.stw1.activate_traversing_task = True
        self.update_outputs()

        if nonblocking:
            return True

        return self.wait_for_position_motion_execution()
