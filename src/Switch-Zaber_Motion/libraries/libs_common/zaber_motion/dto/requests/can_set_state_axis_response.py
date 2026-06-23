# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class CanSetStateAxisResponse:

    axis_number: int = 0

    error: Optional[str] = None

    @staticmethod
    def zero_values() -> 'CanSetStateAxisResponse':
        return CanSetStateAxisResponse(
            error=None,
            axis_number=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CanSetStateAxisResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CanSetStateAxisResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': str(self.error) if self.error is not None else None,
            'axisNumber': int(self.axis_number),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CanSetStateAxisResponse':
        return CanSetStateAxisResponse(
            error=data.get('error'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.error is not None:
            if not isinstance(self.error, str):
                raise ValueError(f'Property "Error" of "CanSetStateAxisResponse" is not a string.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "CanSetStateAxisResponse" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "CanSetStateAxisResponse" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "CanSetStateAxisResponse" is not integer value.')
