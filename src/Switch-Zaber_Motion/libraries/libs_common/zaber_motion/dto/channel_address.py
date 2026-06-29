# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class ChannelAddress:
    """
    Holds device address and IO channel number.
    """

    device: int
    """
    Device address.
    """

    channel: int
    """
    IO channel number.
    """

    @staticmethod
    def zero_values() -> 'ChannelAddress':
        return ChannelAddress(
            device=0,
            channel=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ChannelAddress':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ChannelAddress.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'device': int(self.device),
            'channel': int(self.channel),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ChannelAddress':
        return ChannelAddress(
            device=data.get('device'),  # type: ignore
            channel=data.get('channel'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device is None:
            raise ValueError(f'Property "Device" of "ChannelAddress" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "ChannelAddress" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "ChannelAddress" is not integer value.')

        if self.channel is None:
            raise ValueError(f'Property "Channel" of "ChannelAddress" is None.')

        if not isinstance(self.channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Channel" of "ChannelAddress" is not a number.')

        if int(self.channel) != self.channel:
            raise ValueError(f'Property "Channel" of "ChannelAddress" is not integer value.')
