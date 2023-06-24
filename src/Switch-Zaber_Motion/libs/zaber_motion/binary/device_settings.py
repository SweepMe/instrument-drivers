# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from ..call import call, call_async

from ..protobufs import main_pb2
from ..units import Units
from .binary_settings import BinarySettings

if TYPE_CHECKING:
    from .device import Device


class DeviceSettings:
    """
    Class providing access to various device settings and properties.
    """

    def __init__(self, device: 'Device'):
        self._device = device

    def get(
            self,
            setting: BinarySettings,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Setting to get.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.BinaryDeviceGetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting.value
        request.unit = unit.value
        response = main_pb2.BinaryDeviceGetSettingResponse()
        call("binary/device/get_setting", request, response)
        return response.value

    async def get_async(
            self,
            setting: BinarySettings,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Setting to get.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.BinaryDeviceGetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting.value
        request.unit = unit.value
        response = main_pb2.BinaryDeviceGetSettingResponse()
        await call_async("binary/device/get_setting", request, response)
        return response.value

    def set(
            self,
            setting: BinarySettings,
            value: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Setting to set.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.BinaryDeviceSetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting.value
        request.value = value
        request.unit = unit.value
        call("binary/device/set_setting", request)

    async def set_async(
            self,
            setting: BinarySettings,
            value: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Setting to set.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.BinaryDeviceSetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting.value
        request.value = value
        request.unit = unit.value
        await call_async("binary/device/set_setting", request)
