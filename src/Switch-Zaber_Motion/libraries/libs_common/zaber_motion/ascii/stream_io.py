# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.digital_output_action import DigitalOutputAction
from ..units import Units, TimeUnits

if TYPE_CHECKING:
    from .device import Device


class StreamIo:
    """
    Class providing access to I/O for a stream.
    """

    def __init__(self, device: 'Device', stream_id: int):
        self._device: 'Device' = device
        self._stream_id: int = stream_id

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
        request = dto.StreamSetDigitalOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        call("device/stream_set_digital_output", request)

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
        request = dto.StreamSetDigitalOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        await call_async("device/stream_set_digital_output", request)

    def set_all_digital_outputs(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = dto.StreamSetAllDigitalOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
        )
        call("device/stream_set_all_digital_outputs", request)

    async def set_all_digital_outputs_async(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = dto.StreamSetAllDigitalOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
        )
        await call_async("device/stream_set_all_digital_outputs", request)

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

        request = dto.StreamSetDigitalOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        call("device/stream_set_digital_output_schedule", request)

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

        request = dto.StreamSetDigitalOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        await call_async("device/stream_set_digital_output_schedule", request)

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

        request = dto.StreamSetAllDigitalOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        call("device/stream_set_all_digital_outputs_schedule", request)

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

        request = dto.StreamSetAllDigitalOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        await call_async("device/stream_set_all_digital_outputs_schedule", request)

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
        request = dto.StreamSetAnalogOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        call("device/stream_set_analog_output", request)

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
        request = dto.StreamSetAnalogOutputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        await call_async("device/stream_set_analog_output", request)

    def set_all_analog_outputs(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = dto.StreamSetAllAnalogOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
        )
        call("device/stream_set_all_analog_outputs", request)

    async def set_all_analog_outputs_async(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = dto.StreamSetAllAnalogOutputsRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
        )
        await call_async("device/stream_set_all_analog_outputs", request)

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

        request = dto.StreamSetAnalogOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        call("device/stream_set_analog_output_schedule", request)

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

        request = dto.StreamSetAnalogOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
            future_value=future_value,
            delay=delay,
            unit=unit,
        )
        await call_async("device/stream_set_analog_output_schedule", request)

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

        request = dto.StreamSetAllAnalogOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        call("device/stream_set_all_analog_outputs_schedule", request)

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

        request = dto.StreamSetAllAnalogOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            values=values,
            future_values=future_values,
            delay=delay,
            unit=unit,
        )
        await call_async("device/stream_set_all_analog_outputs_schedule", request)

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
        request = dto.StreamCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            stream_id=self._stream_id,
            channel_number=channel_number,
        )
        call("device/stream_cancel_output_schedule", request)

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
        request = dto.StreamCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            stream_id=self._stream_id,
            channel_number=channel_number,
        )
        await call_async("device/stream_cancel_output_schedule", request)

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
        request = dto.StreamCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            stream_id=self._stream_id,
            channels=channels,
        )
        call("device/stream_cancel_all_outputs_schedule", request)

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
        request = dto.StreamCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=False,
            stream_id=self._stream_id,
            channels=channels,
        )
        await call_async("device/stream_cancel_all_outputs_schedule", request)

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
        request = dto.StreamCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            stream_id=self._stream_id,
            channel_number=channel_number,
        )
        call("device/stream_cancel_output_schedule", request)

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
        request = dto.StreamCancelOutputScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            stream_id=self._stream_id,
            channel_number=channel_number,
        )
        await call_async("device/stream_cancel_output_schedule", request)

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
        request = dto.StreamCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            stream_id=self._stream_id,
            channels=channels,
        )
        call("device/stream_cancel_all_outputs_schedule", request)

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
        request = dto.StreamCancelAllOutputsScheduleRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            analog=True,
            stream_id=self._stream_id,
            channels=channels,
        )
        await call_async("device/stream_cancel_all_outputs_schedule", request)

    def wait_digital_input(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Wait for a digital input channel to reach a given value.

        Args:
            channel_number: The number of the digital input channel.
                Channel numbers are numbered from one.
            value: The value that the stream should wait for.
        """
        request = dto.StreamWaitDigitalInputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        call("device/stream_wait_digital_input", request)

    async def wait_digital_input_async(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Wait for a digital input channel to reach a given value.

        Args:
            channel_number: The number of the digital input channel.
                Channel numbers are numbered from one.
            value: The value that the stream should wait for.
        """
        request = dto.StreamWaitDigitalInputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            value=value,
        )
        await call_async("device/stream_wait_digital_input", request)

    def wait_analog_input(
            self,
            channel_number: int,
            condition: str,
            value: float
    ) -> None:
        """
        Wait for the value of a analog input channel to reach a condition concerning a given value.

        Args:
            channel_number: The number of the analog input channel.
                Channel numbers are numbered from one.
            condition: A condition (e.g. <, <=, ==, !=).
            value: The value that the condition concerns, in Volts.
        """
        request = dto.StreamWaitAnalogInputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            condition=condition,
            value=value,
        )
        call("device/stream_wait_analog_input", request)

    async def wait_analog_input_async(
            self,
            channel_number: int,
            condition: str,
            value: float
    ) -> None:
        """
        Wait for the value of a analog input channel to reach a condition concerning a given value.

        Args:
            channel_number: The number of the analog input channel.
                Channel numbers are numbered from one.
            condition: A condition (e.g. <, <=, ==, !=).
            value: The value that the condition concerns, in Volts.
        """
        request = dto.StreamWaitAnalogInputRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            stream_id=self._stream_id,
            channel_number=channel_number,
            condition=condition,
            value=value,
        )
        await call_async("device/stream_wait_analog_input", request)
