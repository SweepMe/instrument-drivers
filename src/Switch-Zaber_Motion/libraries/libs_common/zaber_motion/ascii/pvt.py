# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from ..dto import requests as dto
from .pvt_buffer import PvtBuffer
from .pvt_sequence import PvtSequence

if TYPE_CHECKING:
    from .device import Device


class Pvt:
    """
    Class providing access to device PVT (Position-Velocity-Time) features.
    Requires at least Firmware 7.33.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that this PVT belongs to.
        """
        return self._device

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def get_sequence(
            self,
            pvt_id: int
    ) -> 'PvtSequence':
        """
        Gets a PvtSequence class instance which allows you to control a particular PVT sequence on the device.

        Args:
            pvt_id: The ID of the PVT sequence to control. The IDs start at 1.

        Returns:
            PvtSequence instance.
        """
        if pvt_id <= 0:
            raise ValueError('Invalid value; PVT sequences are numbered from 1.')

        return PvtSequence(self.device, pvt_id)

    def get_buffer(
            self,
            pvt_buffer_number: int
    ) -> 'PvtBuffer':
        """
        Gets a PvtBuffer class instance which is a handle for a PVT buffer on the device.

        Args:
            pvt_buffer_number: The ID number of the PVT buffer to control. PVT buffer numbers start at one.

        Returns:
            PvtBuffer instance.
        """
        if pvt_buffer_number <= 0:
            raise ValueError('Invalid value; PVT buffers are numbered from 1.')

        return PvtBuffer(self.device, pvt_buffer_number)

    def list_buffer_numbers(
            self
    ) -> List[int]:
        """
        Get a list of buffer ID numbers that are currently in use.

        Returns:
            List of buffer IDs.
        """
        request = dto.StreamBufferList(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            pvt=True,
        )
        response = call(
            "device/stream_buffer_list",
            request,
            dto.IntArrayResponse.from_binary)
        return response.values

    async def list_buffer_numbers_async(
            self
    ) -> List[int]:
        """
        Get a list of buffer ID numbers that are currently in use.

        Returns:
            List of buffer IDs.
        """
        request = dto.StreamBufferList(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            pvt=True,
        )
        response = await call_async(
            "device/stream_buffer_list",
            request,
            dto.IntArrayResponse.from_binary)
        return response.values
