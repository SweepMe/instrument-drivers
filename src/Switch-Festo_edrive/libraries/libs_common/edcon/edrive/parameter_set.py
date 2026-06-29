
"""
Contains ParameterSet class which is used to represent parameter sets of EDrives.
"""
from dataclasses import dataclass
from edcon.edrive.parameter_mapping import ParameterMap
from edcon.utils.logging import Logging


@dataclass
class Parameter:
    """Class representing a parameter."""
    axis: int
    data_id: int
    instance: int
    subindex: int
    value: bytes

    @classmethod
    def from_uid(cls, uid_id: str, value: bytes):
        """Function to create a Parameter by providing a uid and value.

        Parameters:
            uid_id (str): uid of the parameter
            value (bytes): value of the parameter

        Returns:
            Parameter object
        """
        axis, data_id, instance, subindex = uid_id.strip('P').split('.')
        return cls(int(axis), int(data_id), int(instance), int(subindex), value)

    def uid(self) -> str:
        """Returns the uid of the parameter.

        Returns:
            str: uid
        """
        return f'{self.axis}.{self.data_id}.{self.instance}.{self.subindex}'

    def is_null_terminator(self):
        """Determines if the parameter is a null terminator.

        Returns:
            bool: True if the parameter is a null terminator
        """
        parameter_map = ParameterMap()
        if not self.uid() in parameter_map:
            return None

        data_type = parameter_map[self.uid()].data_type
        if 'STRING' in data_type:
            last_index = int(data_type.strip('STRING()')) - 1
            if self.subindex == last_index:
                Logging.logger.debug(
                    f'Parameter {self.uid()}.{self.subindex} is a null terminator')
                return True
        return False


class ParameterSet:
    """Class representing a parameter set."""

    def __init__(self, parameterset_file, strip_null_terminators=True) -> None:
        self.parameters = []
        with open(parameterset_file, 'rb') as pfile:
            lines = pfile.readlines()

        start_idx = lines.index(b'----\r\n') + 1
        end_idx = start_idx + lines[start_idx:].index(b'----\r\n')

        for item in lines[start_idx:end_idx]:
            key, hex_value = item.decode().strip('P').split(';')
            value = bytes.fromhex(hex_value.split('x')[1])[::-1]

            self.parameters.append(Parameter.from_uid(key, value))

        if strip_null_terminators:
            Logging.logger.info('Stripping null terminators from parameter set')
            self.strip_null_terminators()

    def __iter__(self):
        return iter(self.parameters)

    def __len__(self):
        return len(self.parameters)

    def strip_null_terminators(self):
        """Removes all parameters from the parameter set that represent null terminators."""
        self.parameters = filter(
            lambda v: not v.is_null_terminator(), self.parameters)
