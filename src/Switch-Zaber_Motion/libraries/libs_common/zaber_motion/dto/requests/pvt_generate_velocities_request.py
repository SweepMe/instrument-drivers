# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.pvt_partial_sequence_item import PvtPartialSequenceItem, PvtPartialSequenceItemWireFormat


@dataclass
class PvtGenerateVelocitiesRequest:

    sequence_items: List[PvtPartialSequenceItem] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'PvtGenerateVelocitiesRequest':
        return PvtGenerateVelocitiesRequest(
            sequence_items=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtGenerateVelocitiesRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtGenerateVelocitiesRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sequenceItems': [PvtPartialSequenceItemWireFormat(item).to_dict() for item in self.sequence_items] if self.sequence_items is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtGenerateVelocitiesRequest':
        return PvtGenerateVelocitiesRequest(
            sequence_items=[PvtPartialSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceItems')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sequence_items is not None:
            if not isinstance(self.sequence_items, Iterable):
                raise ValueError('Property "SequenceItems" of "PvtGenerateVelocitiesRequest" is not iterable.')

            for i, sequence_items_item in enumerate(self.sequence_items):
                if sequence_items_item is None:
                    raise ValueError(f'Item {i} in property "SequenceItems" of "PvtGenerateVelocitiesRequest" is None.')

                PvtPartialSequenceItemWireFormat(sequence_items_item).validate()
