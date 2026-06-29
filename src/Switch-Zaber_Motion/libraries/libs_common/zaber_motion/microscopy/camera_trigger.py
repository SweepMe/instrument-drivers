# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0622

from ..ascii import Device
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..units import TimeUnits, Units


class CameraTrigger:
    """
    An abstraction over a device and it's digital output channel.
    """

    @property
    def device(self) -> Device:
        """
        The device whose digital output triggers the camera.
        """
        return self._device

    @property
    def channel(self) -> int:
        """
        The digital output channel that triggers the camera.
        """
        return self._channel

    def __init__(self, device: Device, channel: int):
        """
        Creates instance of `CameraTrigger` based on the given device and digital output channel.
        """
        self._device: Device = device
        self._channel: int = channel

    def trigger(
            self,
            pulse_width: float,
            unit: TimeUnits = Units.NATIVE,
            wait: bool = True
    ) -> None:
        """
        Triggers the camera.
        Schedules trigger pulse on the digital output channel.
        By default, the method waits until the trigger pulse is finished.

        Args:
            pulse_width: The time duration of the trigger pulse.
                Depending on the camera setting, the argument can be use to specify exposure.
            unit: Units of time.
            wait: If false, the method does not wait until the trigger pulse is finished.
        """
        request = dto.MicroscopeTriggerCameraRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            channel_number=self.channel,
            delay=pulse_width,
            unit=unit,
            wait=wait,
        )
        call("microscope/trigger_camera", request)

    async def trigger_async(
            self,
            pulse_width: float,
            unit: TimeUnits = Units.NATIVE,
            wait: bool = True
    ) -> None:
        """
        Triggers the camera.
        Schedules trigger pulse on the digital output channel.
        By default, the method waits until the trigger pulse is finished.

        Args:
            pulse_width: The time duration of the trigger pulse.
                Depending on the camera setting, the argument can be use to specify exposure.
            unit: Units of time.
            wait: If false, the method does not wait until the trigger pulse is finished.
        """
        request = dto.MicroscopeTriggerCameraRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            channel_number=self.channel,
            delay=pulse_width,
            unit=unit,
            wait=wait,
        )
        await call_async("microscope/trigger_camera", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = call_sync(
            "device/device_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
