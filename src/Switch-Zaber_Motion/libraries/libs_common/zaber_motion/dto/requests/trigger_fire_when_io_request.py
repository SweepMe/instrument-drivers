# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.io_port_type import IoPortType
from ..ascii.trigger_condition import TriggerCondition


@dataclass
class TriggerFireWhenIoRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    port_type: IoPortType = next(first for first in IoPortType)

    channel: int = 0

    trigger_condition: TriggerCondition = next(first for first in TriggerCondition)

    value: float = 0

    @staticmethod
    def zero_values() -> 'TriggerFireWhenIoRequest':
        return TriggerFireWhenIoRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            port_type=next(first for first in IoPortType),
            channel=0,
            trigger_condition=next(first for first in TriggerCondition),
            value=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerFireWhenIoRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerFireWhenIoRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'triggerNumber': int(self.trigger_number),
            'portType': self.port_type.value,
            'channel': int(self.channel),
            'triggerCondition': self.trigger_condition.value,
            'value': float(self.value),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerFireWhenIoRequest':
        return TriggerFireWhenIoRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            port_type=IoPortType(data.get('portType')),  # type: ignore
            channel=data.get('channel'),  # type: ignore
            trigger_condition=TriggerCondition(data.get('triggerCondition')),  # type: ignore
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerFireWhenIoRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerFireWhenIoRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerFireWhenIoRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerFireWhenIoRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireWhenIoRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireWhenIoRequest" is not integer value.')

        if self.port_type is None:
            raise ValueError(f'Property "PortType" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.port_type, IoPortType):
            raise ValueError(f'Property "PortType" of "TriggerFireWhenIoRequest" is not an instance of "IoPortType".')

        if self.channel is None:
            raise ValueError(f'Property "Channel" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Channel" of "TriggerFireWhenIoRequest" is not a number.')

        if int(self.channel) != self.channel:
            raise ValueError(f'Property "Channel" of "TriggerFireWhenIoRequest" is not integer value.')

        if self.trigger_condition is None:
            raise ValueError(f'Property "TriggerCondition" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.trigger_condition, TriggerCondition):
            raise ValueError(f'Property "TriggerCondition" of "TriggerFireWhenIoRequest" is not an instance of "TriggerCondition".')

        if self.value is None:
            raise ValueError(f'Property "Value" of "TriggerFireWhenIoRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "TriggerFireWhenIoRequest" is not a number.')
