# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .stream_segment_type import StreamSegmentType
from ..ascii.pvt_sequence_item import PvtSequenceItem, PvtSequenceItemWireFormat


@dataclass
class PvtItemsRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    type: StreamSegmentType = next(first for first in StreamSegmentType)

    sequence_data: List[PvtSequenceItem] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'PvtItemsRequest':
        return PvtItemsRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            type=next(first for first in StreamSegmentType),
            sequence_data=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtItemsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtItemsRequest.from_dict(data)

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
            'sequenceData': [PvtSequenceItemWireFormat(item).to_dict() for item in self.sequence_data] if self.sequence_data is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtItemsRequest':
        return PvtItemsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            type=StreamSegmentType(data.get('type')),  # type: ignore
            sequence_data=[PvtSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceData')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "PvtItemsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "PvtItemsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "PvtItemsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "PvtItemsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "PvtItemsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "PvtItemsRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "PvtItemsRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "PvtItemsRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "PvtItemsRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "PvtItemsRequest" is None.')

        if not isinstance(self.type, StreamSegmentType):
            raise ValueError(f'Property "Type" of "PvtItemsRequest" is not an instance of "StreamSegmentType".')

        if self.sequence_data is not None:
            if not isinstance(self.sequence_data, Iterable):
                raise ValueError('Property "SequenceData" of "PvtItemsRequest" is not iterable.')

            for i, sequence_data_item in enumerate(self.sequence_data):
                if sequence_data_item is None:
                    raise ValueError(f'Item {i} in property "SequenceData" of "PvtItemsRequest" is None.')

                PvtSequenceItemWireFormat(sequence_data_item).validate()
