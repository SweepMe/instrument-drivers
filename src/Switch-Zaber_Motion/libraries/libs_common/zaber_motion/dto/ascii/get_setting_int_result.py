# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class GetSettingIntResult:
    """
    The response from a multi-get command with integer values.
    """

    setting: str
    """
    The setting read.
    """

    values: List[int]
    """
    The list of values returned.
    """

    @staticmethod
    def zero_values() -> 'GetSettingIntResult':
        return GetSettingIntResult(
            setting="",
            values=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetSettingIntResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetSettingIntResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'values': [int(item) for item in self.values] if self.values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetSettingIntResult':
        return GetSettingIntResult(
            setting=data.get('setting'),  # type: ignore
            values=data.get('values'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetSettingIntResult" is not a string.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "GetSettingIntResult" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "GetSettingIntResult" is None.')

                if not isinstance(values_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Values" of "GetSettingIntResult" is not a number.')

                if int(values_item) != values_item:
                    raise ValueError(f'Item {i} in property "Values" of "GetSettingIntResult" is not integer value.')
