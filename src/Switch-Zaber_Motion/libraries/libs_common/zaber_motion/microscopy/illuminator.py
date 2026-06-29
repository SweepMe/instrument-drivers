# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from ..ascii import DeviceIO, Connection, Device
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from .illuminator_channel import IlluminatorChannel


class Illuminator:
    """
    Use to manage an LED controller.
    Requires at least Firmware 7.09.
    """

    @property
    def device(self) -> Device:
        """
        The base device of this illuminator.
        """
        return self._device

    @property
    def io(self) -> DeviceIO:
        """
        I/O channels of this device.
        """
        return self._io

    def __init__(self, device: Device):
        """
        Creates instance of `Illuminator` based on the given device.
        If the device is identified, this constructor will ensure it is an illuminator.
        """
        self._device: Device = device
        self._io: DeviceIO = DeviceIO(device)
        self.__verify_is_illuminator()

    def get_channel(
            self,
            channel_number: int
    ) -> IlluminatorChannel:
        """
        Gets an IlluminatorChannel class instance that allows control of a particular channel.
        Channels are numbered from 1.

        Args:
            channel_number: Number of channel to control.

        Returns:
            Illuminator channel instance.
        """
        if channel_number <= 0:
            raise ValueError('Invalid value; channels are numbered from 1.')

        return IlluminatorChannel(self, channel_number)

    def turn_off(
            self
    ) -> None:
        """
        Turns all channels off.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        call("illuminator/all_off", request)

    async def turn_off_async(
            self
    ) -> None:
        """
        Turns all channels off.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        await call_async("illuminator/all_off", request)

    def __verify_is_illuminator(
            self
    ) -> None:
        """
        Checks if this is an illuminator or some other type of device and throws an error if it is not.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        call_sync("illuminator/verify", request)

    @staticmethod
    def find(
            connection: Connection,
            device_address: int = 0
    ) -> 'Illuminator':
        """
        Finds an illuminator on a connection.
        In case of conflict, specify the optional device address.

        Args:
            connection: Connection on which to detect the illuminator.
            device_address: Optional device address of the illuminator.

        Returns:
            New instance of illuminator.
        """
        request = dto.FindDeviceRequest(
            interface_id=connection.interface_id,
            device_address=device_address,
        )
        response = call(
            "illuminator/detect",
            request,
            dto.FindDeviceResponse.from_binary)
        return Illuminator(Device(connection, response.address))

    @staticmethod
    async def find_async(
            connection: Connection,
            device_address: int = 0
    ) -> 'Illuminator':
        """
        Finds an illuminator on a connection.
        In case of conflict, specify the optional device address.

        Args:
            connection: Connection on which to detect the illuminator.
            device_address: Optional device address of the illuminator.

        Returns:
            New instance of illuminator.
        """
        request = dto.FindDeviceRequest(
            interface_id=connection.interface_id,
            device_address=device_address,
        )
        response = await call_async(
            "illuminator/detect",
            request,
            dto.FindDeviceResponse.from_binary)
        return Illuminator(Device(connection, response.address))

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
