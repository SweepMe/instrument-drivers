# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.stream_axis_definition import StreamAxisDefinition
from ..dto.ascii.stream_mode import StreamMode
from ..dto.measurement import Measurement
from ..dto.rotation_direction import RotationDirection
from ..units import Units, VelocityUnits, AccelerationUnits, TimeUnits
from .stream_buffer import StreamBuffer
from .stream_io import StreamIo

if TYPE_CHECKING:
    from .device import Device


class Stream:
    """
    A handle for a stream with this number on the device.
    Streams provide a way to execute or store a sequence of actions.
    Stream methods append actions to a queue which executes or stores actions in a first in, first out order.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this stream.
        """
        return self._device

    @property
    def stream_id(self) -> int:
        """
        The number that identifies the stream on the device.
        """
        return self._stream_id

    @property
    def mode(self) -> StreamMode:
        """
        Current mode of the stream.
        """
        return self.__retrieve_mode()

    @property
    def axes(self) -> List[StreamAxisDefinition]:
        """
        An array of axes definitions the stream is set up to control.
        """
        return self.__retrieve_axes()

    @property
    def io(self) -> StreamIo:
        """
        Gets an object that provides access to I/O for this stream.
        """
        return self._io

    def __init__(self, device: 'Device', stream_id: int):
        self._device: 'Device' = device
        self._stream_id: int = stream_id
        self._io: StreamIo = StreamIo(device, stream_id)

    def setup_live_composite(
            self,
            *axes: StreamAxisDefinition
    ) -> None:
        """
        Setup the stream to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a stream.

        Args:
            axes: Definition of the stream axes.
        """
        request = dto.StreamSetupLiveCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            axes=list(axes),
        )
        call("device/stream_setup_live_composite", request)

    async def setup_live_composite_async(
            self,
            *axes: StreamAxisDefinition
    ) -> None:
        """
        Setup the stream to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a stream.

        Args:
            axes: Definition of the stream axes.
        """
        request = dto.StreamSetupLiveCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            axes=list(axes),
        )
        await call_async("device/stream_setup_live_composite", request)

    def setup_live(
            self,
            *axes: int
    ) -> None:
        """
        Setup the stream to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the stream on.
        """
        request = dto.StreamSetupLiveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            axes=list(axes),
        )
        call("device/stream_setup_live", request)

    async def setup_live_async(
            self,
            *axes: int
    ) -> None:
        """
        Setup the stream to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the stream on.
        """
        request = dto.StreamSetupLiveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            axes=list(axes),
        )
        await call_async("device/stream_setup_live", request)

    def setup_store_composite(
            self,
            stream_buffer: StreamBuffer,
            *axes: StreamAxisDefinition
    ) -> None:
        """
        Setup the stream to control the specified axes and queue actions into a stream buffer.
        Allows use of lockstep axes in a stream.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes: Definition of the stream axes.
        """
        request = dto.StreamSetupStoreCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes=list(axes),
        )
        call("device/stream_setup_store_composite", request)

    async def setup_store_composite_async(
            self,
            stream_buffer: StreamBuffer,
            *axes: StreamAxisDefinition
    ) -> None:
        """
        Setup the stream to control the specified axes and queue actions into a stream buffer.
        Allows use of lockstep axes in a stream.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes: Definition of the stream axes.
        """
        request = dto.StreamSetupStoreCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes=list(axes),
        )
        await call_async("device/stream_setup_store_composite", request)

    def setup_store(
            self,
            stream_buffer: StreamBuffer,
            *axes: int
    ) -> None:
        """
        Setup the stream to control the specified axes and queue actions into a stream buffer.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes: The axis numbers of the physical axes to setup the stream on.
        """
        request = dto.StreamSetupStoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes=list(axes),
        )
        call("device/stream_setup_store", request)

    async def setup_store_async(
            self,
            stream_buffer: StreamBuffer,
            *axes: int
    ) -> None:
        """
        Setup the stream to control the specified axes and queue actions into a stream buffer.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes: The axis numbers of the physical axes to setup the stream on.
        """
        request = dto.StreamSetupStoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes=list(axes),
        )
        await call_async("device/stream_setup_store", request)

    def setup_store_arbitrary_axes(
            self,
            stream_buffer: StreamBuffer,
            axes_count: int
    ) -> None:
        """
        Setup the stream to use a specified number of axes, and to queue actions in a stream buffer.
        Afterwards, you may call the resulting stream buffer on arbitrary axes.
        This mode does not allow for unit conversions.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes_count: The number of axes in the stream.
        """
        request = dto.StreamSetupStoreArbitraryAxesRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes_count=axes_count,
        )
        call("device/stream_setup_store_arbitrary_axes", request)

    async def setup_store_arbitrary_axes_async(
            self,
            stream_buffer: StreamBuffer,
            axes_count: int
    ) -> None:
        """
        Setup the stream to use a specified number of axes, and to queue actions in a stream buffer.
        Afterwards, you may call the resulting stream buffer on arbitrary axes.
        This mode does not allow for unit conversions.

        Args:
            stream_buffer: The stream buffer to queue actions in.
            axes_count: The number of axes in the stream.
        """
        request = dto.StreamSetupStoreArbitraryAxesRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
            axes_count=axes_count,
        )
        await call_async("device/stream_setup_store_arbitrary_axes", request)

    def call(
            self,
            stream_buffer: StreamBuffer
    ) -> None:
        """
        Append the actions in a stream buffer to the queue.

        Args:
            stream_buffer: The stream buffer to call.
        """
        request = dto.StreamCallRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
        )
        call("device/stream_call", request)

    async def call_async(
            self,
            stream_buffer: StreamBuffer
    ) -> None:
        """
        Append the actions in a stream buffer to the queue.

        Args:
            stream_buffer: The stream buffer to call.
        """
        request = dto.StreamCallRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            stream_buffer=stream_buffer.buffer_number,
        )
        await call_async("device/stream_call", request)

    def line_absolute(
            self,
            *endpoint: Measurement
    ) -> None:
        """
        Queue an absolute line movement in the stream.

        Args:
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            endpoint=list(endpoint),
        )
        call("device/stream_line", request)

    async def line_absolute_async(
            self,
            *endpoint: Measurement
    ) -> None:
        """
        Queue an absolute line movement in the stream.

        Args:
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            endpoint=list(endpoint),
        )
        await call_async("device/stream_line", request)

    def line_relative(
            self,
            *endpoint: Measurement
    ) -> None:
        """
        Queue a relative line movement in the stream.

        Args:
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            endpoint=list(endpoint),
        )
        call("device/stream_line", request)

    async def line_relative_async(
            self,
            *endpoint: Measurement
    ) -> None:
        """
        Queue a relative line movement in the stream.

        Args:
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            endpoint=list(endpoint),
        )
        await call_async("device/stream_line", request)

    def line_absolute_on(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue an absolute line movement in the stream, targeting a subset of the stream axes.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            endpoint=endpoint,
        )
        call("device/stream_line", request)

    async def line_absolute_on_async(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue an absolute line movement in the stream, targeting a subset of the stream axes.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            endpoint=endpoint,
        )
        await call_async("device/stream_line", request)

    def line_relative_on(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue a relative line movement in the stream, targeting a subset of the stream axes.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            endpoint=endpoint,
        )
        call("device/stream_line", request)

    async def line_relative_on_async(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue a relative line movement in the stream, targeting a subset of the stream axes.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = dto.StreamLineRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            endpoint=endpoint,
        )
        await call_async("device/stream_line", request)

    def arc_absolute(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue an absolute arc movement on the first two axes of the stream.
        Absolute meaning that the home positions of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        call("device/stream_arc", request)

    async def arc_absolute_async(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue an absolute arc movement on the first two axes of the stream.
        Absolute meaning that the home positions of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        await call_async("device/stream_arc", request)

    def arc_relative(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue a relative arc movement on the first two axes of the stream.
        Relative meaning that the current position of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        call("device/stream_arc", request)

    async def arc_relative_async(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue a relative arc movement on the first two axes of the stream.
        Relative meaning that the current position of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        await call_async("device/stream_arc", request)

    def arc_absolute_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue an absolute arc movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        call("device/stream_arc", request)

    async def arc_absolute_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue an absolute arc movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        await call_async("device/stream_arc", request)

    def arc_relative_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue a relative arc movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        call("device/stream_arc", request)

    async def arc_relative_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement
    ) -> None:
        """
        Queue a relative arc movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the arc exists.
            center_y: The second dimension of the position of the center of the circle on which the arc exists.
            end_x: The first dimension of the end position of the arc.
            end_y: The second dimension of the end position of the arc.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
        )
        await call_async("device/stream_arc", request)

    def helix_absolute_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement,
            *endpoint: Measurement
    ) -> None:
        """
        Queue an absolute helix movement in the stream.
        Requires at least Firmware 7.28.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
                The first two axes refer to the helix's arc component,
                while the rest refers to the helix's line component.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the helix projects.
            center_y: The second dimension of the position of the center of the circle on which the helix projects.
            end_x: The first dimension of the end position of the helix's arc component.
            end_y: The second dimension of the end position of the helix's arc component.
            endpoint: Positions for the helix's line component axes, relative to their home positions.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
            endpoint=list(endpoint),
        )
        call("device/stream_helix", request)

    async def helix_absolute_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement,
            *endpoint: Measurement
    ) -> None:
        """
        Queue an absolute helix movement in the stream.
        Requires at least Firmware 7.28.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
                The first two axes refer to the helix's arc component,
                while the rest refers to the helix's line component.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the helix projects.
            center_y: The second dimension of the position of the center of the circle on which the helix projects.
            end_x: The first dimension of the end position of the helix's arc component.
            end_y: The second dimension of the end position of the helix's arc component.
            endpoint: Positions for the helix's line component axes, relative to their home positions.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
            endpoint=list(endpoint),
        )
        await call_async("device/stream_helix", request)

    def helix_relative_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement,
            *endpoint: Measurement
    ) -> None:
        """
        Queue a relative helix movement in the stream.
        Requires at least Firmware 7.28.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
                The first two axes refer to the helix's arc component,
                while the rest refers to the helix's line component.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the helix projects.
            center_y: The second dimension of the position of the center of the circle on which the helix projects.
            end_x: The first dimension of the end position of the helix's arc component.
            end_y: The second dimension of the end position of the helix's arc component.
            endpoint: Positions for the helix's line component axes, relative to their positions before movement.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
            endpoint=list(endpoint),
        )
        call("device/stream_helix", request)

    async def helix_relative_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement,
            end_x: Measurement,
            end_y: Measurement,
            *endpoint: Measurement
    ) -> None:
        """
        Queue a relative helix movement in the stream.
        Requires at least Firmware 7.28.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
                The first two axes refer to the helix's arc component,
                while the rest refers to the helix's line component.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle on which the helix projects.
            center_y: The second dimension of the position of the center of the circle on which the helix projects.
            end_x: The first dimension of the end position of the helix's arc component.
            end_y: The second dimension of the end position of the helix's arc component.
            endpoint: Positions for the helix's line component axes, relative to their positions before movement.
        """
        request = dto.StreamArcRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
            end_x=end_x,
            end_y=end_y,
            endpoint=list(endpoint),
        )
        await call_async("device/stream_helix", request)

    def circle_absolute(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue an absolute circle movement on the first two axes of the stream.
        Absolute meaning that the home positions of the axes are treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        call("device/stream_circle", request)

    async def circle_absolute_async(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue an absolute circle movement on the first two axes of the stream.
        Absolute meaning that the home positions of the axes are treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        await call_async("device/stream_circle", request)

    def circle_relative(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue a relative circle movement on the first two axes of the stream.
        Relative meaning that the current position of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        call("device/stream_circle", request)

    async def circle_relative_async(
            self,
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue a relative circle movement on the first two axes of the stream.
        Relative meaning that the current position of the axes is treated as the origin.

        Args:
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        await call_async("device/stream_circle", request)

    def circle_absolute_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue an absolute circle movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        call("device/stream_circle", request)

    async def circle_absolute_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue an absolute circle movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.ABS,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        await call_async("device/stream_circle", request)

    def circle_relative_on(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue a relative circle movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        call("device/stream_circle", request)

    async def circle_relative_on_async(
            self,
            target_axes_indices: List[int],
            rotation_direction: RotationDirection,
            center_x: Measurement,
            center_y: Measurement
    ) -> None:
        """
        Queue a relative circle movement in the stream.
        The movement will only target the specified subset of axes in the stream.
        Requires at least Firmware 7.11.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = dto.StreamCircleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            type=dto.StreamSegmentType.REL,
            target_axes_indices=target_axes_indices,
            rotation_direction=rotation_direction,
            center_x=center_x,
            center_y=center_y,
        )
        await call_async("device/stream_circle", request)

    def wait(
            self,
            time: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Wait a specified time.

        Args:
            time: Amount of time to wait.
            unit: Units of time.
        """
        request = dto.StreamWaitRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            time=time,
            unit=unit,
        )
        call("device/stream_wait", request)

    async def wait_async(
            self,
            time: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Wait a specified time.

        Args:
            time: Amount of time to wait.
            unit: Units of time.
        """
        request = dto.StreamWaitRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            time=time,
            unit=unit,
        )
        await call_async("device/stream_wait", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live stream executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.StreamWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        call("device/stream_wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live stream executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.StreamWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("device/stream_wait_until_idle", request)

    def cork(
            self
    ) -> None:
        """
        Cork the front of the stream's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent stream commands reaching the device late.
        You can only cork an idle live stream.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        call("device/stream_cork", request)

    async def cork_async(
            self
    ) -> None:
        """
        Cork the front of the stream's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent stream commands reaching the device late.
        You can only cork an idle live stream.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        await call_async("device/stream_cork", request)

    def uncork(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live stream that is corked.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        call("device/stream_uncork", request)

    async def uncork_async(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live stream that is corked.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        await call_async("device/stream_uncork", request)

    def set_hold(
            self,
            hold: bool
    ) -> None:
        """
        Pauses or resumes execution of the stream in live mode.
        The hold only takes effect during execution of motion segments.

        Args:
            hold: True to pause execution, false to resume.
        """
        request = dto.StreamSetHoldRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            hold=hold,
        )
        call("device/stream_set_hold", request)

    async def set_hold_async(
            self,
            hold: bool
    ) -> None:
        """
        Pauses or resumes execution of the stream in live mode.
        The hold only takes effect during execution of motion segments.

        Args:
            hold: True to pause execution, false to resume.
        """
        request = dto.StreamSetHoldRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            hold=hold,
        )
        await call_async("device/stream_set_hold", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live stream is executing a queued action.

        Returns:
            True if the stream is executing a queued action.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = call(
            "device/stream_is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live stream is executing a queued action.

        Returns:
            True if the stream is executing a queued action.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = await call_async(
            "device/stream_is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_max_speed(
            self,
            unit: VelocityUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of velocity.

        Returns:
            The maximum speed of the stream.
        """
        request = dto.StreamGetMaxSpeedRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = call(
            "device/stream_get_max_speed",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_max_speed_async(
            self,
            unit: VelocityUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of velocity.

        Returns:
            The maximum speed of the stream.
        """
        request = dto.StreamGetMaxSpeedRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = await call_async(
            "device/stream_get_max_speed",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_max_speed(
            self,
            max_speed: float,
            unit: VelocityUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_speed: Maximum speed at which any stream action is executed.
            unit: Units of velocity.
        """
        request = dto.StreamSetMaxSpeedRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_speed=max_speed,
            unit=unit,
        )
        call("device/stream_set_max_speed", request)

    async def set_max_speed_async(
            self,
            max_speed: float,
            unit: VelocityUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_speed: Maximum speed at which any stream action is executed.
            unit: Units of velocity.
        """
        request = dto.StreamSetMaxSpeedRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_speed=max_speed,
            unit=unit,
        )
        await call_async("device/stream_set_max_speed", request)

    def get_max_tangential_acceleration(
            self,
            unit: AccelerationUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum tangential acceleration of the live stream.
        """
        request = dto.StreamGetMaxTangentialAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = call(
            "device/stream_get_max_tangential_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_max_tangential_acceleration_async(
            self,
            unit: AccelerationUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum tangential acceleration of the live stream.
        """
        request = dto.StreamGetMaxTangentialAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = await call_async(
            "device/stream_get_max_tangential_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_max_tangential_acceleration(
            self,
            max_tangential_acceleration: float,
            unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_tangential_acceleration: Maximum tangential acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = dto.StreamSetMaxTangentialAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_tangential_acceleration=max_tangential_acceleration,
            unit=unit,
        )
        call("device/stream_set_max_tangential_acceleration", request)

    async def set_max_tangential_acceleration_async(
            self,
            max_tangential_acceleration: float,
            unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_tangential_acceleration: Maximum tangential acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = dto.StreamSetMaxTangentialAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_tangential_acceleration=max_tangential_acceleration,
            unit=unit,
        )
        await call_async("device/stream_set_max_tangential_acceleration", request)

    def get_max_centripetal_acceleration(
            self,
            unit: AccelerationUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum centripetal acceleration of the live stream.
        """
        request = dto.StreamGetMaxCentripetalAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = call(
            "device/stream_get_max_centripetal_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_max_centripetal_acceleration_async(
            self,
            unit: AccelerationUnits = Units.NATIVE
    ) -> float:
        """
        Gets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum centripetal acceleration of the live stream.
        """
        request = dto.StreamGetMaxCentripetalAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            unit=unit,
        )
        response = await call_async(
            "device/stream_get_max_centripetal_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_max_centripetal_acceleration(
            self,
            max_centripetal_acceleration: float,
            unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_centripetal_acceleration: Maximum centripetal acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = dto.StreamSetMaxCentripetalAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_centripetal_acceleration=max_centripetal_acceleration,
            unit=unit,
        )
        call("device/stream_set_max_centripetal_acceleration", request)

    async def set_max_centripetal_acceleration_async(
            self,
            max_centripetal_acceleration: float,
            unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Sets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_centripetal_acceleration: Maximum centripetal acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = dto.StreamSetMaxCentripetalAccelerationRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            max_centripetal_acceleration=max_centripetal_acceleration,
            unit=unit,
        )
        await call_async("device/stream_set_max_centripetal_acceleration", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string which represents the stream.

        Returns:
            String which represents the stream.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = call_sync(
            "device/stream_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def disable(
            self
    ) -> None:
        """
        Disables the stream.
        If the stream is not setup, this command does nothing.
        Once disabled, the stream will no longer accept stream commands.
        The stream will process the rest of the commands in the queue until it is empty.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        call("device/stream_disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disables the stream.
        If the stream is not setup, this command does nothing.
        Once disabled, the stream will no longer accept stream commands.
        The stream will process the rest of the commands in the queue until it is empty.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        await call_async("device/stream_disable", request)

    def generic_command(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the stream.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = dto.StreamGenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            command=command,
        )
        call("device/stream_generic_command", request)

    async def generic_command_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the stream.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = dto.StreamGenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            command=command,
        )
        await call_async("device/stream_generic_command", request)

    def generic_command_batch(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the stream.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = dto.StreamGenericCommandBatchRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            batch=batch,
        )
        call("device/stream_generic_command_batch", request)

    async def generic_command_batch_async(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the stream.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = dto.StreamGenericCommandBatchRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
            batch=batch,
        )
        await call_async("device/stream_generic_command_batch", request)

    def check_disabled(
            self
    ) -> bool:
        """
        Queries the stream status from the device
        and returns boolean indicating whether the stream is disabled.
        Useful to determine if streaming was interrupted by other movements.

        Returns:
            True if the stream is disabled.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = call(
            "device/stream_check_disabled",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def check_disabled_async(
            self
    ) -> bool:
        """
        Queries the stream status from the device
        and returns boolean indicating whether the stream is disabled.
        Useful to determine if streaming was interrupted by other movements.

        Returns:
            True if the stream is disabled.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = await call_async(
            "device/stream_check_disabled",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def treat_discontinuities_as_error(
            self
    ) -> None:
        """
        Makes the stream throw StreamDiscontinuityException when it encounters discontinuities (ND warning flag).
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        call_sync("device/stream_treat_discontinuities", request)

    def ignore_current_discontinuity(
            self
    ) -> None:
        """
        Prevents StreamDiscontinuityException as a result of expected discontinuity when resuming streaming.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        call_sync("device/stream_ignore_discontinuity", request)

    def __retrieve_axes(
            self
    ) -> List[StreamAxisDefinition]:
        """
        Gets the axes of the stream.

        Returns:
            An array of axis numbers of the axes the stream is set up to control.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = call_sync(
            "device/stream_get_axes",
            request,
            dto.StreamGetAxesResponse.from_binary)
        return response.axes

    def __retrieve_mode(
            self
    ) -> StreamMode:
        """
        Get the mode of the stream.

        Returns:
            Mode of the stream.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.stream_id,
        )
        response = call_sync(
            "device/stream_get_mode",
            request,
            dto.StreamModeResponse.from_binary)
        return response.stream_mode
