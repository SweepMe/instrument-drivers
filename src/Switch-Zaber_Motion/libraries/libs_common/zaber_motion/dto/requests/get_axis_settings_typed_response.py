# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.get_axis_setting_typed_result import GetAxisSettingTypedResult


@dataclass
class GetAxisSettingsTypedResponse:

    values: List[GetAxisSettingTypedResult] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'GetAxisSettingsTypedResponse':
        return GetAxisSettingsTypedResponse(
            values=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetAxisSettingsTypedResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetAxisSettingsTypedResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'values': [item.to_dict() for item in self.values] if self.values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetAxisSettingsTypedResponse':
        return GetAxisSettingsTypedResponse(
            values=[GetAxisSettingTypedResult.from_dict(item) for item in data.get('values')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "GetAxisSettingsTypedResponse" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "GetAxisSettingsTypedResponse" is None.')

                if not isinstance(values_item, GetAxisSettingTypedResult):
                    raise ValueError(f'Item {i} in property "Values" of "GetAxisSettingsTypedResponse" is not an instance of "GetAxisSettingTypedResult".')

                values_item.validate()
