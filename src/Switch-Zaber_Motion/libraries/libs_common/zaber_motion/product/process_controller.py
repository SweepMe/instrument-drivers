# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List
from ..ascii.connection import Connection
from ..ascii.device import Device
from ..call import call, call_sync, call_async
from ..dto import requests as dto
from .process import Process


class ProcessController:
    """
    Use to manage a process controller.
    Requires at least Firmware 7.35.
    """

    @property
    def device(self) -> Device:
        """
        The base device of this process controller.
        """
        return self._device

    def __init__(self, device: Device):
        """
        Creates instance of `ProcessController` of the given device.
        If the device is identified, this constructor will ensure it is a process controller.
        """
        self._device: Device = device
        self.__verify_is_process_controller()

    @staticmethod
    def detect(
            connection: Connection,
            identify: bool = True
    ) -> List['ProcessController']:
        """
        Detects the process controllers on the connection.

        Args:
            connection: The connection to detect process controllers on.
            identify: If the Process Controllers should be identified upon detection.

        Returns:
            A list of all `ProcessController`s on the connection.
        """
        request = dto.DeviceDetectRequest(
            type=dto.DeviceType.PROCESS_CONTROLLER,
            interface_id=connection.interface_id,
            identify_devices=identify,
        )
        response = call(
            "device/detect",
            request,
            dto.DeviceDetectResponse.from_binary)
        return [ProcessController(connection.get_device(device)) for device in response.devices]

    @staticmethod
    async def detect_async(
            connection: Connection,
            identify: bool = True
    ) -> List['ProcessController']:
        """
        Detects the process controllers on the connection.

        Args:
            connection: The connection to detect process controllers on.
            identify: If the Process Controllers should be identified upon detection.

        Returns:
            A list of all `ProcessController`s on the connection.
        """
        request = dto.DeviceDetectRequest(
            type=dto.DeviceType.PROCESS_CONTROLLER,
            interface_id=connection.interface_id,
            identify_devices=identify,
        )
        response = await call_async(
            "device/detect",
            request,
            dto.DeviceDetectResponse.from_binary)
        return [ProcessController(connection.get_device(device)) for device in response.devices]

    def get_process(
            self,
            process_number: int
    ) -> Process:
        """
        Gets an Process class instance which allows you to control a particular voltage source.
        Axes are numbered from 1.

        Args:
            process_number: Number of process to control.

        Returns:
            Process instance.
        """
        if process_number <= 0:
            raise ValueError('Invalid value; processes are numbered from 1.')

        return Process(self, process_number)

    def __verify_is_process_controller(
            self
    ) -> None:
        """
        Checks if this is a process controller or some other type of device and throws an error if it is not.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        call_sync("process_controller/verify", request)

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
