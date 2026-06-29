# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class SetStateAxisResponse:
    """
    An object containing any non-blocking issues encountered when loading a saved state to an axis.
    """

    warnings: List[str]
    """
    The warnings encountered when applying this state to the given axis.
    """

    axis_number: int
    """
    The number of the axis that was set.
    """

    @staticmethod
    def zero_values() -> 'SetStateAxisResponse':
        return SetStateAxisResponse(
            warnings=[],
            axis_number=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetStateAxisResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetStateAxisResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'warnings': [str(item or '') for item in self.warnings] if self.warnings is not None else [],
            'axisNumber': int(self.axis_number),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetStateAxisResponse':
        return SetStateAxisResponse(
            warnings=data.get('warnings'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.warnings is not None:
            if not isinstance(self.warnings, Iterable):
                raise ValueError('Property "Warnings" of "SetStateAxisResponse" is not iterable.')

            for i, warnings_item in enumerate(self.warnings):
                if warnings_item is not None:
                    if not isinstance(warnings_item, str):
                        raise ValueError(f'Item {i} in property "Warnings" of "SetStateAxisResponse" is not a string.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "SetStateAxisResponse" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "SetStateAxisResponse" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "SetStateAxisResponse" is not integer value.')
