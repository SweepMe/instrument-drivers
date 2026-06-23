# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class GetAxisSettingResult:
    """
    The response from a multi-get axis command.
    """

    setting: str
    """
    The setting read.
    """

    value: float
    """
    The value read.
    """

    unit: UnitsAndLiterals
    """
    The unit of the values.
    """

    @staticmethod
    def zero_values() -> 'GetAxisSettingResult':
        return GetAxisSettingResult(
            setting="",
            value=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetAxisSettingResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetAxisSettingResult.from_dict(data)

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
    def from_dict(data: Dict[str, Any]) -> 'GetAxisSettingResult':
        return GetAxisSettingResult(
            setting=data.get('setting'),  # type: ignore
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetAxisSettingResult" is not a string.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "GetAxisSettingResult" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "GetAxisSettingResult" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "GetAxisSettingResult" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "GetAxisSettingResult" is not Units.')
