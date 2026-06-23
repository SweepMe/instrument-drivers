# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.get_setting import GetSetting
from ..ascii.get_axis_setting import GetAxisSetting


@dataclass
class DeviceMultiGetSettingRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    settings: List[GetSetting] = field(default_factory=list)

    axis_settings: List[GetAxisSetting] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DeviceMultiGetSettingRequest':
        return DeviceMultiGetSettingRequest(
            interface_id=0,
            device=0,
            axis=0,
            settings=[],
            axis_settings=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceMultiGetSettingRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceMultiGetSettingRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'settings': [item.to_dict() for item in self.settings] if self.settings is not None else [],
            'axisSettings': [item.to_dict() for item in self.axis_settings] if self.axis_settings is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceMultiGetSettingRequest':
        return DeviceMultiGetSettingRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            settings=[GetSetting.from_dict(item) for item in data.get('settings')],  # type: ignore
            axis_settings=[GetAxisSetting.from_dict(item) for item in data.get('axisSettings')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceMultiGetSettingRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceMultiGetSettingRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceMultiGetSettingRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceMultiGetSettingRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceMultiGetSettingRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceMultiGetSettingRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceMultiGetSettingRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceMultiGetSettingRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceMultiGetSettingRequest" is not integer value.')

        if self.settings is not None:
            if not isinstance(self.settings, Iterable):
                raise ValueError('Property "Settings" of "DeviceMultiGetSettingRequest" is not iterable.')

            for i, settings_item in enumerate(self.settings):
                if settings_item is None:
                    raise ValueError(f'Item {i} in property "Settings" of "DeviceMultiGetSettingRequest" is None.')

                if not isinstance(settings_item, GetSetting):
                    raise ValueError(f'Item {i} in property "Settings" of "DeviceMultiGetSettingRequest" is not an instance of "GetSetting".')

                settings_item.validate()

        if self.axis_settings is not None:
            if not isinstance(self.axis_settings, Iterable):
                raise ValueError('Property "AxisSettings" of "DeviceMultiGetSettingRequest" is not iterable.')

            for i, axis_settings_item in enumerate(self.axis_settings):
                if axis_settings_item is None:
                    raise ValueError(f'Item {i} in property "AxisSettings" of "DeviceMultiGetSettingRequest" is None.')

                if not isinstance(axis_settings_item, GetAxisSetting):
                    raise ValueError(f'Item {i} in property "AxisSettings" of "DeviceMultiGetSettingRequest" is not an instance of "GetAxisSetting".')

                axis_settings_item.validate()
