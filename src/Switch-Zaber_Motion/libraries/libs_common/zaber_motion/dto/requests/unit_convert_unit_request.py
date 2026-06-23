# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class UnitConvertUnitRequest:

    value: float = 0

    from_unit: UnitsAndLiterals = Units.NATIVE

    to_unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'UnitConvertUnitRequest':
        return UnitConvertUnitRequest(
            value=0,
            from_unit=Units.NATIVE,
            to_unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnitConvertUnitRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnitConvertUnitRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': float(self.value),
            'fromUnit': units_from_literals(self.from_unit).value,
            'toUnit': units_from_literals(self.to_unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnitConvertUnitRequest':
        return UnitConvertUnitRequest(
            value=data.get('value'),  # type: ignore
            from_unit=Units(data.get('fromUnit')),  # type: ignore
            to_unit=Units(data.get('toUnit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "UnitConvertUnitRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "UnitConvertUnitRequest" is not a number.')

        if self.from_unit is None:
            raise ValueError(f'Property "FromUnit" of "UnitConvertUnitRequest" is None.')

        if not isinstance(self.from_unit, (Units, str)):
            raise ValueError(f'Property "FromUnit" of "UnitConvertUnitRequest" is not Units.')

        if self.to_unit is None:
            raise ValueError(f'Property "ToUnit" of "UnitConvertUnitRequest" is None.')

        if not isinstance(self.to_unit, (Units, str)):
            raise ValueError(f'Property "ToUnit" of "UnitConvertUnitRequest" is not Units.')
