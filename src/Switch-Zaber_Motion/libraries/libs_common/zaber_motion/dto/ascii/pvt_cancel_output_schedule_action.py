# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .io_port_type import IoPortType


@dataclass
class PvtCancelOutputScheduleAction:
    """
    Cancel the pending scheduled output change for a single analog or digital output pin in a PVT sequence or buffer.
    """

    channel: int
    """
    The 1-based number of the output pin whose pending scheduled change to cancel.
    """

    io_type: IoPortType
    """
    The type of the output pin to cancel. Must be AO or DO; input types are not valid here.
    """

    @staticmethod
    def zero_values() -> 'PvtCancelOutputScheduleAction':
        return PvtCancelOutputScheduleAction(
            channel=0,
            io_type=next(first for first in IoPortType),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtCancelOutputScheduleAction':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtCancelOutputScheduleAction.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'channel': int(self.channel),
            'ioType': self.io_type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtCancelOutputScheduleAction':
        return PvtCancelOutputScheduleAction(
            channel=data.get('channel'),  # type: ignore
            io_type=IoPortType(data.get('ioType')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.channel is None:
            raise ValueError(f'Property "Channel" of "PvtCancelOutputScheduleAction" is None.')

        if not isinstance(self.channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Channel" of "PvtCancelOutputScheduleAction" is not a number.')

        if int(self.channel) != self.channel:
            raise ValueError(f'Property "Channel" of "PvtCancelOutputScheduleAction" is not integer value.')

        if self.io_type is None:
            raise ValueError(f'Property "IoType" of "PvtCancelOutputScheduleAction" is None.')

        if not isinstance(self.io_type, IoPortType):
            raise ValueError(f'Property "IoType" of "PvtCancelOutputScheduleAction" is not an instance of "IoPortType".')
