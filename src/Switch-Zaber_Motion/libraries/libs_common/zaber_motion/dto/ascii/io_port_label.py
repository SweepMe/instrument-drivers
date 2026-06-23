# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .io_port_type import IoPortType


@dataclass
class IoPortLabel:
    """
    The label of an IO port.
    """

    port_type: IoPortType
    """
    The type of the port.
    """

    channel_number: int
    """
    The number of the port.
    """

    label: str
    """
    The label of the port.
    """

    @staticmethod
    def zero_values() -> 'IoPortLabel':
        return IoPortLabel(
            port_type=next(first for first in IoPortType),
            channel_number=0,
            label="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'IoPortLabel':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return IoPortLabel.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'portType': self.port_type.value,
            'channelNumber': int(self.channel_number),
            'label': str(self.label or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'IoPortLabel':
        return IoPortLabel(
            port_type=IoPortType(data.get('portType')),  # type: ignore
            channel_number=data.get('channelNumber'),  # type: ignore
            label=data.get('label'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.port_type is None:
            raise ValueError(f'Property "PortType" of "IoPortLabel" is None.')

        if not isinstance(self.port_type, IoPortType):
            raise ValueError(f'Property "PortType" of "IoPortLabel" is not an instance of "IoPortType".')

        if self.channel_number is None:
            raise ValueError(f'Property "ChannelNumber" of "IoPortLabel" is None.')

        if not isinstance(self.channel_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ChannelNumber" of "IoPortLabel" is not a number.')

        if int(self.channel_number) != self.channel_number:
            raise ValueError(f'Property "ChannelNumber" of "IoPortLabel" is not integer value.')

        if self.label is not None:
            if not isinstance(self.label, str):
                raise ValueError(f'Property "Label" of "IoPortLabel" is not a string.')
