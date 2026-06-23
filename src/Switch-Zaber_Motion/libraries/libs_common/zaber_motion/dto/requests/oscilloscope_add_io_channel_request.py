# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.io_port_type import IoPortType


@dataclass
class OscilloscopeAddIoChannelRequest:

    interface_id: int = 0

    device: int = 0

    io_type: IoPortType = next(first for first in IoPortType)

    io_channel: int = 0

    @staticmethod
    def zero_values() -> 'OscilloscopeAddIoChannelRequest':
        return OscilloscopeAddIoChannelRequest(
            interface_id=0,
            device=0,
            io_type=next(first for first in IoPortType),
            io_channel=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeAddIoChannelRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeAddIoChannelRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'ioType': self.io_type.value,
            'ioChannel': int(self.io_channel),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeAddIoChannelRequest':
        return OscilloscopeAddIoChannelRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            io_type=IoPortType(data.get('ioType')),  # type: ignore
            io_channel=data.get('ioChannel'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeAddIoChannelRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeAddIoChannelRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeAddIoChannelRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "OscilloscopeAddIoChannelRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "OscilloscopeAddIoChannelRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "OscilloscopeAddIoChannelRequest" is not integer value.')

        if self.io_type is None:
            raise ValueError(f'Property "IoType" of "OscilloscopeAddIoChannelRequest" is None.')

        if not isinstance(self.io_type, IoPortType):
            raise ValueError(f'Property "IoType" of "OscilloscopeAddIoChannelRequest" is not an instance of "IoPortType".')

        if self.io_channel is None:
            raise ValueError(f'Property "IoChannel" of "OscilloscopeAddIoChannelRequest" is None.')

        if not isinstance(self.io_channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "IoChannel" of "OscilloscopeAddIoChannelRequest" is not a number.')

        if int(self.io_channel) != self.io_channel:
            raise ValueError(f'Property "IoChannel" of "OscilloscopeAddIoChannelRequest" is not integer value.')
