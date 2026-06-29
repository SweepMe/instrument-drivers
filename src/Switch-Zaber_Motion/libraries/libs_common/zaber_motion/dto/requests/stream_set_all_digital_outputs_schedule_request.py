# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.digital_output_action import DigitalOutputAction
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class StreamSetAllDigitalOutputsScheduleRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    values: List[DigitalOutputAction] = field(default_factory=list)

    future_values: List[DigitalOutputAction] = field(default_factory=list)

    delay: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'StreamSetAllDigitalOutputsScheduleRequest':
        return StreamSetAllDigitalOutputsScheduleRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            values=[],
            future_values=[],
            delay=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamSetAllDigitalOutputsScheduleRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamSetAllDigitalOutputsScheduleRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'streamId': int(self.stream_id),
            'pvt': bool(self.pvt),
            'values': [item.value for item in self.values] if self.values is not None else [],
            'futureValues': [item.value for item in self.future_values] if self.future_values is not None else [],
            'delay': float(self.delay),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamSetAllDigitalOutputsScheduleRequest':
        return StreamSetAllDigitalOutputsScheduleRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            values=[DigitalOutputAction(item) for item in data.get('values')],  # type: ignore
            future_values=[DigitalOutputAction(item) for item in data.get('futureValues')],  # type: ignore
            delay=data.get('delay'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamSetAllDigitalOutputsScheduleRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamSetAllDigitalOutputsScheduleRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamSetAllDigitalOutputsScheduleRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamSetAllDigitalOutputsScheduleRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamSetAllDigitalOutputsScheduleRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamSetAllDigitalOutputsScheduleRequest" is not integer value.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "StreamSetAllDigitalOutputsScheduleRequest" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

                if not isinstance(values_item, DigitalOutputAction):
                    raise ValueError(f'Item {i} in property "Values" of "StreamSetAllDigitalOutputsScheduleRequest" is not an instance of "DigitalOutputAction".')

        if self.future_values is not None:
            if not isinstance(self.future_values, Iterable):
                raise ValueError('Property "FutureValues" of "StreamSetAllDigitalOutputsScheduleRequest" is not iterable.')

            for i, future_values_item in enumerate(self.future_values):
                if future_values_item is None:
                    raise ValueError(f'Item {i} in property "FutureValues" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

                if not isinstance(future_values_item, DigitalOutputAction):
                    raise ValueError(f'Item {i} in property "FutureValues" of "StreamSetAllDigitalOutputsScheduleRequest" is not an instance of "DigitalOutputAction".')

        if self.delay is None:
            raise ValueError(f'Property "Delay" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

        if not isinstance(self.delay, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Delay" of "StreamSetAllDigitalOutputsScheduleRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "StreamSetAllDigitalOutputsScheduleRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "StreamSetAllDigitalOutputsScheduleRequest" is not Units.')
