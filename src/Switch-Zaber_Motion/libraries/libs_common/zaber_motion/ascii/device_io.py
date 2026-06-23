# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.device_io_info import DeviceIOInfo
from ..dto.ascii.digital_output_action import DigitalOutputAction
from ..dto.ascii.io_port_label import IoPortLabel
from ..dto.ascii.io_port_type import IoPortType
from ..units import Units, TimeUnits, FrequencyUnits

if TYPE_CHECKING:
    from .device import Device


class DeviceIO:
    """
    Class providing access to the I/O channels of the device.
    """

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def get_channels_info(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
        )
        response = call(
            "device/get_io_info",
            request,
            DeviceIOInfo.from_binary)
        return response

    async def get_channels_info_async(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
        )
        response = await call_async(
            "device/get_io_info",
            request,
            DeviceIOInfo.from_binary)
        return response

    def set_label(
            self,
            port_type: IoPortType,
            channel_number: int,
            label: Optional[str]
    ) -> None:
        """
        Sets the label of the specified channel.

        Args:
            port_type: The type of channel to set the label of.
            channel_number: Channel number starting at 1.
            label: The label to set for the specified channel.
                If no value or an empty string is provided, this label is deleted.
        """
        request = dto.SetIoPortLabelRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            port_type=port_type,
            channel_number=channel_number,
            label=label,
        )
        call("device/set_io_label", request)

    async def set_label_async(
            self,
            port_type: IoPortType,
            channel_number: int,
            label: Optional[str]
    ) -> None:
        """
        Sets the label of the specified channel.

        Args:
            port_type: The type of channel to set the label of.
            channel_number: Channel number starting at 1.
            label: The label to set for the specified channel.
                If no value or an empty string is provided, this label is deleted.
        """
        request = dto.SetIoPortLabelRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            port_type=port_type,
            channel_number=channel_number,
            label=label,
        )
        await call_async("device/set_io_label", request)

    def get_label(
            self,
            port_type: IoPortType,
            channel_number: int
    ) -> str:
        """
        Returns the label of the specified channel.

        Args:
            port_type: The type of channel to get the label of.
            channel_number: Channel number starting at 1.

        Returns:
            The label of the specified channel.
        """
        request = dto.GetIoPortLabelRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            port_type=port_type,
            channel_number=channel_number,
        )
        response = call(
            "device/get_io_label",
            request,
            dto.StringResponse.from_binary)
        return response.value

    async def get_label_async(
            self,
            port_type: IoPortType,
            channel_number: int
    ) -> str:
        """
        Returns the label of the specified channel.

        Args:
            port_type: The type of channel to get the label of.
            channel_number: Channel number starting at 1.

        Returns:
            The label of the specified channel.
        """
        request = dto.GetIoPortLabelRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            port_type=port_type,
            channel_number=channel_number,
        )
        response = await call_async(
            "device/get_io_label",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def get_all_labels(
            self
    ) -> List[IoPortLabel]:
        """
        Returns every label assigned to an IO port on this device.

        Returns:
            The labels set for this device's IO.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
        )
        response = call(
            "device/get_all_io_labels",
            request,
            dto.GetAllIoPortLabelsResponse.from_binary)
        return response.labels

    async def get_all_labels_async(
            self
    ) -> List[IoPortLabel]:
        """
        Returns every label assigned to an IO port on this device.

        Returns:
            The labels set for this device's IO.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
        )
        response = await call_async(
            "device/get_all_io_labels",
            request,
            dto.GetAllIoPortLabelsResponse.from_binary)
        return response.labels

    def get_digital_input(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = dto.DeviceGetDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="di",
            channel_number=channel_number,
        )
        response = call(
            "device/get_digital_io",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def get_digital_input_async(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = dto.DeviceGetDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="di",
            channel_number=channel_number,
        )
        response = await call_async(
            "device/get_digital_io",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_digital_output(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = dto.DeviceGetDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="do",
            channel_number=channel_number,
        )
        response = call(
            "device/get_digital_io",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def get_digital_output_async(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = dto.DeviceGetDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="do",
            channel_number=channel_number,
        )
        response = await call_async(
            "device/get_digital_io",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_analog_input(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current value of the specified analog input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
             A measurement of the voltage present on the input channel.
        """
        request = dto.DeviceGetAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ai",
            channel_number=channel_number,
        )
        response = call(
            "device/get_analog_io",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_analog_input_async(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current value of the specified analog input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
             A measurement of the voltage present on the input channel.
        """
        request = dto.DeviceGetAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ai",
            channel_number=channel_number,
        )
        response = await call_async(
            "device/get_analog_io",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_analog_output(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current values of the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            A measurement of voltage that the output channel is conducting.
        """
        request = dto.DeviceGetAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ao",
            channel_number=channel_number,
        )
        response = call(
            "device/get_analog_io",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_analog_output_async(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current values of the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            A measurement of voltage that the output channel is conducting.
        """
        request = dto.DeviceGetAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ao",
            channel_number=channel_number,
        )
        response = await call_async(
            "device/get_analog_io",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_all_digital_inputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = dto.DeviceGetAllDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="di",
        )
        response = call(
            "device/get_all_digital_io",
            request,
            dto.DeviceGetAllDigitalIOResponse.from_binary)
        return response.values

    async def get_all_digital_inputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = dto.DeviceGetAllDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="di",
        )
        response = await call_async(
            "device/get_all_digital_io",
            request,
            dto.DeviceGetAllDigitalIOResponse.from_binary)
        return response.values

    def get_all_digital_outputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = dto.DeviceGetAllDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="do",
        )
        response = call(
            "device/get_all_digital_io",
            request,
            dto.DeviceGetAllDigitalIOResponse.from_binary)
        return response.values

    async def get_all_digital_outputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = dto.DeviceGetAllDigitalIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="do",
        )
        response = await call_async(
            "device/get_all_digital_io",
            request,
            dto.DeviceGetAllDigitalIOResponse.from_binary)
        return response.values

    def get_all_analog_inputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
            Measurements of the voltages present on the input channels.
        """
        request = dto.DeviceGetAllAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ai",
        )
        response = call(
            "device/get_all_analog_io",
            request,
            dto.DeviceGetAllAnalogIOResponse.from_binary)
        return response.values

    async def get_all_analog_inputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
            Measurements of the voltages present on the input channels.
        """
        request = dto.DeviceGetAllAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ai",
        )
        response = await call_async(
            "device/get_all_analog_io",
            request,
            dto.DeviceGetAllAnalogIOResponse.from_binary)
        return response.values

    def get_all_analog_outputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
            Measurements of voltage that the output channels are conducting.
        """
        request = dto.DeviceGetAllAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ao",
        )
        response = call(
            "device/get_all_analog_io",
            request,
            dto.DeviceGetAllAnalogIOResponse.from_binary)
        return response.values

    async def get_all_analog_outputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
            Measurements of voltage that the output channels are conducting.
        """
        request = dto.DeviceGetAllAnalogIORequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_type="ao",
        )
        response = await call_async(
            "device/get_all_analog_io",
            request,
            dto.DeviceGetAllAnalogIOResponse.from_binary)
        return response.values

    def set_digital_output(
            self,
            channel_number: int,
            value: DigitalOutputAction
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform on the channel.
        """
        request = dto.DeviceSetDigitalOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
        )
        call("device/set_digital_output", request)

    async def set_digital_output_async(
            self,
            channel_number: int,
            value: DigitalOutputAction
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform on the channel.
        """
        request = dto.DeviceSetDigitalOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
        )
        await call_async("device/set_digital_output", request)

    def set_all_digital_outputs(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = dto.DeviceSetAllDigitalOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
        )
        call("device/set_all_digital_outputs", request)

    async def set_all_digital_outputs_async(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = dto.DeviceSetAllDigitalOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
        )
        await call_async("device/set_all_digital_outputs", request)

    def set_digital_output_schedule(
            self,
            channel_number: int,
            value: DigitalOutputAction,
            future_value: DigitalOutputAction,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified digital output channel.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform immediately on the channel.
            future_value: The type of action to perform in the future on the channel.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetDigitalOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        call("device/set_digital_output_schedule", request)

    async def set_digital_output_schedule_async(
            self,
            channel_number: int,
            value: DigitalOutputAction,
            future_value: DigitalOutputAction,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified digital output channel.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform immediately on the channel.
            future_value: The type of action to perform in the future on the channel.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetDigitalOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        await call_async("device/set_digital_output_schedule", request)

    def set_all_digital_outputs_schedule(
            self,
            values: List[DigitalOutputAction],
            future_values: List[DigitalOutputAction],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future values for all digital output channels.
        Requires at least Firmware 7.37.

        Args:
            values: The type of actions to perform immediately on output channels.
            future_values: The type of actions to perform in the future on output channels.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAllDigitalOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        call("device/set_all_digital_outputs_schedule", request)

    async def set_all_digital_outputs_schedule_async(
            self,
            values: List[DigitalOutputAction],
            future_values: List[DigitalOutputAction],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future values for all digital output channels.
        Requires at least Firmware 7.37.

        Args:
            values: The type of actions to perform immediately on output channels.
            future_values: The type of actions to perform in the future on output channels.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAllDigitalOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        await call_async("device/set_all_digital_outputs_schedule", request)

    def set_analog_output(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Sets value for the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to.
        """
        request = dto.DeviceSetAnalogOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
        )
        call("device/set_analog_output", request)

    async def set_analog_output_async(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Sets value for the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to.
        """
        request = dto.DeviceSetAnalogOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
        )
        await call_async("device/set_analog_output", request)

    def set_all_analog_outputs(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = dto.DeviceSetAllAnalogOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
        )
        call("device/set_all_analog_outputs", request)

    async def set_all_analog_outputs_async(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = dto.DeviceSetAllAnalogOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
        )
        await call_async("device/set_all_analog_outputs", request)

    def set_analog_output_schedule(
            self,
            channel_number: int,
            value: float,
            future_value: float,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified analog output channel.
        Requires at least Firmware 7.38.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to immediately.
            future_value: Value to set the output channel voltage to in the future.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAnalogOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        call("device/set_analog_output_schedule", request)

    async def set_analog_output_schedule_async(
            self,
            channel_number: int,
            value: float,
            future_value: float,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified analog output channel.
        Requires at least Firmware 7.38.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to immediately.
            future_value: Value to set the output channel voltage to in the future.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAnalogOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        await call_async("device/set_analog_output_schedule", request)

    def set_all_analog_outputs_schedule(
            self,
            values: List[float],
            future_values: List[float],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future values for all analog output channels.
        Requires at least Firmware 7.38.

        Args:
            values: Voltage values to set the output channels to immediately.
            future_values: Voltage values to set the output channels to in the future.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAllAnalogOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        call("device/set_all_analog_outputs_schedule", request)

    async def set_all_analog_outputs_schedule_async(
            self,
            values: List[float],
            future_values: List[float],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future values for all analog output channels.
        Requires at least Firmware 7.38.

        Args:
            values: Voltage values to set the output channels to immediately.
            future_values: Voltage values to set the output channels to in the future.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = dto.DeviceSetAllAnalogOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        await call_async("device/set_all_analog_outputs_schedule", request)

    def set_analog_input_lowpass_filter(
            self,
            channel_number: int,
            cutoff_frequency: float,
            unit: FrequencyUnits = Units.NATIVE
    ) -> None:
        """
        Sets the cutoff frequency of the low-pass filter for the specified analog input channel.
        Set the frequency to 0 to disable the filter.

        Args:
            channel_number: Channel number starting at 1.
            cutoff_frequency: Cutoff frequency of the low-pass filter.
            unit: Units of frequency.
        """
        request = dto.DeviceSetLowpassFilterRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            cutoff_frequency=cutoff_frequency,
            unit=unit,
        )
        call("device/set_lowpass_filter", request)

    async def set_analog_input_lowpass_filter_async(
            self,
            channel_number: int,
            cutoff_frequency: float,
            unit: FrequencyUnits = Units.NATIVE
    ) -> None:
        """
        Sets the cutoff frequency of the low-pass filter for the specified analog input channel.
        Set the frequency to 0 to disable the filter.

        Args:
            channel_number: Channel number starting at 1.
            cutoff_frequency: Cutoff frequency of the low-pass filter.
            unit: Units of frequency.
        """
        request = dto.DeviceSetLowpassFilterRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            channel_number=channel_number,
            cutoff_frequency=cutoff_frequency,
            unit=unit,
        )
        await call_async("device/set_lowpass_filter", request)

    def cancel_digital_output_schedule(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled digital output action.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = dto.DeviceCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            channel_number=channel_number,
        )
        call("device/cancel_output_schedule", request)

    async def cancel_digital_output_schedule_async(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled digital output action.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = dto.DeviceCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            channel_number=channel_number,
        )
        await call_async("device/cancel_output_schedule", request)

    def cancel_all_digital_outputs_schedule(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled digital output actions.
        Requires at least Firmware 7.37.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled digital output action for that channel.
        """
        request = dto.DeviceCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            channels=channels,
        )
        call("device/cancel_all_outputs_schedule", request)

    async def cancel_all_digital_outputs_schedule_async(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled digital output actions.
        Requires at least Firmware 7.37.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled digital output action for that channel.
        """
        request = dto.DeviceCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            channels=channels,
        )
        await call_async("device/cancel_all_outputs_schedule", request)

    def cancel_analog_output_schedule(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled analog output value.
        Requires at least Firmware 7.38.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = dto.DeviceCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            channel_number=channel_number,
        )
        call("device/cancel_output_schedule", request)

    async def cancel_analog_output_schedule_async(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled analog output value.
        Requires at least Firmware 7.38.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = dto.DeviceCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            channel_number=channel_number,
        )
        await call_async("device/cancel_output_schedule", request)

    def cancel_all_analog_outputs_schedule(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled analog output actions.
        Requires at least Firmware 7.38.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled analog output value for that channel.
        """
        request = dto.DeviceCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            channels=channels,
        )
        call("device/cancel_all_outputs_schedule", request)

    async def cancel_all_analog_outputs_schedule_async(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled analog output actions.
        Requires at least Firmware 7.38.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled analog output value for that channel.
        """
        request = dto.DeviceCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            channels=channels,
        )
        await call_async("device/cancel_all_outputs_schedule", request)
