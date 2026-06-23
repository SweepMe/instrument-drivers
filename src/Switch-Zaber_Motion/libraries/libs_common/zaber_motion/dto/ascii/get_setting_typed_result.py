# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .typed_setting import TypedSetting, TypedSettingWireFormat
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class GetSettingTypedResult:
    """
    The response from a multi-get command with typed values.
    """

    setting: str
    """
    The setting read.
    """

    values: List[TypedSetting]
    """
    The list of values returned.
    """

    unit: UnitsAndLiterals
    """
    The unit of the values.
    """

    @staticmethod
    def zero_values() -> 'GetSettingTypedResult':
        return GetSettingTypedResult(
            setting="",
            values=[],
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetSettingTypedResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetSettingTypedResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'values': [TypedSettingWireFormat(item).to_dict() for item in self.values] if self.values is not None else [],
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetSettingTypedResult':
        return GetSettingTypedResult(
            setting=data.get('setting'),  # type: ignore
            values=[TypedSettingWireFormat.from_dict(item).convert_back() for item in data.get('values')],  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetSettingTypedResult" is not a string.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "GetSettingTypedResult" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "GetSettingTypedResult" is None.')

                TypedSettingWireFormat(values_item).validate()

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "GetSettingTypedResult" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "GetSettingTypedResult" is not Units.')
