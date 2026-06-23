# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class DoubleResponse:

    value: float = 0

    @staticmethod
    def zero_values() -> 'DoubleResponse':
        return DoubleResponse(
            value=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DoubleResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DoubleResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': float(self.value),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DoubleResponse':
        return DoubleResponse(
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "DoubleResponse" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "DoubleResponse" is not a number.')
