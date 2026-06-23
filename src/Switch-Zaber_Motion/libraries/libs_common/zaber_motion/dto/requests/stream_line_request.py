# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .stream_segment_type import StreamSegmentType
from ..measurement import Measurement


@dataclass
class StreamLineRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    type: StreamSegmentType = next(first for first in StreamSegmentType)

    endpoint: List[Measurement] = field(default_factory=list)

    target_axes_indices: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamLineRequest':
        return StreamLineRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            type=next(first for first in StreamSegmentType),
            endpoint=[],
            target_axes_indices=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamLineRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamLineRequest.from_dict(data)

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
            'endpoint': [item.to_dict() for item in self.endpoint] if self.endpoint is not None else [],
            'targetAxesIndices': [int(item) for item in self.target_axes_indices] if self.target_axes_indices is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamLineRequest':
        return StreamLineRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            type=StreamSegmentType(data.get('type')),  # type: ignore
            endpoint=[Measurement.from_dict(item) for item in data.get('endpoint')],  # type: ignore
            target_axes_indices=data.get('targetAxesIndices'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamLineRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamLineRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamLineRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamLineRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamLineRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamLineRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamLineRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamLineRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamLineRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "StreamLineRequest" is None.')

        if not isinstance(self.type, StreamSegmentType):
            raise ValueError(f'Property "Type" of "StreamLineRequest" is not an instance of "StreamSegmentType".')

        if self.endpoint is not None:
            if not isinstance(self.endpoint, Iterable):
                raise ValueError('Property "Endpoint" of "StreamLineRequest" is not iterable.')

            for i, endpoint_item in enumerate(self.endpoint):
                if endpoint_item is None:
                    raise ValueError(f'Item {i} in property "Endpoint" of "StreamLineRequest" is None.')

                if not isinstance(endpoint_item, Measurement):
                    raise ValueError(f'Item {i} in property "Endpoint" of "StreamLineRequest" is not an instance of "Measurement".')

                endpoint_item.validate()

        if self.target_axes_indices is not None:
            if not isinstance(self.target_axes_indices, Iterable):
                raise ValueError('Property "TargetAxesIndices" of "StreamLineRequest" is not iterable.')

            for i, target_axes_indices_item in enumerate(self.target_axes_indices):
                if target_axes_indices_item is None:
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamLineRequest" is None.')

                if not isinstance(target_axes_indices_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamLineRequest" is not a number.')

                if int(target_axes_indices_item) != target_axes_indices_item:
                    raise ValueError(f'Item {i} in property "TargetAxesIndices" of "StreamLineRequest" is not integer value.')
