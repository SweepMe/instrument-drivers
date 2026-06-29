# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from ..ascii.pvt_sequence_item import PvtSequenceItem, PvtSequenceItemWireFormat


@dataclass
class PvtSaveCsvRequest:

    sequence_data: List[PvtSequenceItem] = field(default_factory=list)

    path: str = ""

    dimension_names: Optional[List[str]] = None

    @staticmethod
    def zero_values() -> 'PvtSaveCsvRequest':
        return PvtSaveCsvRequest(
            sequence_data=[],
            path="",
            dimension_names=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtSaveCsvRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtSaveCsvRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sequenceData': [PvtSequenceItemWireFormat(item).to_dict() for item in self.sequence_data] if self.sequence_data is not None else [],
            'path': str(self.path or ''),
            'dimensionNames': [str(item or '') for item in self.dimension_names] if self.dimension_names is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtSaveCsvRequest':
        return PvtSaveCsvRequest(
            sequence_data=[PvtSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceData')],  # type: ignore
            path=data.get('path'),  # type: ignore
            dimension_names=data.get('dimensionNames'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sequence_data is not None:
            if not isinstance(self.sequence_data, Iterable):
                raise ValueError('Property "SequenceData" of "PvtSaveCsvRequest" is not iterable.')

            for i, sequence_data_item in enumerate(self.sequence_data):
                if sequence_data_item is None:
                    raise ValueError(f'Item {i} in property "SequenceData" of "PvtSaveCsvRequest" is None.')

                PvtSequenceItemWireFormat(sequence_data_item).validate()

        if self.path is not None:
            if not isinstance(self.path, str):
                raise ValueError(f'Property "Path" of "PvtSaveCsvRequest" is not a string.')

        if self.dimension_names is not None:
            if not isinstance(self.dimension_names, Iterable):
                raise ValueError('Property "DimensionNames" of "PvtSaveCsvRequest" is not iterable.')

            for i, dimension_names_item in enumerate(self.dimension_names):
                if dimension_names_item is not None:
                    if not isinstance(dimension_names_item, str):
                        raise ValueError(f'Item {i} in property "DimensionNames" of "PvtSaveCsvRequest" is not a string.')
