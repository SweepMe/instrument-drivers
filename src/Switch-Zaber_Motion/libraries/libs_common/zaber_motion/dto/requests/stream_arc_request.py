# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .stream_segment_type import StreamSegmentType
from ..rotation_direction import RotationDirection
from ..measurement import Measurement


@dataclass
class StreamArcRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    type: StreamSegmentType = next(first for first in StreamSegmentType)

    rotation_direction: RotationDirection = next(first for first in RotationDirection)

    center_x: Measurement = field(default_factory=Measurement.zero_values)

    center_y: Measurement = field(default_factory=Measurement.zero_values)

    end_x: Measurement = field(default_factory=Measurement.zero_values)

    end_y: Measurement = field(default_factory=Measurement.zero_values)

    target_axes_indices: List[int] = field(default_factory=list)

    endpoint: List[Measurement] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamArcRequest':
        return StreamArcRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            type=next(first for first in StreamSegmentType),
            rotation_direction=next(first for first in RotationDirection),
            center_x=Measurement.zero_values(),
            center_y=Measurement.zero_values(),
            end_x=Measurement.zero_values(),
            end_y=Measurement.zero_values(),
            target_axes_indices=[],
            endpoint=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamArcRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamArcRequest.from_dict(data)

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
            'rotationDirection': self.rotation_direction.value,
            'centerX': self.center_x.to_dict(),
            'centerY': self.center_y.to_dict(),
            'endX': self.end_x.to_dict(),
            'endY': self.end_y.to_dict(),
            'targetAxesIndices': [int(item) for item in self.target_axes_indices] if self.target_axes_indices is not None else [],
            'endpoint': [item.to_dict() for item in self.endpoint] if self.endpoint is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamArcRequest':
        return StreamArcRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            type=StreamSegmentType(data.get('type')),  # type: ignore
            rotation_direction=RotationDirection(data.get('rotationDirection')),  # type: ignore
            center_x=Measurement.from_dict(data.get('centerX')),  # type: ignore
            center_y=Measurement.from_dict(data.get('centerY')),  # type: ignore
            end_x=Measurement.from_dict(data.get('endX')),  # type: ignore
            end_y=Measurement.from_dict(data.get('endY')),  # type: ignore
            target_axes_indices=data.get('targetAxesIndices'),  # type: ignore
            endpoint=[Measurement.from_dict(item) for item in data.get('endpoint')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamArcRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamArcRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamArcRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamArcRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamArcRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamArcRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamArcRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamArcRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamArcRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "StreamArcRequest" is None.')

        if not isinstance(self.type, StreamSegmentType):
            raise ValueError(f'Property "Type" of "StreamArcRequest" is not an instance of "StreamSegmentType".')

        if self.rotation_direction is None:
            raise ValueError(f'Property "RotationDirection" of "StreamArcRequest" is None.')

        if not isinstance(self.rotation_direction, RotationDirection):
            raise ValueError(f'Property "RotationDirection" of "StreamArcRequest" is not an instance of "RotationDirection".')

        if self.center_x is None:
            raise ValueError(f'Property "CenterX" of "StreamArcRequest" is None.')

        if not isinstance(self.center_x, Measurement):
            raise ValueError(f'Property "CenterX" of "StreamArcRequest" is not an instance of "Measurement".')

        self.center_x.validate()

        if self.center_y is None:
            raise ValueError(f'Property "CenterY" of "StreamArcRequest" is None.')

        if not isinstance(self.center_y, Measurement):
            raise ValueError(f'Property "CenterY" of "StreamArcRequest" is not an instance of "Measurement".')

        self.center_y.validate()

        if self.end_x is None:
            raise ValueError(f'Property "EndX" of "StreamArcRequest" is None.')

        if not isinstance(self.end_x, Measurement):
            raise ValueError(f'Property "EndX" of "StreamArcRequest" is not an instance of "Measurement".')

        self.end_x.validate()

        if self.end_y is None:
            raise ValueError(f'Property "EndY" of "StreamArcRequest" is None.')

        if not isinstance(self.end_y, Measurement):
            raise ValueError(f'Property "EndY" of "StreamArcRequest" is not an instance of "Measurement".')

        self.end_y.validate()

        if self.target_axes_indices is not None:
            if not isinstance(self.target_axes_indices, Iterable):
                raise ValueError('Property "TargetAxesIndices" of "StreamArcRequest" is not iterable.')

            for i, target_axes_indices_item in enumerate(self.target_axes_indices):
                if target_axes_indices_item is None:
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamArcRequest" is None.')

                if not isinstance(target_axes_indices_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamArcRequest" is not a number.')

                if int(target_axes_indices_item) != target_axes_indices_item:
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamArcRequest" is not integer value.')

        if self.endpoint is not None:
            if not isinstance(self.endpoint, Iterable):
                raise ValueError('Property "Endpoint" of "StreamArcRequest" is not iterable.')

            for i, endpoint_item in enumerate(self.endpoint):
                if endpoint_item is None:
                    raise ValueError(f'Item {i} in property "Endpoint" of "StreamArcRequest" is None.')

                if not isinstance(endpoint_item, Measurement):
                    raise ValueError(f'Item {i} in property "Endpoint" of "StreamArcRequest" is not an instance of "Measurement".')

                endpoint_item.validate()
