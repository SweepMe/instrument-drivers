"""Class definition containing generic telegram execution functions."""

import traceback
from edcon.utils.logging import Logging
from edcon.utils.func_helpers import func_sequence, wait_until


class TelegramHandler:
    """Basic class for executing telegrams."""

    def __init__(self, telegram, com) -> None:
        self.telegram = telegram

        # Configure generic values of the telegram
        self.telegram.stw1.control_by_plc = True
        self.telegram.stw1.no_coast_stop = True
        self.telegram.stw1.no_quick_stop = True
        self.telegram.stw1.enable_operation = True

        self.com = com
        # Start process data
        self.com.start_io()

    def __del__(self):
        self.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trc_bck):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, trc_bck)
        self.shutdown()

    def shutdown(self):
        """Tries to disable the powerstage and stops the communication thread """
        if hasattr(self, 'telegram') and hasattr(self, 'com'):
            self.telegram.stw1.enable_operation = False
            self.com.send_io(self.telegram.output_bytes())
            self.com.shutdown()

    def update_inputs(self):
        """Reads current input process data and updates telegram"""
        self.telegram.input_bytes(self.com.recv_io())

    def update_outputs(self):
        """Writes current telegram value to output process data
        """
        self.com.send_io(self.telegram.output_bytes())

    def update_io(self):
        """Updates process data in both directions (I/O)"""
        self.update_inputs()
        self.update_outputs()

    def fault_string(self) -> str:
        """Returns string containing fault reason

        Returns:
            str: String containing the fault reason
        """
        return "Unknown fault"

    def fault_present(self) -> bool:
        """Gives information whether a fault is present

        Returns:
            bool: True if fault presens, False otherwise
        """
        self.update_inputs()
        if self.telegram.zsw1.fault_present:
            Logging.logger.error("Fault bit is present")
            return True
        return False

    def plc_control_granted(self) -> bool:
        """Gives information if PLC control is granted

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Check if PLC control is granted")

        self.update_inputs()
        if not self.telegram.zsw1.control_requested:
            Logging.logger.info("=> PLC control denied")
            return False
        Logging.logger.info("=> PLC control granted")
        return True

    def ready_for_motion(self):
        """Gives information if motion tasks can be started

        Returns:
            bool: True if drive is ready for motion tasks, False otherwise
        """
        if not self.plc_control_granted():
            return False
        Logging.logger.info("Check if drive is ready for motion")
        self.update_inputs()
        if not self.telegram.zsw1.operation_enabled:
            Logging.logger.info("=> Drive not ready for motion")
            return False
        Logging.logger.info("=> Drive is ready for motion")
        return True

    def configure_coast_stop(self, active: bool):
        """Configures the coast stop option

        Parameters:
            active (bool): True => activate coasting, False => deactivate coasting
        """
        self.telegram.stw1.no_coast_stop = not active

    def configure_quick_stop(self, active: bool):
        """Configures the quick stop option

        Parameters:
            active (bool): True => activate quick stop, False => deactivate quick stop
        """
        self.telegram.stw1.no_quick_stop = not active

    def configure_brake(self, active: bool):
        """Configures the holding brake

        Parameters:
            active (bool): True => activate brake, False => release brake
        """
        self.telegram.stw1.open_holding_brake = not active

    def acknowledge_faults(self, timeout: float = 5.0) -> bool:
        """Send telegram to acknowledge present faults of the EDrive

        Parameter:
            timeout (float): time that should be waited for acknowledgement

        Returns:
            bool: True if succesful, False otherwise
        """
        Logging.logger.info("Acknowledge any present faults")

        def toggle_func(value):
            self.telegram.stw1.fault_ack = value
            self.update_outputs()

        func_sequence(toggle_func, [True, False])

        def cond():
            self.update_inputs()
            return not self.telegram.zsw1.fault_present

        if not wait_until(cond, timeout=timeout, error_string=self.fault_string):
            return False

        Logging.logger.info("=> No fault present")
        return True

    def enable_powerstage(self, timeout: float = 5.0) -> bool:
        """Send telegram to enable the power stage

        Parameter:
            timeout (float): time that should be waited for enabling

        Returns:
            bool: True if succesful, False otherwise
        """
        if not self.plc_control_granted():
            Logging.logger.error("Enabling powerstage is not possible")
            return False
        Logging.logger.info("Enable powerstage")

        # Toggle to low (in case it is already True)
        def toggle_func(value):
            self.telegram.stw1.on = value
            self.update_outputs()

        func_sequence(toggle_func, [False, True])

        def cond():
            self.update_inputs()
            return self.telegram.zsw1.operation_enabled

        if not wait_until(cond, self.fault_present, timeout,
                          error_string=self.fault_string):
            Logging.logger.error("Operation inhibited")
            return False

        Logging.logger.info("=> Powerstage enabled")
        return True

    def disable_powerstage(self, timeout: float = 5.0) -> bool:
        """Send telegram to disable the power stage"""
        Logging.logger.info("Disable powerstage")
        self.telegram.stw1.on = False
        self.update_outputs()

        def cond():
            self.update_inputs()
            return not self.telegram.zsw1.operation_enabled

        if not wait_until(cond, self.fault_present, timeout,
                          error_string=self.fault_string):
            Logging.logger.error("Operation inhibited")
            return False

        Logging.logger.info("=> Powerstage disabled")
        return True
