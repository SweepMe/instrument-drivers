# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import TYPE_CHECKING, List
from ..protobufs import main_pb2
from ..call import call, call_async

if TYPE_CHECKING:
    from .device import Device


class StreamBuffer:
    """
    Represents a stream buffer with this ID on a device.
    A stream buffer is a place to store a queue of stream actions.
    """

    @property
    def device(self) -> 'Device':
        """
        The Device this buffer exists on.
        """
        return self._device

    @property
    def buffer_id(self) -> int:
        """
        The number identifying the buffer on the device.
        """
        return self._buffer_id

    def __init__(self, device: 'Device', buffer_id: int):
        self._device = device
        self._buffer_id = buffer_id

    def get_content(
            self
    ) -> List[str]:
        """
        Get the buffer contents as an array of strings.

        Returns:
            A string array containing all the stream commands stored in the buffer.
        """
        request = main_pb2.StreamBufferGetContentRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.buffer_id = self.buffer_id
        response = main_pb2.StreamBufferGetContentResponse()
        call("device/stream_buffer_get_content", request, response)
        return response.buffer_lines[:]

    async def get_content_async(
            self
    ) -> List[str]:
        """
        Get the buffer contents as an array of strings.

        Returns:
            A string array containing all the stream commands stored in the buffer.
        """
        request = main_pb2.StreamBufferGetContentRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.buffer_id = self.buffer_id
        response = main_pb2.StreamBufferGetContentResponse()
        await call_async("device/stream_buffer_get_content", request, response)
        return response.buffer_lines[:]

    def erase(
            self
    ) -> None:
        """
        Erase the contents of the buffer.
        """
        request = main_pb2.StreamBufferEraseRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.buffer_id = self.buffer_id
        call("device/stream_buffer_erase", request)

    async def erase_async(
            self
    ) -> None:
        """
        Erase the contents of the buffer.
        """
        request = main_pb2.StreamBufferEraseRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.buffer_id = self.buffer_id
        await call_async("device/stream_buffer_erase", request)
