# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DeviceSetAllAnalogOutputsScheduleRequest:

    interface_id: int = 0

    device: int = 0

    values: List[float] = field(default_factory=list)

    future_values: List[float] = field(default_factory=list)

    delay: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'DeviceSetAllAnalogOutputsScheduleRequest':
        return DeviceSetAllAnalogOutputsScheduleRequest(
            interface_id=0,
            device=0,
            values=[],
            future_values=[],
            delay=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetAllAnalogOutputsScheduleRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetAllAnalogOutputsScheduleRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'values': [float(item) for item in self.values] if self.values is not None else [],
            'futureValues': [float(item) for item in self.future_values] if self.future_values is not None else [],
            'delay': float(self.delay),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetAllAnalogOutputsScheduleRequest':
        return DeviceSetAllAnalogOutputsScheduleRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            values=data.get('values'),  # type: ignore
            future_values=data.get('futureValues'),  # type: ignore
            delay=data.get('delay'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllAnalogOutputsScheduleRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllAnalogOutputsScheduleRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetAllAnalogOutputsScheduleRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetAllAnalogOutputsScheduleRequest" is not integer value.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "DeviceSetAllAnalogOutputsScheduleRequest" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

                if not isinstance(values_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Values" of "DeviceSetAllAnalogOutputsScheduleRequest" is not a number.')

        if self.future_values is not None:
            if not isinstance(self.future_values, Iterable):
                raise ValueError('Property "FutureValues" of "DeviceSetAllAnalogOutputsScheduleRequest" is not iterable.')

            for i, future_values_item in enumerate(self.future_values):
                if future_values_item is None:
                    raise ValueError(f'Item {i} in property "FutureValues" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

                if not isinstance(future_values_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "FutureValues" of "DeviceSetAllAnalogOutputsScheduleRequest" is not a number.')

        if self.delay is None:
            raise ValueError(f'Property "Delay" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

        if not isinstance(self.delay, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Delay" of "DeviceSetAllAnalogOutputsScheduleRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "DeviceSetAllAnalogOutputsScheduleRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "DeviceSetAllAnalogOutputsScheduleRequest" is not Units.')
