# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class AxisMapping:
    """
    Maps a translator axis to a Zaber stream axis.
    """

    axis_letter: str
    """
    Letter of the translator axis (X,Y,Z,A,B,C,E).
    """

    axis_index: int
    """
    Index of the stream axis.
    """

    @staticmethod
    def zero_values() -> 'AxisMapping':
        return AxisMapping(
            axis_letter="",
            axis_index=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisMapping':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisMapping.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisLetter': str(self.axis_letter or ''),
            'axisIndex': int(self.axis_index),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisMapping':
        return AxisMapping(
            axis_letter=data.get('axisLetter'),  # type: ignore
            axis_index=data.get('axisIndex'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_letter is not None:
            if not isinstance(self.axis_letter, str):
                raise ValueError(f'Property "AxisLetter" of "AxisMapping" is not a string.')

        if self.axis_index is None:
            raise ValueError(f'Property "AxisIndex" of "AxisMapping" is None.')

        if not isinstance(self.axis_index, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisIndex" of "AxisMapping" is not a number.')

        if int(self.axis_index) != self.axis_index:
            raise ValueError(f'Property "AxisIndex" of "AxisMapping" is not integer value.')
