# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.io_port_type import IoPortType
from ..units import Units, TimeUnits, FrequencyUnits
from .oscilloscope_data import OscilloscopeData

if TYPE_CHECKING:
    from .device import Device


class Oscilloscope:
    """
    Provides a convenient way to control the oscilloscope data recording feature of some devices.
    The oscilloscope can record the values of some settings over time at high resolution.
    Requires at least Firmware 7.00.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that this Oscilloscope measures.
        """
        return self._device

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def add_channel(
            self,
            axis: int,
            setting: str
    ) -> None:
        """
        Select a setting to be recorded.

        Args:
            axis: The 1-based index of the axis to record the value from.
            setting: The name of a setting to record.
        """
        request = dto.OscilloscopeAddSettingChannelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=axis,
            setting=setting,
        )
        call("oscilloscope/add_setting_channel", request)

    async def add_channel_async(
            self,
            axis: int,
            setting: str
    ) -> None:
        """
        Select a setting to be recorded.

        Args:
            axis: The 1-based index of the axis to record the value from.
            setting: The name of a setting to record.
        """
        request = dto.OscilloscopeAddSettingChannelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=axis,
            setting=setting,
        )
        await call_async("oscilloscope/add_setting_channel", request)

    def add_io_channel(
            self,
            io_type: IoPortType,
            io_channel: int
    ) -> None:
        """
        Select an I/O pin to be recorded.
        Requires at least Firmware 7.33.

        Args:
            io_type: The I/O port type to read data from.
            io_channel: The 1-based index of the I/O pin to read from.
        """
        request = dto.OscilloscopeAddIoChannelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            io_type=io_type,
            io_channel=io_channel,
        )
        call("oscilloscope/add_io_channel", request)

    async def add_io_channel_async(
            self,
            io_type: IoPortType,
            io_channel: int
    ) -> None:
        """
        Select an I/O pin to be recorded.
        Requires at least Firmware 7.33.

        Args:
            io_type: The I/O port type to read data from.
            io_channel: The 1-based index of the I/O pin to read from.
        """
        request = dto.OscilloscopeAddIoChannelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            io_type=io_type,
            io_channel=io_channel,
        )
        await call_async("oscilloscope/add_io_channel", request)

    def clear(
            self
    ) -> None:
        """
        Clear the list of channels to record.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        call("oscilloscope/clear_channels", request)

    async def clear_async(
            self
    ) -> None:
        """
        Clear the list of channels to record.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        await call_async("oscilloscope/clear_channels", request)

    def get_timebase(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the current sampling interval.

        Args:
            unit: Unit of measure to represent the timebase in.

        Returns:
            The current sampling interval in the selected time units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_timebase_async(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the current sampling interval.

        Args:
            unit: Unit of measure to represent the timebase in.

        Returns:
            The current sampling interval in the selected time units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_timebase(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling interval.

        Args:
            interval: Sample interval for the next oscilloscope recording. Minimum value is 100µs.
            unit: Unit of measure the timebase is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            value=interval,
            unit=unit,
        )
        call("device/set_setting", request)

    async def set_timebase_async(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling interval.

        Args:
            interval: Sample interval for the next oscilloscope recording. Minimum value is 100µs.
            unit: Unit of measure the timebase is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            value=interval,
            unit=unit,
        )
        await call_async("device/set_setting", request)

    def get_frequency(
            self,
            unit: FrequencyUnits = Units.NATIVE
    ) -> float:
        """
        Get the current sampling frequency.
        The values is calculated as the inverse of the current sampling interval.

        Args:
            unit: Unit of measure to represent the frequency in.

        Returns:
            The inverse of current sampling interval in the selected units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            unit=unit,
        )
        response = call(
            "oscilloscope/get_frequency",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_frequency_async(
            self,
            unit: FrequencyUnits = Units.NATIVE
    ) -> float:
        """
        Get the current sampling frequency.
        The values is calculated as the inverse of the current sampling interval.

        Args:
            unit: Unit of measure to represent the frequency in.

        Returns:
            The inverse of current sampling interval in the selected units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            unit=unit,
        )
        response = await call_async(
            "oscilloscope/get_frequency",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_frequency(
            self,
            frequency: float,
            unit: FrequencyUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling frequency (inverse of the sampling interval).
        The value is quantized to the next closest value supported by the firmware.

        Args:
            frequency: Sample frequency for the next oscilloscope recording.
            unit: Unit of measure the frequency is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            value=frequency,
            unit=unit,
        )
        call("oscilloscope/set_frequency", request)

    async def set_frequency_async(
            self,
            frequency: float,
            unit: FrequencyUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling frequency (inverse of the sampling interval).
        The value is quantized to the next closest value supported by the firmware.

        Args:
            frequency: Sample frequency for the next oscilloscope recording.
            unit: Unit of measure the frequency is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.timebase",
            value=frequency,
            unit=unit,
        )
        await call_async("oscilloscope/set_frequency", request)

    def get_delay(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the delay before oscilloscope recording starts.

        Args:
            unit: Unit of measure to represent the delay in.

        Returns:
            The current start delay in the selected time units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.delay",
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_delay_async(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the delay before oscilloscope recording starts.

        Args:
            unit: Unit of measure to represent the delay in.

        Returns:
            The current start delay in the selected time units.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.delay",
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_delay(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling start delay.

        Args:
            interval: Delay time between triggering a recording and the first data point being recorded.
            unit: Unit of measure the delay is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.delay",
            value=interval,
            unit=unit,
        )
        call("device/set_setting", request)

    async def set_delay_async(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set the sampling start delay.

        Args:
            interval: Delay time between triggering a recording and the first data point being recorded.
            unit: Unit of measure the delay is represented in.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.delay",
            value=interval,
            unit=unit,
        )
        await call_async("device/set_setting", request)

    def get_max_channels(
            self
    ) -> int:
        """
        Get the maximum number of channels that can be recorded.

        Returns:
            The maximum number of channels that can be added to an Oscilloscope recording.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.numchannels",
        )
        response = call(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_max_channels_async(
            self
    ) -> int:
        """
        Get the maximum number of channels that can be recorded.

        Returns:
            The maximum number of channels that can be added to an Oscilloscope recording.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.numchannels",
        )
        response = await call_async(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_max_buffer_size(
            self
    ) -> int:
        """
        Get the maximum number of samples that can be recorded per Oscilloscope channel.

        Returns:
            The maximum number of samples that can be recorded per Oscilloscope channel.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.channel.size.max",
        )
        response = call(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_max_buffer_size_async(
            self
    ) -> int:
        """
        Get the maximum number of samples that can be recorded per Oscilloscope channel.

        Returns:
            The maximum number of samples that can be recorded per Oscilloscope channel.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.channel.size.max",
        )
        response = await call_async(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_buffer_size(
            self
    ) -> int:
        """
        Get the number of samples that can be recorded per channel given the current number of channels added.

        Returns:
            Number of samples that will be recorded per channel with the current channels. Zero if none have been added.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.channel.size",
        )
        response = call(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_buffer_size_async(
            self
    ) -> int:
        """
        Get the number of samples that can be recorded per channel given the current number of channels added.

        Returns:
            Number of samples that will be recorded per channel with the current channels. Zero if none have been added.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="scope.channel.size",
        )
        response = await call_async(
            "oscilloscope/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def start(
            self,
            capture_length: int = 0
    ) -> None:
        """
        Trigger data recording.

        Args:
            capture_length: Optional number of samples to record per channel.
                If left empty, the device records samples until the buffer fills.
                Requires at least Firmware 7.29.
        """
        request = dto.OscilloscopeStartRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            capture_length=capture_length,
        )
        call("oscilloscope/start", request)

    async def start_async(
            self,
            capture_length: int = 0
    ) -> None:
        """
        Trigger data recording.

        Args:
            capture_length: Optional number of samples to record per channel.
                If left empty, the device records samples until the buffer fills.
                Requires at least Firmware 7.29.
        """
        request = dto.OscilloscopeStartRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            capture_length=capture_length,
        )
        await call_async("oscilloscope/start", request)

    def stop(
            self
    ) -> None:
        """
        End data recording if currently in progress.
        """
        request = dto.OscilloscopeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        call("oscilloscope/stop", request)

    async def stop_async(
            self
    ) -> None:
        """
        End data recording if currently in progress.
        """
        request = dto.OscilloscopeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        await call_async("oscilloscope/stop", request)

    def read(
            self
    ) -> List[OscilloscopeData]:
        """
        Reads the last-recorded data from the oscilloscope. Will block until any in-progress recording completes.

        Returns:
            Array of recorded channel data arrays, in the order added.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = call(
            "oscilloscope/read",
            request,
            dto.OscilloscopeReadResponse.from_binary)
        return list(map(OscilloscopeData, response.data_ids))

    async def read_async(
            self
    ) -> List[OscilloscopeData]:
        """
        Reads the last-recorded data from the oscilloscope. Will block until any in-progress recording completes.

        Returns:
            Array of recorded channel data arrays, in the order added.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = await call_async(
            "oscilloscope/read",
            request,
            dto.OscilloscopeReadResponse.from_binary)
        return list(map(OscilloscopeData, response.data_ids))
