# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.typed_setting import TypedSetting
from ..dto.ascii.get_setting import GetSetting
from ..dto.ascii.get_settings_by_type_result import GetSettingsByTypeResult
from ..dto.ascii.get_setting_result import GetSettingResult
from ..dto.ascii.get_setting_typed_result import GetSettingTypedResult
from ..dto.unit_conversion_descriptor import UnitConversionDescriptor
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
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_async(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any device setting or property.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_typed(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> TypedSetting:
        """
        Returns any device setting or property in its native type.
        Note that specifying units will cause settings that are otherwise integers to be returned as floats.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting to convert result to.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = call(
            "device/get_setting_typed",
            request,
            dto.TypedSettingResponse.from_binary)
        return response.value

    async def get_typed_async(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> TypedSetting:
        """
        Returns any device setting or property in its native type.
        Note that specifying units will cause settings that are otherwise integers to be returned as floats.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting to convert result to.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = await call_async(
            "device/get_setting_typed",
            request,
            dto.TypedSettingResponse.from_binary)
        return response.value

    def set(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
            unit=unit,
        )
        call("device/set_setting", request)

    async def set_async(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any device setting.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
            unit=unit,
        )
        await call_async("device/set_setting", request)

    def get_string(
            self,
            setting: str
    ) -> str:
        """
        Returns any device setting or property as a string.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call(
            "device/get_setting_str",
            request,
            dto.StringResponse.from_binary)
        return response.value

    async def get_string_async(
            self,
            setting: str
    ) -> str:
        """
        Returns any device setting or property as a string.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = await call_async(
            "device/get_setting_str",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def set_string(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any device setting as a string.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingStrRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        call("device/set_setting_str", request)

    async def set_string_async(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any device setting as a string.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingStrRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        await call_async("device/set_setting_str", request)

    def get_int(
            self,
            setting: str
    ) -> int:
        """
        Returns any device setting or property as an integer.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call(
            "device/get_setting_int",
            request,
            dto.Int64Response.from_binary)
        return response.value

    async def get_int_async(
            self,
            setting: str
    ) -> int:
        """
        Returns any device setting or property as an integer.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = await call_async(
            "device/get_setting_int",
            request,
            dto.Int64Response.from_binary)
        return response.value

    def set_int(
            self,
            setting: str,
            value: int
    ) -> None:
        """
        Sets any device setting or property as an integer.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingIntRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        call("device/set_setting_int", request)

    async def set_int_async(
            self,
            setting: str,
            value: int
    ) -> None:
        """
        Sets any device setting or property as an integer.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingIntRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        await call_async("device/set_setting_int", request)

    def get_bool(
            self,
            setting: str
    ) -> bool:
        """
        Returns any device setting or property as a boolean.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call(
            "device/get_setting_bool",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def get_bool_async(
            self,
            setting: str
    ) -> bool:
        """
        Returns any device setting or property as a boolean.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = await call_async(
            "device/get_setting_bool",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def set_bool(
            self,
            setting: str,
            value: bool
    ) -> None:
        """
        Sets any device setting as a boolean.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingBoolRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        call("device/set_setting_bool", request)

    async def set_bool_async(
            self,
            setting: str,
            value: bool
    ) -> None:
        """
        Sets any device setting as a boolean.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = dto.DeviceSetSettingBoolRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
        )
        await call_async("device/set_setting_bool", request)

    def convert_to_native_units(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals,
            round: bool = False
    ) -> float:
        """
        Convert arbitrary setting value to Zaber native units.

        Args:
            setting: Name of the setting.
            value: Value of the setting in units specified by following argument.
            unit: Units of the value.
            round: If true, round the result to the device's native decimal places.

        Returns:
            Setting value.
        """
        request = dto.DeviceConvertSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            value=value,
            unit=unit,
            round=round,
        )
        response = call_sync(
            "device/convert_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def convert_from_native_units(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals
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
        request = dto.DeviceConvertSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            from_native=True,
            setting=setting,
            value=value,
            unit=unit,
        )
        response = call_sync(
            "device/convert_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_default(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns the default value of a setting.

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Default setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
            unit=unit,
        )
        response = call_sync(
            "device/get_setting_default",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_default_string(
            self,
            setting: str
    ) -> str:
        """
        Returns the default value of a setting as a string.

        Args:
            setting: Name of the setting.

        Returns:
            Default setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/get_setting_default_str",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def get_default_int(
            self,
            setting: str
    ) -> int:
        """
        Returns the default value of a setting as an integer.

        Args:
            setting: Name of the setting.

        Returns:
            Default setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/get_setting_default_int",
            request,
            dto.Int64Response.from_binary)
        return response.value

    def get_default_bool(
            self,
            setting: str
    ) -> bool:
        """
        Returns the default value of a setting as a boolean.

        Args:
            setting: Name of the setting.

        Returns:
            Default setting value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/get_setting_default_bool",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def can_convert_native_units(
            self,
            setting: str
    ) -> bool:
        """
        Indicates if given setting can be converted from and to native units.

        Args:
            setting: Name of the setting.

        Returns:
            True if unit conversion can be performed.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/can_convert_setting",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def has_setting(
            self,
            setting: str
    ) -> bool:
        """
        Indicates whether the specified setting exists on this device.

        Args:
            setting: Name of the setting.

        Returns:
            True if the setting exists on this device.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/has_setting",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_unit_conversion_descriptor(
            self,
            setting: str
    ) -> UnitConversionDescriptor:
        """
        Retrieves unit conversion descriptor for a setting, allowing unit conversion without a device.
        The descriptor can be used with the ConvertTo/FromNativeUnits methods of the UnitTable class.

        Args:
            setting: Name of the setting.

        Returns:
            The unit conversion descriptor for the setting.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call_sync(
            "device/get_setting_unit_conversion",
            request,
            UnitConversionDescriptor.from_binary)
        return response

    def get_from_all_axes(
            self,
            setting: str
    ) -> List[float]:
        """
        Gets the value of an axis scope setting for each axis on the device.
        Values may be NaN where the setting is not applicable.

        Args:
            setting: Name of the setting.

        Returns:
            The setting values on each axis.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = call(
            "device/get_setting_from_all_axes",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    async def get_from_all_axes_async(
            self,
            setting: str
    ) -> List[float]:
        """
        Gets the value of an axis scope setting for each axis on the device.
        Values may be NaN where the setting is not applicable.

        Args:
            setting: Name of the setting.

        Returns:
            The setting values on each axis.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            setting=setting,
        )
        response = await call_async(
            "device/get_setting_from_all_axes",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    def get_many(
            self,
            *settings: GetSetting
    ) -> List[GetSettingResult]:
        """
        Gets many setting values in as few device requests as possible.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = call(
            "device/get_many_settings",
            request,
            dto.GetSettingResults.from_binary)
        return response.results

    async def get_many_async(
            self,
            *settings: GetSetting
    ) -> List[GetSettingResult]:
        """
        Gets many setting values in as few device requests as possible.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = await call_async(
            "device/get_many_settings",
            request,
            dto.GetSettingResults.from_binary)
        return response.results

    def get_many_typed(
            self,
            *settings: GetSetting
    ) -> List[GetSettingTypedResult]:
        """
        Returns many device settings or properties in their native types in as few requests as possible.
        Note that specifying units will always return floating point values,
        even for settings that are natively integers.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = call(
            "device/get_many_settings_typed",
            request,
            dto.GetSettingsTypedResponse.from_binary)
        return response.values

    async def get_many_typed_async(
            self,
            *settings: GetSetting
    ) -> List[GetSettingTypedResult]:
        """
        Returns many device settings or properties in their native types in as few requests as possible.
        Note that specifying units will always return floating point values,
        even for settings that are natively integers.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = await call_async(
            "device/get_many_settings_typed",
            request,
            dto.GetSettingsTypedResponse.from_binary)
        return response.values

    def get_many_by_type(
            self,
            float_settings: List[GetSetting] = [],
            int_settings: List[GetSetting] = [],
            bool_settings: List[GetSetting] = [],
            string_settings: List[GetSetting] = []
    ) -> GetSettingsByTypeResult:
        """
        Gets many settings in as few requests as possible, parsing each as the caller-specified type.
        Unlike GetManyTyped, the type is determined by the caller, not the device database.
        If a value cannot be parsed as the requested type, an error is thrown.

        Args:
            float_settings: Settings to read as float values. Supports unit conversion.
            int_settings: Settings to read as integer values. Unit conversion is not supported.
            bool_settings: Settings to read as boolean values.
            string_settings: Settings to read as string values.

        Returns:
            The setting values grouped by type.
        """
        request = dto.DeviceGetManyByTypeRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            float_settings=float_settings,
            int_settings=int_settings,
            bool_settings=bool_settings,
            string_settings=string_settings,
        )
        response = call(
            "device/get_many_settings_by_type",
            request,
            GetSettingsByTypeResult.from_binary)
        return response

    async def get_many_by_type_async(
            self,
            float_settings: List[GetSetting] = [],
            int_settings: List[GetSetting] = [],
            bool_settings: List[GetSetting] = [],
            string_settings: List[GetSetting] = []
    ) -> GetSettingsByTypeResult:
        """
        Gets many settings in as few requests as possible, parsing each as the caller-specified type.
        Unlike GetManyTyped, the type is determined by the caller, not the device database.
        If a value cannot be parsed as the requested type, an error is thrown.

        Args:
            float_settings: Settings to read as float values. Supports unit conversion.
            int_settings: Settings to read as integer values. Unit conversion is not supported.
            bool_settings: Settings to read as boolean values.
            string_settings: Settings to read as string values.

        Returns:
            The setting values grouped by type.
        """
        request = dto.DeviceGetManyByTypeRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            float_settings=float_settings,
            int_settings=int_settings,
            bool_settings=bool_settings,
            string_settings=string_settings,
        )
        response = await call_async(
            "device/get_many_settings_by_type",
            request,
            GetSettingsByTypeResult.from_binary)
        return response

    def get_synchronized(
            self,
            *settings: GetSetting
    ) -> List[GetSettingResult]:
        """
        Gets many setting values in the same tick, ensuring their values are synchronized.
        Requires at least Firmware 7.35.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = call(
            "device/get_sync_settings",
            request,
            dto.GetSettingResults.from_binary)
        return response.results

    async def get_synchronized_async(
            self,
            *settings: GetSetting
    ) -> List[GetSettingResult]:
        """
        Gets many setting values in the same tick, ensuring their values are synchronized.
        Requires at least Firmware 7.35.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = dto.DeviceMultiGetSettingRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            settings=list(settings),
        )
        response = await call_async(
            "device/get_sync_settings",
            request,
            dto.GetSettingResults.from_binary)
        return response.results
