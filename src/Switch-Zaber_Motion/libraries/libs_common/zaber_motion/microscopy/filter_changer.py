# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0622

from ..ascii import Device
from ..call import call, call_async, call_sync
from ..dto import requests as dto


class FilterChanger:
    """
    A generic turret device.
    """

    @property
    def device(self) -> Device:
        """
        The base device of this turret.
        """
        return self._device

    def __init__(self, device: Device):
        """
        Creates instance of `FilterChanger` based on the given device.
        """
        self._device: Device = device

    def get_number_of_filters(
            self
    ) -> int:
        """
        Gets number of filters of the changer.

        Returns:
            Number of positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
        )
        response = call(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_number_of_filters_async(
            self
    ) -> int:
        """
        Gets number of filters of the changer.

        Returns:
            Number of positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
        )
        response = await call_async(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_current_filter(
            self
    ) -> int:
        """
        Returns the current filter number starting from 1.
        The value of 0 indicates that the position is either unknown or between two filters.

        Returns:
            Filter number starting from 1 or 0 if the position cannot be determined.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
        )
        response = call(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_current_filter_async(
            self
    ) -> int:
        """
        Returns the current filter number starting from 1.
        The value of 0 indicates that the position is either unknown or between two filters.

        Returns:
            Filter number starting from 1 or 0 if the position cannot be determined.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
        )
        response = await call_async(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def change(
            self,
            filter: int
    ) -> None:
        """
        Changes to the specified filter.

        Args:
            filter: Filter number starting from 1.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
            type=dto.AxisMoveType.INDEX,
            wait_until_idle=True,
            arg_int=filter,
        )
        call("device/move", request)

    async def change_async(
            self,
            filter: int
    ) -> None:
        """
        Changes to the specified filter.

        Args:
            filter: Filter number starting from 1.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=1,
            type=dto.AxisMoveType.INDEX,
            wait_until_idle=True,
            arg_int=filter,
        )
        await call_async("device/move", request)

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
