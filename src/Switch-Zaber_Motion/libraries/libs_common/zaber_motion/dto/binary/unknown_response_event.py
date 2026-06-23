# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class UnknownResponseEvent:
    """
    Reply that could not be matched to a request.
    """

    device_address: int
    """
    Number of the device that sent or should receive the message.
    """

    command: int
    """
    The warning flag contains the highest priority warning currently active for the device or axis.
    """

    data: int
    """
    Data payload of the message, if applicable, or zero otherwise.
    """

    @staticmethod
    def zero_values() -> 'UnknownResponseEvent':
        return UnknownResponseEvent(
            device_address=0,
            command=0,
            data=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnknownResponseEvent':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnknownResponseEvent.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceAddress': int(self.device_address),
            'command': int(self.command),
            'data': int(self.data),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnknownResponseEvent':
        return UnknownResponseEvent(
            device_address=data.get('deviceAddress'),  # type: ignore
            command=data.get('command'),  # type: ignore
            data=data.get('data'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_address is None:
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is None.')

        if not isinstance(self.device_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is not a number.')

        if int(self.device_address) != self.device_address:
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is not integer value.')

        if self.command is None:
            raise ValueError(f'Property "Command" of "UnknownResponseEvent" is None.')

        if not isinstance(self.command, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Command" of "UnknownResponseEvent" is not a number.')

        if int(self.command) != self.command:
            raise ValueError(f'Property "Command" of "UnknownResponseEvent" is not integer value.')

        if self.data is None:
            raise ValueError(f'Property "Data" of "UnknownResponseEvent" is None.')

        if not isinstance(self.data, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Data" of "UnknownResponseEvent" is not a number.')

        if int(self.data) != self.data:
            raise ValueError(f'Property "Data" of "UnknownResponseEvent" is not integer value.')
