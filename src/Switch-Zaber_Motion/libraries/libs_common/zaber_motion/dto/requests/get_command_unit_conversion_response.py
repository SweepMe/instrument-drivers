# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from ..unit_conversion_descriptor import UnitConversionDescriptor


@dataclass
class GetCommandUnitConversionResponse:

    value: List[Optional[UnitConversionDescriptor]] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'GetCommandUnitConversionResponse':
        return GetCommandUnitConversionResponse(
            value=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetCommandUnitConversionResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetCommandUnitConversionResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': [item.to_dict() if item is not None else None for item in self.value] if self.value is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetCommandUnitConversionResponse':
        return GetCommandUnitConversionResponse(
            value=[UnitConversionDescriptor.from_dict(item) if item is not None else None for item in data.get('value')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is not None:
            if not isinstance(self.value, Iterable):
                raise ValueError('Property "Value" of "GetCommandUnitConversionResponse" is not iterable.')

            for i, value_item in enumerate(self.value):
                if value_item is not None:
                    if not isinstance(value_item, UnitConversionDescriptor):
                        raise ValueError(f'Item {i} in property "Value" of "GetCommandUnitConversionResponse" is not an instance of "UnitConversionDescriptor".')

                    value_item.validate()
