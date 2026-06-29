# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from .typed_setting import TypedSetting, TypedSettingWireFormat
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class GetAxisSettingTypedResult:
    """
    The response from a multi-get axis command with typed values.
    """

    setting: str
    """
    The setting read.
    """

    value: TypedSetting
    """
    The value returned.
    """

    unit: UnitsAndLiterals
    """
    The unit of the value.
    """

    @staticmethod
    def zero_values() -> 'GetAxisSettingTypedResult':
        return GetAxisSettingTypedResult(
            setting="",
            value=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetAxisSettingTypedResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetAxisSettingTypedResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'value': TypedSettingWireFormat(self.value).to_dict(),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetAxisSettingTypedResult':
        return GetAxisSettingTypedResult(
            setting=data.get('setting'),  # type: ignore
            value=TypedSettingWireFormat.from_dict(data.get('value')).convert_back(),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetAxisSettingTypedResult" is not a string.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "GetAxisSettingTypedResult" is None.')

        TypedSettingWireFormat(self.value).validate()

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "GetAxisSettingTypedResult" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "GetAxisSettingTypedResult" is not Units.')
