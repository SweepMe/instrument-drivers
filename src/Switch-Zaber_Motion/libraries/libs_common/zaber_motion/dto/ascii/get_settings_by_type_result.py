# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .get_setting_result import GetSettingResult
from .get_setting_int_result import GetSettingIntResult
from .get_setting_bool_result import GetSettingBoolResult
from .get_setting_string_result import GetSettingStringResult


@dataclass
class GetSettingsByTypeResult:
    """
    The response from a multi-get command with values grouped by type.
    """

    float_settings: List[GetSettingResult]
    """
    Float setting results.
    """

    int_settings: List[GetSettingIntResult]
    """
    Integer setting results.
    """

    bool_settings: List[GetSettingBoolResult]
    """
    Boolean setting results.
    """

    string_settings: List[GetSettingStringResult]
    """
    String setting results.
    """

    @staticmethod
    def zero_values() -> 'GetSettingsByTypeResult':
        return GetSettingsByTypeResult(
            float_settings=[],
            int_settings=[],
            bool_settings=[],
            string_settings=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetSettingsByTypeResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetSettingsByTypeResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'floatSettings': [item.to_dict() for item in self.float_settings] if self.float_settings is not None else [],
            'intSettings': [item.to_dict() for item in self.int_settings] if self.int_settings is not None else [],
            'boolSettings': [item.to_dict() for item in self.bool_settings] if self.bool_settings is not None else [],
            'stringSettings': [item.to_dict() for item in self.string_settings] if self.string_settings is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetSettingsByTypeResult':
        return GetSettingsByTypeResult(
            float_settings=[GetSettingResult.from_dict(item) for item in data.get('floatSettings')],  # type: ignore
            int_settings=[GetSettingIntResult.from_dict(item) for item in data.get('intSettings')],  # type: ignore
            bool_settings=[GetSettingBoolResult.from_dict(item) for item in data.get('boolSettings')],  # type: ignore
            string_settings=[GetSettingStringResult.from_dict(item) for item in data.get('stringSettings')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.float_settings is not None:
            if not isinstance(self.float_settings, Iterable):
                raise ValueError('Property "FloatSettings" of "GetSettingsByTypeResult" is not iterable.')

            for i, float_settings_item in enumerate(self.float_settings):
                if float_settings_item is None:
                    raise ValueError(f'Item {i} in property "FloatSettings" of "GetSettingsByTypeResult" is None.')

                if not isinstance(float_settings_item, GetSettingResult):
                    raise ValueError(f'Item {i} in property "FloatSettings" of "GetSettingsByTypeResult" is not an instance of "GetSettingResult".')

                float_settings_item.validate()

        if self.int_settings is not None:
            if not isinstance(self.int_settings, Iterable):
                raise ValueError('Property "IntSettings" of "GetSettingsByTypeResult" is not iterable.')

            for i, int_settings_item in enumerate(self.int_settings):
                if int_settings_item is None:
                    raise ValueError(f'Item {i} in property "IntSettings" of "GetSettingsByTypeResult" is None.')

                if not isinstance(int_settings_item, GetSettingIntResult):
                    raise ValueError(f'Item {i} in property "IntSettings" of "GetSettingsByTypeResult" is not an instance of "GetSettingIntResult".')

                int_settings_item.validate()

        if self.bool_settings is not None:
            if not isinstance(self.bool_settings, Iterable):
                raise ValueError('Property "BoolSettings" of "GetSettingsByTypeResult" is not iterable.')

            for i, bool_settings_item in enumerate(self.bool_settings):
                if bool_settings_item is None:
                    raise ValueError(f'Item {i} in property "BoolSettings" of "GetSettingsByTypeResult" is None.')

                if not isinstance(bool_settings_item, GetSettingBoolResult):
                    raise ValueError(f'Item {i} in property "BoolSettings" of "GetSettingsByTypeResult" is not an instance of "GetSettingBoolResult".')

                bool_settings_item.validate()

        if self.string_settings is not None:
            if not isinstance(self.string_settings, Iterable):
                raise ValueError('Property "StringSettings" of "GetSettingsByTypeResult" is not iterable.')

            for i, string_settings_item in enumerate(self.string_settings):
                if string_settings_item is None:
                    raise ValueError(f'Item {i} in property "StringSettings" of "GetSettingsByTypeResult" is None.')

                if not isinstance(string_settings_item, GetSettingStringResult):
                    raise ValueError(f'Item {i} in property "StringSettings" of "GetSettingsByTypeResult" is not an instance of "GetSettingStringResult".')

                string_settings_item.validate()
