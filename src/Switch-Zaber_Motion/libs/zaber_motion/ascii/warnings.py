# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Set
from ..call import call, call_async

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class Warnings:
    """
    Class used to check and reset warnings and faults on device or axis.
    """

    def __init__(self, device: 'Device', axis_number: int):
        self._device = device
        self._axis_number = axis_number

    def get_flags(
            self
    ) -> Set[str]:
        """
        Returns current warnings and faults on axis or device.

        Returns:
            Retrieved warnings and faults. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = False
        response = main_pb2.DeviceGetWarningsResponse()
        call("device/get_warnings", request, response)
        return set(response.flags)

    async def get_flags_async(
            self
    ) -> Set[str]:
        """
        Returns current warnings and faults on axis or device.

        Returns:
            Retrieved warnings and faults. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = False
        response = main_pb2.DeviceGetWarningsResponse()
        await call_async("device/get_warnings", request, response)
        return set(response.flags)

    def clear_flags(
            self
    ) -> Set[str]:
        """
        Clears (acknowledges) current warnings and faults on axis or device and returns them.

        Returns:
            Warnings and faults before clearing. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = True
        response = main_pb2.DeviceGetWarningsResponse()
        call("device/get_warnings", request, response)
        return set(response.flags)

    async def clear_flags_async(
            self
    ) -> Set[str]:
        """
        Clears (acknowledges) current warnings and faults on axis or device and returns them.

        Returns:
            Warnings and faults before clearing. Refer to WarningFlags to check a particular flag.
        """
        request = main_pb2.DeviceGetWarningsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.axis = self._axis_number
        request.clear = True
        response = main_pb2.DeviceGetWarningsResponse()
        await call_async("device/get_warnings", request, response)
        return set(response.flags)
