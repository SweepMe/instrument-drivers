# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from .device_io_info import DeviceIOInfo

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class DeviceIO:
    """
    Class providing access to the I/O channels of the device.
    """

    def __init__(self, device: 'Device'):
        self._device = device

    def get_all_digital_inputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        call("device/get_all_digital_io", request, response)
        return list(response.values)

    async def get_all_digital_inputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        await call_async("device/get_all_digital_io", request, response)
        return list(response.values)

    def get_all_digital_outputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        call("device/get_all_digital_io", request, response)
        return list(response.values)

    async def get_all_digital_outputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        await call_async("device/get_all_digital_io", request, response)
        return list(response.values)

    def get_all_analog_inputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
             Measurements of the voltage present on the input channels.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        call("device/get_all_analog_io", request, response)
        return list(response.values)

    async def get_all_analog_inputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
             Measurements of the voltage present on the input channels.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        await call_async("device/get_all_analog_io", request, response)
        return list(response.values)

    def get_all_analog_outputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
             Measurements of voltage that the output channels are conducting.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        call("device/get_all_analog_io", request, response)
        return list(response.values)

    async def get_all_analog_outputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
             Measurements of voltage that the output channels are conducting.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        await call_async("device/get_all_analog_io", request, response)
        return list(response.values)

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
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetDigitalIOResponse()
        call("device/get_digital_io", request, response)
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
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetDigitalIOResponse()
        await call_async("device/get_digital_io", request, response)
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
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetDigitalIOResponse()
        call("device/get_digital_io", request, response)
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
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetDigitalIOResponse()
        await call_async("device/get_digital_io", request, response)
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
             A measurementsof the voltage present on the input channel.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetAnalogIOResponse()
        call("device/get_analog_io", request, response)
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
             A measurementsof the voltage present on the input channel.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetAnalogIOResponse()
        await call_async("device/get_analog_io", request, response)
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
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetAnalogIOResponse()
        call("device/get_analog_io", request, response)
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
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        request.channel_number = channel_number
        response = main_pb2.DeviceGetAnalogIOResponse()
        await call_async("device/get_analog_io", request, response)
        return response.value

    def set_all_digital_outputs(
            self,
            values: List[bool]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.DeviceSetAllDigitalOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
        call("device/set_all_digital_outputs", request)

    async def set_all_digital_outputs_async(
            self,
            values: List[bool]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.DeviceSetAllDigitalOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
        await call_async("device/set_all_digital_outputs", request)

    def set_all_analog_outputs(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = main_pb2.DeviceSetAllAnalogOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
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
        request = main_pb2.DeviceSetAllAnalogOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
        await call_async("device/set_all_analog_outputs", request)

    def set_digital_output(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.DeviceSetDigitalOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
        call("device/set_digital_output", request)

    async def set_digital_output_async(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: True to set the output channel to conducting and false to turn it off.
        """
        request = main_pb2.DeviceSetDigitalOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
        await call_async("device/set_digital_output", request)

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
        request = main_pb2.DeviceSetAnalogOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
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
        request = main_pb2.DeviceSetAnalogOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
        await call_async("device/set_analog_output", request)

    def get_channels_info(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = main_pb2.DeviceGetIOChannelsInfoRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        response = main_pb2.DeviceIOInfo()
        call("device/get_io_info", request, response)
        return DeviceIOInfo.from_protobuf(response)

    async def get_channels_info_async(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = main_pb2.DeviceGetIOChannelsInfoRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        response = main_pb2.DeviceIOInfo()
        await call_async("device/get_io_info", request, response)
        return DeviceIOInfo.from_protobuf(response)
