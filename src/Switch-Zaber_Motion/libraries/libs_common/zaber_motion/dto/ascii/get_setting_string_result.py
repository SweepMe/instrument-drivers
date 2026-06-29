# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson


@dataclass
class GetSettingStringResult:
    """
    The response from a multi-get command with string values.
    """

    setting: str
    """
    The setting read.
    """

    values: List[str]
    """
    The list of values returned.
    """

    @staticmethod
    def zero_values() -> 'GetSettingStringResult':
        return GetSettingStringResult(
            setting="",
            values=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetSettingStringResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetSettingStringResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'values': [str(item or '') for item in self.values] if self.values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetSettingStringResult':
        return GetSettingStringResult(
            setting=data.get('setting'),  # type: ignore
            values=data.get('values'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetSettingStringResult" is not a string.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "GetSettingStringResult" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is not None:
                    if not isinstance(values_item, str):
                        raise ValueError(f'Item {i} in property "Values" of "GetSettingStringResult" is not a string.')
