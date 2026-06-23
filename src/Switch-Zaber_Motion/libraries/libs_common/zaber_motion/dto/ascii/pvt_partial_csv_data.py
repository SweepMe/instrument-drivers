# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .pvt_partial_sequence_item import PvtPartialSequenceItem, PvtPartialSequenceItemWireFormat


@dataclass
class PvtPartialCsvData:
    """
    Data representing content loaded from PVT CSV file, with partial sequence data and sequence names.
    """

    sequence_data: List[PvtPartialSequenceItem]
    """
    The points and actions of the PVT sequence.
    """

    series_names: List[str]
    """
    The names of the columns in the CSV header.
    If the header columns do not contain names, these will default to `Series 1`, `Series 2`, etc..
    """

    @staticmethod
    def zero_values() -> 'PvtPartialCsvData':
        return PvtPartialCsvData(
            sequence_data=[],
            series_names=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPartialCsvData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPartialCsvData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sequenceData': [PvtPartialSequenceItemWireFormat(item).to_dict() for item in self.sequence_data] if self.sequence_data is not None else [],
            'seriesNames': [str(item or '') for item in self.series_names] if self.series_names is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPartialCsvData':
        return PvtPartialCsvData(
            sequence_data=[PvtPartialSequenceItemWireFormat.from_dict(item).convert_back() for item in data.get('sequenceData')],  # type: ignore
            series_names=data.get('seriesNames'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sequence_data is not None:
            if not isinstance(self.sequence_data, Iterable):
                raise ValueError('Property "SequenceData" of "PvtPartialCsvData" is not iterable.')

            for i, sequence_data_item in enumerate(self.sequence_data):
                if sequence_data_item is None:
                    raise ValueError(f'Item {i} in property "SequenceData" of "PvtPartialCsvData" is None.')

                PvtPartialSequenceItemWireFormat(sequence_data_item).validate()

        if self.series_names is not None:
            if not isinstance(self.series_names, Iterable):
                raise ValueError('Property "SeriesNames" of "PvtPartialCsvData" is not iterable.')

            for i, series_names_item in enumerate(self.series_names):
                if series_names_item is not None:
                    if not isinstance(series_names_item, str):
                        raise ValueError(f'Item {i} in property "SeriesNames" of "PvtPartialCsvData" is not a string.')
