# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from ..units import Units

if TYPE_CHECKING:
    from .axis import Axis


class AxisSettings:
    """
    Class providing access to various axis settings and properties.
    """

    def __init__(self, axis: 'Axis'):
        self._axis = axis

    def get(
            self,
            setting: str,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns any axis setting or property.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        call("device/get_setting", request, response)
        return response.value

    async def get_async(
            self,
            setting: str,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns any axis setting or property.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        await call_async("device/get_setting", request, response)
        return response.value

    def set(
            self,
            setting: str,
            value: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets any axis setting.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = unit.value
        call("device/set_setting", request)

    async def set_async(
            self,
            setting: str,
            value: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets any axis setting.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = unit.value
        await call_async("device/set_setting", request)

    def get_string(
            self,
            setting: str
    ) -> str:
        """
        Returns any axis setting or property as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.DeviceGetSettingStrResponse()
        call("device/get_setting_str", request, response)
        return response.value

    async def get_string_async(
            self,
            setting: str
    ) -> str:
        """
        Returns any axis setting or property as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.DeviceGetSettingStrResponse()
        await call_async("device/get_setting_str", request, response)
        return response.value

    def set_string(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any axis setting as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingStrRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        call("device/set_setting_str", request)

    async def set_string_async(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any axis setting as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingStrRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        await call_async("device/set_setting_str", request)

    def convert_to_native_units(
            self,
            setting: str,
            value: float,
            unit: Units
    ) -> float:
        """
        Convert arbitrary setting value to Zaber native units.

        Args:
            setting: Name of the setting.
            value: Value of the setting in units specified by following argument.
            unit: Units of the value.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceConvertSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = unit.value
        response = main_pb2.DeviceConvertSettingResponse()
        call_sync("device/convert_setting", request, response)
        return response.value

    def convert_from_native_units(
            self,
            setting: str,
            value: float,
            unit: Units
    ) -> float:
        """
        Convert arbitrary setting value from Zaber native units.

        Args:
            setting: Name of the setting.
            value: Value of the setting in Zaber native units.
            unit: Units to convert value to.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceConvertSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.from_native = True
        request.setting = setting
        request.value = value
        request.unit = unit.value
        response = main_pb2.DeviceConvertSettingResponse()
        call_sync("device/convert_setting", request, response)
        return response.value
