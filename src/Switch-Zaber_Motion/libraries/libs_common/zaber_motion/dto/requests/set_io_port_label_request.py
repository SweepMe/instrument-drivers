# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..ascii.io_port_type import IoPortType


@dataclass
class SetIoPortLabelRequest:

    interface_id: int = 0

    device: int = 0

    port_type: IoPortType = next(first for first in IoPortType)

    channel_number: int = 0

    label: Optional[str] = None

    @staticmethod
    def zero_values() -> 'SetIoPortLabelRequest':
        return SetIoPortLabelRequest(
            interface_id=0,
            device=0,
            port_type=next(first for first in IoPortType),
            channel_number=0,
            label=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetIoPortLabelRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetIoPortLabelRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'portType': self.port_type.value,
            'channelNumber': int(self.channel_number),
            'label': str(self.label) if self.label is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetIoPortLabelRequest':
        return SetIoPortLabelRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            port_type=IoPortType(data.get('portType')),  # type: ignore
            channel_number=data.get('channelNumber'),  # type: ignore
            label=data.get('label'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "SetIoPortLabelRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "SetIoPortLabelRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "SetIoPortLabelRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "SetIoPortLabelRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "SetIoPortLabelRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "SetIoPortLabelRequest" is not integer value.')

        if self.port_type is None:
            raise ValueError(f'Property "PortType" of "SetIoPortLabelRequest" is None.')

        if not isinstance(self.port_type, IoPortType):
            raise ValueError(f'Property "PortType" of "SetIoPortLabelRequest" is not an instance of "IoPortType".')

        if self.channel_number is None:
            raise ValueError(f'Property "ChannelNumber" of "SetIoPortLabelRequest" is None.')

        if not isinstance(self.channel_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ChannelNumber" of "SetIoPortLabelRequest" is not a number.')

        if int(self.channel_number) != self.channel_number:
            raise ValueError(f'Property "ChannelNumber" of "SetIoPortLabelRequest" is not integer value.')

        if self.label is not None:
            if not isinstance(self.label, str):
                raise ValueError(f'Property "Label" of "SetIoPortLabelRequest" is not a string.')
