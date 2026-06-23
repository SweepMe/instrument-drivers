
"""
Contains ParameterSet class which is used to represent parameter sets of EDrives.
"""
from edcon.utils.logging import Logging
from edcon.edrive.com_base import ComBase
from edcon.edrive.parameter_mapping import ParameterMap

class ParameterHandler:
    """Class for parameter handling activities."""
    # pylint: disable=too-few-public-methods
    # ParameterHandler will be expanded soon.

    def __init__(self, com: ComBase):
        self.com = com
        self.parameter_map = ParameterMap()

    def validate(self, parameter_uid: str, value) -> bool:
        """Asserts that the provided pnu is actually configured"""
        pnu = int(self.parameter_map[parameter_uid].pnu)
        pnu_name = self.parameter_map[parameter_uid].name
        pnu_data_type = self.parameter_map[parameter_uid].data_type
        Logging.logger.info(f"Try to validate PNU {pnu} ({pnu_name}) of type {pnu_data_type}")

        configured_value = self.com.read_pnu(pnu)
        if not configured_value:
            Logging.logger.error(f"Could not validate PNU {pnu} ({pnu_name})")
            return False

        assert configured_value == value, \
            f"Incorrect value configured on {pnu} ({pnu_name}) -> " \
            f"Expected: {value}, Actual: {configured_value}"
        Logging.logger.info(f"Correct value configured on {pnu} ({pnu_name}): {configured_value}")
        return True
