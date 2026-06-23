# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.pvt_buffer_axis_units import PvtBufferAxisUnits
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class PvtBufferGetSequenceDataRequest:

    interface_id: int = 0

    device: int = 0

    buffer_number: int = 0

    time_units: UnitsAndLiterals = Units.NATIVE

    axes: Optional[List[PvtBufferAxisUnits]] = None

    @staticmethod
    def zero_values() -> 'PvtBufferGetSequenceDataRequest':
        return PvtBufferGetSequenceDataRequest(
            interface_id=0,
            device=0,
            buffer_number=0,
            axes=None,
            time_units=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtBufferGetSequenceDataRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtBufferGetSequenceDataRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'bufferNumber': int(self.buffer_number),
            'axes': [item.to_dict() for item in self.axes] if self.axes is not None else [],
            'timeUnits': units_from_literals(self.time_units).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtBufferGetSequenceDataRequest':
        return PvtBufferGetSequenceDataRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            buffer_number=data.get('bufferNumber'),  # type: ignore
            axes=[PvtBufferAxisUnits.from_dict(item) for item in data.get('axes')] if data.get('axes') is not None else None,  # type: ignore
            time_units=Units(data.get('timeUnits')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "PvtBufferGetSequenceDataRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "PvtBufferGetSequenceDataRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "PvtBufferGetSequenceDataRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "PvtBufferGetSequenceDataRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "PvtBufferGetSequenceDataRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "PvtBufferGetSequenceDataRequest" is not integer value.')

        if self.buffer_number is None:
            raise ValueError(f'Property "BufferNumber" of "PvtBufferGetSequenceDataRequest" is None.')

        if not isinstance(self.buffer_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "BufferNumber" of "PvtBufferGetSequenceDataRequest" is not a number.')

        if int(self.buffer_number) != self.buffer_number:
            raise ValueError(f'Property "BufferNumber" of "PvtBufferGetSequenceDataRequest" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "PvtBufferGetSequenceDataRequest" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "PvtBufferGetSequenceDataRequest" is None.')

                if not isinstance(axes_item, PvtBufferAxisUnits):
                    raise ValueError(f'Item {i} in property "Axes" of "PvtBufferGetSequenceDataRequest" is not an instance of "PvtBufferAxisUnits".')

                axes_item.validate()

        if self.time_units is None:
            raise ValueError(f'Property "TimeUnits" of "PvtBufferGetSequenceDataRequest" is None.')

        if not isinstance(self.time_units, (Units, str)):
            raise ValueError(f'Property "TimeUnits" of "PvtBufferGetSequenceDataRequest" is not Units.')
