# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DeviceSetAnalogOutputScheduleRequest:

    interface_id: int = 0

    device: int = 0

    channel_number: int = 0

    value: float = 0

    future_value: float = 0

    delay: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'DeviceSetAnalogOutputScheduleRequest':
        return DeviceSetAnalogOutputScheduleRequest(
            interface_id=0,
            device=0,
            channel_number=0,
            value=0,
            future_value=0,
            delay=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetAnalogOutputScheduleRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetAnalogOutputScheduleRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'channelNumber': int(self.channel_number),
            'value': float(self.value),
            'futureValue': float(self.future_value),
            'delay': float(self.delay),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetAnalogOutputScheduleRequest':
        return DeviceSetAnalogOutputScheduleRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            channel_number=data.get('channelNumber'),  # type: ignore
            value=data.get('value'),  # type: ignore
            future_value=data.get('futureValue'),  # type: ignore
            delay=data.get('delay'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAnalogOutputScheduleRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetAnalogOutputScheduleRequest" is not integer value.')

        if self.channel_number is None:
            raise ValueError(f'Property "ChannelNumber" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.channel_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ChannelNumber" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if int(self.channel_number) != self.channel_number:
            raise ValueError(f'Property "ChannelNumber" of "DeviceSetAnalogOutputScheduleRequest" is not integer value.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if self.future_value is None:
            raise ValueError(f'Property "FutureValue" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.future_value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FutureValue" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if self.delay is None:
            raise ValueError(f'Property "Delay" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.delay, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Delay" of "DeviceSetAnalogOutputScheduleRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "DeviceSetAnalogOutputScheduleRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "DeviceSetAnalogOutputScheduleRequest" is not Units.')
