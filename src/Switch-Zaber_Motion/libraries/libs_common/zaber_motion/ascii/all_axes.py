# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from ..call import call, call_async, call_sync
from ..dto import requests as dto

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
        self._device: 'Device' = device

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes all axes. Axes return to their homing positions.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.DeviceHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            wait_until_idle=wait_until_idle,
        )
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
        request = dto.DeviceHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            wait_until_idle=wait_until_idle,
        )
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
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            wait_until_idle=wait_until_idle,
        )
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
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            wait_until_idle=wait_until_idle,
        )
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
        request = dto.DeviceWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            throw_error_on_fault=throw_error_on_fault,
        )
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
        request = dto.DeviceWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("device/wait_until_idle", request)

    def park(
            self
    ) -> None:
        """
        Parks the device in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        call("device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the device in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        await call_async("device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks the device. The device will now be able to move.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        call("device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks the device. The device will now be able to move.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        await call_async("device/unpark", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether any axis is executing a motion command.

        Returns:
            True if any axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        response = call(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether any axis is executing a motion command.

        Returns:
            True if any axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        response = await call_async(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def is_homed(
            self
    ) -> bool:
        """
        Returns bool indicating whether all axes have position reference and were homed.

        Returns:
            True if all axes have position reference and were homed.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        response = call(
            "device/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_homed_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether all axes have position reference and were homed.

        Returns:
            True if all axes have position reference and were homed.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        response = await call_async(
            "device/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def driver_disable(
            self
    ) -> None:
        """
        Disables all axes drivers, which prevents current from being sent to the motor or load.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        call("device/driver_disable", request)

    async def driver_disable_async(
            self
    ) -> None:
        """
        Disables all axes drivers, which prevents current from being sent to the motor or load.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        await call_async("device/driver_disable", request)

    def driver_enable(
            self,
            timeout: float = 10
    ) -> None:
        """
        Attempts to enable all axes drivers (where applicable) repeatedly for the specified timeout.
        If the driver is already enabled, the driver remains enabled.

        Args:
            timeout: Timeout in seconds. Specify 0 to attempt to enable the driver once.
        """
        request = dto.DriverEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            timeout=timeout,
        )
        call("device/driver_enable", request)

    async def driver_enable_async(
            self,
            timeout: float = 10
    ) -> None:
        """
        Attempts to enable all axes drivers (where applicable) repeatedly for the specified timeout.
        If the driver is already enabled, the driver remains enabled.

        Args:
            timeout: Timeout in seconds. Specify 0 to attempt to enable the driver once.
        """
        request = dto.DriverEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
            timeout=timeout,
        )
        await call_async("device/driver_enable", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axes.

        Returns:
            A string that represents the axes.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=0,
        )
        response = call_sync(
            "device/all_axes_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
