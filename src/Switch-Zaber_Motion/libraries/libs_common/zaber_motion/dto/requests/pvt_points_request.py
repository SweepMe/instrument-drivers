# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .stream_segment_type import StreamSegmentType
from ..ascii.measurement_sequence import MeasurementSequence


@dataclass
class PvtPointsRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    type: StreamSegmentType = next(first for first in StreamSegmentType)

    positions: List[MeasurementSequence] = field(default_factory=list)

    velocities: List[MeasurementSequence] = field(default_factory=list)

    times: MeasurementSequence = field(default_factory=MeasurementSequence.zero_values)

    @staticmethod
    def zero_values() -> 'PvtPointsRequest':
        return PvtPointsRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            type=next(first for first in StreamSegmentType),
            positions=[],
            velocities=[],
            times=MeasurementSequence.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPointsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPointsRequest.from_dict(data)

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
            'type': self.type.value,
            'positions': [item.to_dict() for item in self.positions] if self.positions is not None else [],
            'velocities': [item.to_dict() for item in self.velocities] if self.velocities is not None else [],
            'times': self.times.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPointsRequest':
        return PvtPointsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            type=StreamSegmentType(data.get('type')),  # type: ignore
            positions=[MeasurementSequence.from_dict(item) for item in data.get('positions')],  # type: ignore
            velocities=[MeasurementSequence.from_dict(item) for item in data.get('velocities')],  # type: ignore
            times=MeasurementSequence.from_dict(data.get('times')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "PvtPointsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "PvtPointsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "PvtPointsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "PvtPointsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "PvtPointsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "PvtPointsRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "PvtPointsRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "PvtPointsRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "PvtPointsRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "PvtPointsRequest" is None.')

        if not isinstance(self.type, StreamSegmentType):
            raise ValueError(f'Property "Type" of "PvtPointsRequest" is not an instance of "StreamSegmentType".')

        if self.positions is not None:
            if not isinstance(self.positions, Iterable):
                raise ValueError('Property "Positions" of "PvtPointsRequest" is not iterable.')

            for i, positions_item in enumerate(self.positions):
                if positions_item is None:
                    raise ValueError(f'Item {i} in property "Positions" of "PvtPointsRequest" is None.')

                if not isinstance(positions_item, MeasurementSequence):
                    raise ValueError(f'Item {i} in property "Positions" of "PvtPointsRequest" is not an instance of "MeasurementSequence".')

                positions_item.validate()

        if self.velocities is not None:
            if not isinstance(self.velocities, Iterable):
                raise ValueError('Property "Velocities" of "PvtPointsRequest" is not iterable.')

            for i, velocities_item in enumerate(self.velocities):
                if velocities_item is None:
                    raise ValueError(f'Item {i} in property "Velocities" of "PvtPointsRequest" is None.')

                if not isinstance(velocities_item, MeasurementSequence):
                    raise ValueError(f'Item {i} in property "Velocities" of "PvtPointsRequest" is not an instance of "MeasurementSequence".')

                velocities_item.validate()

        if self.times is None:
            raise ValueError(f'Property "Times" of "PvtPointsRequest" is None.')

        if not isinstance(self.times, MeasurementSequence):
            raise ValueError(f'Property "Times" of "PvtPointsRequest" is not an instance of "MeasurementSequence".')

        self.times.validate()
