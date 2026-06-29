# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class DeviceIOInfo:
    """
    Class representing information on the I/O channels of the device.
    """

    number_analog_outputs: int
    """
    Number of analog output channels.
    """

    number_analog_inputs: int
    """
    Number of analog input channels.
    """

    number_digital_outputs: int
    """
    Number of digital output channels.
    """

    number_digital_inputs: int
    """
    Number of digital input channels.
    """

    @staticmethod
    def zero_values() -> 'DeviceIOInfo':
        return DeviceIOInfo(
            number_analog_outputs=0,
            number_analog_inputs=0,
            number_digital_outputs=0,
            number_digital_inputs=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceIOInfo':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceIOInfo.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'numberAnalogOutputs': int(self.number_analog_outputs),
            'numberAnalogInputs': int(self.number_analog_inputs),
            'numberDigitalOutputs': int(self.number_digital_outputs),
            'numberDigitalInputs': int(self.number_digital_inputs),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceIOInfo':
        return DeviceIOInfo(
            number_analog_outputs=data.get('numberAnalogOutputs'),  # type: ignore
            number_analog_inputs=data.get('numberAnalogInputs'),  # type: ignore
            number_digital_outputs=data.get('numberDigitalOutputs'),  # type: ignore
            number_digital_inputs=data.get('numberDigitalInputs'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.number_analog_outputs is None:
            raise ValueError(f'Property "NumberAnalogOutputs" of "DeviceIOInfo" is None.')

        if not isinstance(self.number_analog_outputs, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "NumberAnalogOutputs" of "DeviceIOInfo" is not a number.')

        if int(self.number_analog_outputs) != self.number_analog_outputs:
            raise ValueError(f'Property "NumberAnalogOutputs" of "DeviceIOInfo" is not integer value.')

        if self.number_analog_inputs is None:
            raise ValueError(f'Property "NumberAnalogInputs" of "DeviceIOInfo" is None.')

        if not isinstance(self.number_analog_inputs, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "NumberAnalogInputs" of "DeviceIOInfo" is not a number.')

        if int(self.number_analog_inputs) != self.number_analog_inputs:
            raise ValueError(f'Property "NumberAnalogInputs" of "DeviceIOInfo" is not integer value.')

        if self.number_digital_outputs is None:
            raise ValueError(f'Property "NumberDigitalOutputs" of "DeviceIOInfo" is None.')

        if not isinstance(self.number_digital_outputs, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "NumberDigitalOutputs" of "DeviceIOInfo" is not a number.')

        if int(self.number_digital_outputs) != self.number_digital_outputs:
            raise ValueError(f'Property "NumberDigitalOutputs" of "DeviceIOInfo" is not integer value.')

        if self.number_digital_inputs is None:
            raise ValueError(f'Property "NumberDigitalInputs" of "DeviceIOInfo" is None.')

        if not isinstance(self.number_digital_inputs, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "NumberDigitalInputs" of "DeviceIOInfo" is not a number.')

        if int(self.number_digital_inputs) != self.number_digital_inputs:
            raise ValueError(f'Property "NumberDigitalInputs" of "DeviceIOInfo" is not integer value.')
