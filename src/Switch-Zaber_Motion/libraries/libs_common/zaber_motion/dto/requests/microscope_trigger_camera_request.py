# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class MicroscopeTriggerCameraRequest:

    interface_id: int = 0

    device: int = 0

    channel_number: int = 0

    delay: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    wait: bool = False

    @staticmethod
    def zero_values() -> 'MicroscopeTriggerCameraRequest':
        return MicroscopeTriggerCameraRequest(
            interface_id=0,
            device=0,
            channel_number=0,
            delay=0,
            unit=Units.NATIVE,
            wait=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MicroscopeTriggerCameraRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MicroscopeTriggerCameraRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'channelNumber': int(self.channel_number),
            'delay': float(self.delay),
            'unit': units_from_literals(self.unit).value,
            'wait': bool(self.wait),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MicroscopeTriggerCameraRequest':
        return MicroscopeTriggerCameraRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            channel_number=data.get('channelNumber'),  # type: ignore
            delay=data.get('delay'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            wait=data.get('wait'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeTriggerCameraRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "MicroscopeTriggerCameraRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeTriggerCameraRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "MicroscopeTriggerCameraRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "MicroscopeTriggerCameraRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "MicroscopeTriggerCameraRequest" is not integer value.')

        if self.channel_number is None:
            raise ValueError(f'Property "ChannelNumber" of "MicroscopeTriggerCameraRequest" is None.')

        if not isinstance(self.channel_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ChannelNumber" of "MicroscopeTriggerCameraRequest" is not a number.')

        if int(self.channel_number) != self.channel_number:
            raise ValueError(f'Property "ChannelNumber" of "MicroscopeTriggerCameraRequest" is not integer value.')

        if self.delay is None:
            raise ValueError(f'Property "Delay" of "MicroscopeTriggerCameraRequest" is None.')

        if not isinstance(self.delay, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Delay" of "MicroscopeTriggerCameraRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "MicroscopeTriggerCameraRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "MicroscopeTriggerCameraRequest" is not Units.')
