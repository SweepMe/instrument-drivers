# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class Measurement:
    """
    Represents a numerical value with optional units specified.
    """

    value: float
    """
    Value of the measurement.
    """

    unit: Optional[UnitsAndLiterals] = None
    """
    Optional units of the measurement.
    """

    @staticmethod
    def zero_values() -> 'Measurement':
        return Measurement(
            value=0,
            unit=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Measurement':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Measurement.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': float(self.value),
            'unit': units_from_literals(self.unit).value if self.unit is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Measurement':
        return Measurement(
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')) if data.get('unit') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "Measurement" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "Measurement" is not a number.')

        if self.unit is not None:
            if not isinstance(self.unit, (Units, str)):
                raise ValueError(f'Property "Unit" of "Measurement" is not Units.')
