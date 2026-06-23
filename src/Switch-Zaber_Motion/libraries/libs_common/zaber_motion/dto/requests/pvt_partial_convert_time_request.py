# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.pvt_partial_sequence_item import PvtPartialSequenceItem, PvtPartialSequenceItemWireFormat


@dataclass
class PvtPartialConvertTimeRequest:

    sequence_data: List[PvtPartialSequenceItem] = field(default_factory=list)

    from_absolute: bool = False

    @staticmethod
    def zero_values() -> 'PvtPartialConvertTimeRequest':
        return PvtPartialConvertTimeRequest(
            sequence_data=[],
            from_absolute=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPartialConvertTimeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPartialConvertTimeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sequenceData': [PvtPartialSequenceItemWireFormat(item).to_dict() for item in self.sequence_data] if self.sequence_data is not None else [],
            'fromAbsolute': bool(self.from_absolute),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPartialConvertTimeRequest':
        return PvtPartialConvertTimeRequest(
            sequence_data=[PvtPartialSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceData')],  # type: ignore
            from_absolute=data.get('fromAbsolute'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sequence_data is not None:
            if not isinstance(self.sequence_data, Iterable):
                raise ValueError('Property "SequenceData" of "PvtPartialConvertTimeRequest" is not iterable.')

            for i, sequence_data_item in enumerate(self.sequence_data):
                if sequence_data_item is None:
                    raise ValueError(f'Item {i} in property "SequenceData" of "PvtPartialConvertTimeRequest" is None.')

                PvtPartialSequenceItemWireFormat(sequence_data_item).validate()
