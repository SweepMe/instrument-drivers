# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.pvt_buffer_axis_units import PvtBufferAxisUnits
from ..dto.ascii.pvt_sequence_item import PvtSequenceItem
from ..units import Units, UnitsAndLiterals

if TYPE_CHECKING:
    from .device import Device


class PvtBuffer:
    """
    Represents a PVT buffer with this number on a device.
    A PVT buffer is a place to store a queue of PVT actions.
    """

    @property
    def device(self) -> 'Device':
        """
        The Device this buffer exists on.
        """
        return self._device

    @property
    def buffer_number(self) -> int:
        """
        The number identifying the buffer on the device.
        """
        return self._buffer_number

    def __init__(self, device: 'Device', buffer_number: int):
        self._device: 'Device' = device
        self._buffer_number: int = buffer_number

    def get_content(
            self
    ) -> List[str]:
        """
        Gets the buffer contents as an array of strings.

        Returns:
            A string array containing all the PVT commands stored in the buffer.
        """
        request = dto.StreamBufferGetContentRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            pvt=True,
        )
        response = call(
            "device/stream_buffer_get_content",
            request,
            dto.StreamBufferGetContentResponse.from_binary)
        return response.buffer_lines

    async def get_content_async(
            self
    ) -> List[str]:
        """
        Gets the buffer contents as an array of strings.

        Returns:
            A string array containing all the PVT commands stored in the buffer.
        """
        request = dto.StreamBufferGetContentRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            pvt=True,
        )
        response = await call_async(
            "device/stream_buffer_get_content",
            request,
            dto.StreamBufferGetContentResponse.from_binary)
        return response.buffer_lines

    def retrieve_sequence_data(
            self,
            axes: Optional[List[PvtBufferAxisUnits]] = None,
            time_units: UnitsAndLiterals = Units.NATIVE
    ) -> List[PvtSequenceItem]:
        """
        Gets the buffer contents as an array of PvtSequenceItem objects.

        Args:
            axes: Per-axis unit conversion specification.
                The length must match the number of axes in the buffer.
                When omitted, position and velocity values are returned in native units.
            time_units: Units to convert time values to. Defaults to native.

        Returns:
            The PVT data loaded from the buffer.
        """
        request = dto.PvtBufferGetSequenceDataRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            axes=axes,
            time_units=time_units,
        )
        response = call(
            "device/pvt_buffer_get_data",
            request,
            dto.PvtBufferGetSequenceDataResponse.from_binary)
        return response.sequence_data

    async def retrieve_sequence_data_async(
            self,
            axes: Optional[List[PvtBufferAxisUnits]] = None,
            time_units: UnitsAndLiterals = Units.NATIVE
    ) -> List[PvtSequenceItem]:
        """
        Gets the buffer contents as an array of PvtSequenceItem objects.

        Args:
            axes: Per-axis unit conversion specification.
                The length must match the number of axes in the buffer.
                When omitted, position and velocity values are returned in native units.
            time_units: Units to convert time values to. Defaults to native.

        Returns:
            The PVT data loaded from the buffer.
        """
        request = dto.PvtBufferGetSequenceDataRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            axes=axes,
            time_units=time_units,
        )
        response = await call_async(
            "device/pvt_buffer_get_data",
            request,
            dto.PvtBufferGetSequenceDataResponse.from_binary)
        return response.sequence_data

    def erase(
            self
    ) -> None:
        """
        Erases the contents of the buffer.
        This method fails if there is a PVT sequence writing to the buffer.
        """
        request = dto.StreamBufferEraseRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            pvt=True,
        )
        call("device/stream_buffer_erase", request)

    async def erase_async(
            self
    ) -> None:
        """
        Erases the contents of the buffer.
        This method fails if there is a PVT sequence writing to the buffer.
        """
        request = dto.StreamBufferEraseRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            buffer_number=self.buffer_number,
            pvt=True,
        )
        await call_async("device/stream_buffer_erase", request)
