# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ..ascii.typed_setting import TypedSetting, TypedSettingWireFormat


@dataclass
class TypedSettingResponse:

    value: TypedSetting = 0

    @staticmethod
    def zero_values() -> 'TypedSettingResponse':
        return TypedSettingResponse(
            value=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TypedSettingResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TypedSettingResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': TypedSettingWireFormat(self.value).to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TypedSettingResponse':
        return TypedSettingResponse(
            value=TypedSettingWireFormat.from_dict(data.get('value')).convert_back(),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "TypedSettingResponse" is None.')

        TypedSettingWireFormat(self.value).validate()
