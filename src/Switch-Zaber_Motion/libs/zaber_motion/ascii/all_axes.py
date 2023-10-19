# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class AllAxes:
    """
    Represents all axes of motion associated with a device.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this axis.
        """
        return self._device

    def __init__(self, device: 'Device'):
        self._device = device

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes all axes. Axes return to their homing positions.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.wait_until_idle = wait_until_idle
        call("device/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes all axes. Axes return to their homing positions.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.wait_until_idle = wait_until_idle
        await call_async("device/home", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axes movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.wait_until_idle = wait_until_idle
        call("device/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axes movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.wait_until_idle = wait_until_idle
        await call_async("device/stop", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until all axes of device stop moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.throw_error_on_fault = throw_error_on_fault
        call("device/wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until all axes of device stop moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        request.throw_error_on_fault = throw_error_on_fault
        await call_async("device/wait_until_idle", request)

    def park(
            self
    ) -> None:
        """
        Parks the device in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = main_pb2.DeviceParkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        call("device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the device in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = main_pb2.DeviceParkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        await call_async("device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks the device. The device will now be able to move.
        """
        request = main_pb2.DeviceParkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        call("device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks the device. The device will now be able to move.
        """
        request = main_pb2.DeviceParkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        await call_async("device/unpark", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether any axis is executing a motion command.

        Returns:
            True if any axis is currently executing a motion command.
        """
        request = main_pb2.DeviceIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        response = main_pb2.DeviceIsBusyResponse()
        call("device/is_busy", request, response)
        return response.is_busy

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether any axis is executing a motion command.

        Returns:
            True if any axis is currently executing a motion command.
        """
        request = main_pb2.DeviceIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        response = main_pb2.DeviceIsBusyResponse()
        await call_async("device/is_busy", request, response)
        return response.is_busy

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axes.

        Returns:
            A string that represents the axes.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 0
        response = main_pb2.ToStringResponse()
        call_sync("device/all_axes_to_string", request, response)
        return response.to_str
