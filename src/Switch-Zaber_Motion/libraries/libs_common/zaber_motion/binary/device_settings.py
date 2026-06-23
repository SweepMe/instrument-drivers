# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.binary.binary_settings import BinarySettings
from ..units import UnitsAndLiterals, Units

if TYPE_CHECKING:
    from .device import Device


class DeviceSettings:
    """
    Class providing access to various device settings and properties.
    """

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def get(
            self,
            setting: BinarySettings,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Setting to get.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = dto.BinaryDeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = call(
            "binary/device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_async(
            self,
            setting: BinarySettings,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Setting to get.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = dto.BinaryDeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = await call_async(
            "binary/device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set(
            self,
            setting: BinarySettings,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Setting to set.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = dto.BinaryDeviceSetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
            unit=unit,
        )
        call("binary/device/set_setting", request)

    async def set_async(
            self,
            setting: BinarySettings,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Setting to set.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = dto.BinaryDeviceSetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
            unit=unit,
        )
        await call_async("binary/device/set_setting", request)
