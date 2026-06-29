# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class ConversionFactor:
    """
    Represents unit conversion factor for a single dimension.
    """

    setting: str
    """
    Setting representing the dimension.
    """

    value: float
    """
    Value representing 1 native device unit in specified real-word units.
    """

    unit: UnitsAndLiterals
    """
    Units of the value.
    """

    @staticmethod
    def zero_values() -> 'ConversionFactor':
        return ConversionFactor(
            setting="",
            value=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ConversionFactor':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ConversionFactor.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'value': float(self.value),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ConversionFactor':
        return ConversionFactor(
            setting=data.get('setting'),  # type: ignore
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "ConversionFactor" is not a string.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "ConversionFactor" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "ConversionFactor" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "ConversionFactor" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "ConversionFactor" is not Units.')
