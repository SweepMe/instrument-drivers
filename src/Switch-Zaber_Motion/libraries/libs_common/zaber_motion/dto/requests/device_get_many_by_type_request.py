# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.get_setting import GetSetting


@dataclass
class DeviceGetManyByTypeRequest:

    interface_id: int = 0

    device: int = 0

    float_settings: List[GetSetting] = field(default_factory=list)

    int_settings: List[GetSetting] = field(default_factory=list)

    bool_settings: List[GetSetting] = field(default_factory=list)

    string_settings: List[GetSetting] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DeviceGetManyByTypeRequest':
        return DeviceGetManyByTypeRequest(
            interface_id=0,
            device=0,
            float_settings=[],
            int_settings=[],
            bool_settings=[],
            string_settings=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceGetManyByTypeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceGetManyByTypeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'floatSettings': [item.to_dict() for item in self.float_settings] if self.float_settings is not None else [],
            'intSettings': [item.to_dict() for item in self.int_settings] if self.int_settings is not None else [],
            'boolSettings': [item.to_dict() for item in self.bool_settings] if self.bool_settings is not None else [],
            'stringSettings': [item.to_dict() for item in self.string_settings] if self.string_settings is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceGetManyByTypeRequest':
        return DeviceGetManyByTypeRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            float_settings=[GetSetting.from_dict(item) for item in data.get('floatSettings')],  # type: ignore
            int_settings=[GetSetting.from_dict(item) for item in data.get('intSettings')],  # type: ignore
            bool_settings=[GetSetting.from_dict(item) for item in data.get('boolSettings')],  # type: ignore
            string_settings=[GetSetting.from_dict(item) for item in data.get('stringSettings')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceGetManyByTypeRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceGetManyByTypeRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceGetManyByTypeRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceGetManyByTypeRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceGetManyByTypeRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceGetManyByTypeRequest" is not integer value.')

        if self.float_settings is not None:
            if not isinstance(self.float_settings, Iterable):
                raise ValueError('Property "FloatSettings" of "DeviceGetManyByTypeRequest" is not iterable.')

            for i, float_settings_item in enumerate(self.float_settings):
                if float_settings_item is None:
                    raise ValueError(f'Item {i} in property "FloatSettings" of "DeviceGetManyByTypeRequest" is None.')

                if not isinstance(float_settings_item, GetSetting):
                    raise ValueError(f'Item {i} in property "FloatSettings" of "DeviceGetManyByTypeRequest" is not an instance of "GetSetting".')

                float_settings_item.validate()

        if self.int_settings is not None:
            if not isinstance(self.int_settings, Iterable):
                raise ValueError('Property "IntSettings" of "DeviceGetManyByTypeRequest" is not iterable.')

            for i, int_settings_item in enumerate(self.int_settings):
                if int_settings_item is None:
                    raise ValueError(f'Item {i} in property "IntSettings" of "DeviceGetManyByTypeRequest" is None.')

                if not isinstance(int_settings_item, GetSetting):
                    raise ValueError(f'Item {i} in property "IntSettings" of "DeviceGetManyByTypeRequest" is not an instance of "GetSetting".')

                int_settings_item.validate()

        if self.bool_settings is not None:
            if not isinstance(self.bool_settings, Iterable):
                raise ValueError('Property "BoolSettings" of "DeviceGetManyByTypeRequest" is not iterable.')

            for i, bool_settings_item in enumerate(self.bool_settings):
                if bool_settings_item is None:
                    raise ValueError(f'Item {i} in property "BoolSettings" of "DeviceGetManyByTypeRequest" is None.')

                if not isinstance(bool_settings_item, GetSetting):
                    raise ValueError(f'Item {i} in property "BoolSettings" of "DeviceGetManyByTypeRequest" is not an instance of "GetSetting".')

                bool_settings_item.validate()

        if self.string_settings is not None:
            if not isinstance(self.string_settings, Iterable):
                raise ValueError('Property "StringSettings" of "DeviceGetManyByTypeRequest" is not iterable.')

            for i, string_settings_item in enumerate(self.string_settings):
                if string_settings_item is None:
                    raise ValueError(f'Item {i} in property "StringSettings" of "DeviceGetManyByTypeRequest" is None.')

                if not isinstance(string_settings_item, GetSetting):
                    raise ValueError(f'Item {i} in property "StringSettings" of "DeviceGetManyByTypeRequest" is not an instance of "GetSetting".')

                string_settings_item.validate()
