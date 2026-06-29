# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.pvt_sequence_item import PvtSequenceItem, PvtSequenceItemWireFormat


@dataclass
class PvtGenerateSequenceResponse:

    sequence_data: List[PvtSequenceItem] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'PvtGenerateSequenceResponse':
        return PvtGenerateSequenceResponse(
            sequence_data=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtGenerateSequenceResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtGenerateSequenceResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sequenceData': [PvtSequenceItemWireFormat(item).to_dict() for item in self.sequence_data] if self.sequence_data is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtGenerateSequenceResponse':
        return PvtGenerateSequenceResponse(
            sequence_data=[PvtSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceData')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sequence_data is not None:
            if not isinstance(self.sequence_data, Iterable):
                raise ValueError('Property "SequenceData" of "PvtGenerateSequenceResponse" is not iterable.')

            for i, sequence_data_item in enumerate(self.sequence_data):
                if sequence_data_item is None:
                    raise ValueError(f'Item {i} in property "SequenceData" of "PvtGenerateSequenceResponse" is None.')

                PvtSequenceItemWireFormat(sequence_data_item).validate()
