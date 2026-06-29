# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DeviceConvertSettingRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    setting: str = ""

    unit: UnitsAndLiterals = Units.NATIVE

    value: float = 0

    from_native: bool = False

    round: bool = False

    @staticmethod
    def zero_values() -> 'DeviceConvertSettingRequest':
        return DeviceConvertSettingRequest(
            interface_id=0,
            device=0,
            axis=0,
            setting="",
            unit=Units.NATIVE,
            value=0,
            from_native=False,
            round=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceConvertSettingRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceConvertSettingRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'setting': str(self.setting or ''),
            'unit': units_from_literals(self.unit).value,
            'value': float(self.value),
            'fromNative': bool(self.from_native),
            'round': bool(self.round),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceConvertSettingRequest':
        return DeviceConvertSettingRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            setting=data.get('setting'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            value=data.get('value'),  # type: ignore
            from_native=data.get('fromNative'),  # type: ignore
            round=data.get('round'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceConvertSettingRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceConvertSettingRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceConvertSettingRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceConvertSettingRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceConvertSettingRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceConvertSettingRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceConvertSettingRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceConvertSettingRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceConvertSettingRequest" is not integer value.')

        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "DeviceConvertSettingRequest" is not a string.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "DeviceConvertSettingRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "DeviceConvertSettingRequest" is not Units.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "DeviceConvertSettingRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "DeviceConvertSettingRequest" is not a number.')
