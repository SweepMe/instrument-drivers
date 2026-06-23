# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..unit_conversion_descriptor import UnitConversionDescriptor
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class UnitConvertNativeRequest:

    value: float = 0

    values: List[float] = field(default_factory=list)

    unit: UnitsAndLiterals = Units.NATIVE

    conversion: UnitConversionDescriptor = field(default_factory=UnitConversionDescriptor.zero_values)

    round: bool = False

    @staticmethod
    def zero_values() -> 'UnitConvertNativeRequest':
        return UnitConvertNativeRequest(
            value=0,
            values=[],
            unit=Units.NATIVE,
            conversion=UnitConversionDescriptor.zero_values(),
            round=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnitConvertNativeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnitConvertNativeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': float(self.value),
            'values': [float(item) for item in self.values] if self.values is not None else [],
            'unit': units_from_literals(self.unit).value,
            'conversion': self.conversion.to_dict(),
            'round': bool(self.round),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnitConvertNativeRequest':
        return UnitConvertNativeRequest(
            value=data.get('value'),  # type: ignore
            values=data.get('values'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            conversion=UnitConversionDescriptor.from_dict(data.get('conversion')),  # type: ignore
            round=data.get('round'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "UnitConvertNativeRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "UnitConvertNativeRequest" is not a number.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "UnitConvertNativeRequest" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "UnitConvertNativeRequest" is None.')

                if not isinstance(values_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Values" of "UnitConvertNativeRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "UnitConvertNativeRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "UnitConvertNativeRequest" is not Units.')

        if self.conversion is None:
            raise ValueError(f'Property "Conversion" of "UnitConvertNativeRequest" is None.')

        if not isinstance(self.conversion, UnitConversionDescriptor):
            raise ValueError(f'Property "Conversion" of "UnitConvertNativeRequest" is not an instance of "UnitConversionDescriptor".')

        self.conversion.validate()
