# pylint: disable=too-many-arguments, too-many-lines

# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import TYPE_CHECKING, List
from ..protobufs import main_pb2
from ..units import Units
from ..call import call, call_async, call_sync
from ..measurement import Measurement
from ..rotation_direction import RotationDirection
from .stream_buffer import StreamBuffer
from .stream_mode import StreamMode
from .stream_axis_definition import StreamAxisDefinition

if TYPE_CHECKING:
    from .device import Device


class Stream:
    """
    A handle for a stream with this ID on the device.
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

    def __init__(self, device: 'Device', stream_id: int):
        self._device = device
        self._stream_id = stream_id

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
        request = main_pb2.StreamSetupLiveCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.axes.extend([StreamAxisDefinition.to_protobuf(a) for a in axes])
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
        request = main_pb2.StreamSetupLiveCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.axes.extend([StreamAxisDefinition.to_protobuf(a) for a in axes])
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
        request = main_pb2.StreamSetupLiveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.axes.extend(axes)
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
        request = main_pb2.StreamSetupLiveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.axes.extend(axes)
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
        request = main_pb2.StreamSetupStoreCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes.extend([StreamAxisDefinition.to_protobuf(a) for a in axes])
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
        request = main_pb2.StreamSetupStoreCompositeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes.extend([StreamAxisDefinition.to_protobuf(a) for a in axes])
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
            axes: Numbers of physical axes to setup the stream on.
        """
        request = main_pb2.StreamSetupStoreRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes.extend(axes)
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
            axes: Numbers of physical axes to setup the stream on.
        """
        request = main_pb2.StreamSetupStoreRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes.extend(axes)
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
        request = main_pb2.StreamSetupStoreArbitraryAxesRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes_count = axes_count
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
        request = main_pb2.StreamSetupStoreArbitraryAxesRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
        request.axes_count = axes_count
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
        request = main_pb2.StreamCallRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
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
        request = main_pb2.StreamCallRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.stream_buffer = stream_buffer.buffer_id
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
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.ABS
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
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
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.ABS
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
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
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.REL
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
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
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.REL
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
        await call_async("device/stream_line", request)

    def line_absolute_on(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue an absolute line movement in the stream, targeting a subset of the stream axes.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
        call("device/stream_line", request)

    async def line_absolute_on_async(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue an absolute line movement in the stream, targeting a subset of the stream axes.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their home positions.
        """
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
        await call_async("device/stream_line", request)

    def line_relative_on(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue a relative line movement in the stream, targeting a subset of the stream axes.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
        call("device/stream_line", request)

    async def line_relative_on_async(
            self,
            target_axes_indices: List[int],
            endpoint: List[Measurement]
    ) -> None:
        """
        Queue a relative line movement in the stream, targeting a subset of the stream axes.

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            endpoint: Positions for the axes to move to, relative to their positions before movement.
        """
        request = main_pb2.StreamLineRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamLineRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.endpoint.extend([Measurement.to_protobuf(p) for p in endpoint])
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
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.ABS
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.ABS
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.REL
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.REL
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimensions of the position of the center of the circle on which the arc exists.
            center_y: The second dimensions of the position of the center of the circle on which the arc exists.
            end_x: The first dimensions of the end position of the arc.
            end_y: The second dimensions of the end position of the arc.
        """
        request = main_pb2.StreamArcRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamArcRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        request.end_x.CopyFrom(Measurement.to_protobuf(end_x))
        request.end_y.CopyFrom(Measurement.to_protobuf(end_y))
        await call_async("device/stream_arc", request)

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
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.ABS
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.ABS
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.REL
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.REL
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.ABS
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
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

        Args:
            target_axes_indices: Indices of the axes in the stream the movement targets.
                Refers to the axes provided during the stream setup or further execution.
                Indices are zero-based.
            rotation_direction: The direction of the rotation.
            center_x: The first dimension of the position of the center of the circle.
            center_y: The second dimension of the position of the center of the circle.
        """
        request = main_pb2.StreamCircleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.type = main_pb2.StreamCircleRequest.REL
        request.target_axes_indices.extend(target_axes_indices)
        request.rotation_direction = rotation_direction.value
        request.center_x.CopyFrom(Measurement.to_protobuf(center_x))
        request.center_y.CopyFrom(Measurement.to_protobuf(center_y))
        await call_async("device/stream_circle", request)

    def wait_digital_input(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Wait for a digital input channel to reach a given value.

        Args:
            channel_number: The number of the digital input channel.
                Channel numbers are numbered from one.
            value: The value that the stream should wait for.
        """
        request = main_pb2.StreamWaitDigitalInputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        call("device/stream_wait_digital_input", request)

    async def wait_digital_input_async(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Wait for a digital input channel to reach a given value.

        Args:
            channel_number: The number of the digital input channel.
                Channel numbers are numbered from one.
            value: The value that the stream should wait for.
        """
        request = main_pb2.StreamWaitDigitalInputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        await call_async("device/stream_wait_digital_input", request)

    def wait_analog_input(
            self,
            channel_number: int,
            condition: str,
            value: float
    ) -> None:
        """
        Wait for the value of a analog input channel to reach a condition concerning a given value.

        Args:
            channel_number: The number of the analog input channel.
                Channel numbers are numbered from one.
            condition: A condition (e.g. <, <=, ==, !=).
            value: The value that the condition concerns, in volts.
        """
        request = main_pb2.StreamWaitAnalogInputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.condition = condition
        request.value = value
        call("device/stream_wait_analog_input", request)

    async def wait_analog_input_async(
            self,
            channel_number: int,
            condition: str,
            value: float
    ) -> None:
        """
        Wait for the value of a analog input channel to reach a condition concerning a given value.

        Args:
            channel_number: The number of the analog input channel.
                Channel numbers are numbered from one.
            condition: A condition (e.g. <, <=, ==, !=).
            value: The value that the condition concerns, in volts.
        """
        request = main_pb2.StreamWaitAnalogInputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.condition = condition
        request.value = value
        await call_async("device/stream_wait_analog_input", request)

    def set_digital_output(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Set the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to.
        """
        request = main_pb2.StreamSetDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        call("device/stream_set_digital_output", request)

    async def set_digital_output_async(
            self,
            channel_number: int,
            value: bool
    ) -> None:
        """
        Set the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to.
        """
        request = main_pb2.StreamSetDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        await call_async("device/stream_set_digital_output", request)

    def set_analog_output(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Set the value of an analog output channel.

        Args:
            channel_number: The number of the analog output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to, in volts.
        """
        request = main_pb2.StreamSetAnalogOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        call("device/stream_set_analog_output", request)

    async def set_analog_output_async(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Set the value of an analog output channel.

        Args:
            channel_number: The number of the analog output channel.
                Channel numbers are numbered from one.
            value: The value to set the channel to, in volts.
        """
        request = main_pb2.StreamSetAnalogOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        request.value = value
        await call_async("device/stream_set_analog_output", request)

    def toggle_digital_output(
            self,
            channel_number: int
    ) -> None:
        """
        Toggle the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
        """
        request = main_pb2.StreamToggleDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        call("device/stream_toggle_digital_output", request)

    async def toggle_digital_output_async(
            self,
            channel_number: int
    ) -> None:
        """
        Toggle the value of a digital output channel.

        Args:
            channel_number: The number of the digital output channel.
                Channel numbers are numbered from one.
        """
        request = main_pb2.StreamToggleDigitalOutputRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.channel_number = channel_number
        await call_async("device/stream_toggle_digital_output", request)

    def wait(
            self,
            time: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Wait a specified time.

        Args:
            time: Amount of time to wait.
            unit: Units of time.
        """
        request = main_pb2.StreamWaitRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.time = time
        request.unit = unit.value
        call("device/stream_wait", request)

    async def wait_async(
            self,
            time: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Wait a specified time.

        Args:
            time: Amount of time to wait.
            unit: Units of time.
        """
        request = main_pb2.StreamWaitRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.time = time
        request.unit = unit.value
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
        request = main_pb2.StreamWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.throw_error_on_fault = throw_error_on_fault
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
        request = main_pb2.StreamWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.throw_error_on_fault = throw_error_on_fault
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
        request = main_pb2.StreamCorkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
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
        request = main_pb2.StreamCorkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        await call_async("device/stream_cork", request)

    def uncork(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live stream that is corked.
        """
        request = main_pb2.StreamUncorkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        call("device/stream_uncork", request)

    async def uncork_async(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live stream that is corked.
        """
        request = main_pb2.StreamUncorkRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        await call_async("device/stream_uncork", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live stream is executing a queued action.

        Returns:
            True if the stream is executing a queued action.
        """
        request = main_pb2.StreamIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        response = main_pb2.StreamIsBusyResponse()
        call("device/stream_is_busy", request, response)
        return response.is_busy

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live stream is executing a queued action.

        Returns:
            True if the stream is executing a queued action.
        """
        request = main_pb2.StreamIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        response = main_pb2.StreamIsBusyResponse()
        await call_async("device/stream_is_busy", request, response)
        return response.is_busy

    def get_max_speed(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of velocity.

        Returns:
            The maximum speed of the stream.
        """
        request = main_pb2.StreamGetMaxSpeedRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxSpeedResponse()
        call("device/stream_get_max_speed", request, response)
        return response.max_speed

    async def get_max_speed_async(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of velocity.

        Returns:
            The maximum speed of the stream.
        """
        request = main_pb2.StreamGetMaxSpeedRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxSpeedResponse()
        await call_async("device/stream_get_max_speed", request, response)
        return response.max_speed

    def set_max_speed(
            self,
            max_speed: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_speed: Maximum speed at which any stream action is executed.
            unit: Units of velocity.
        """
        request = main_pb2.StreamSetMaxSpeedRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_speed = max_speed
        request.unit = unit.value
        call("device/stream_set_max_speed", request)

    async def set_max_speed_async(
            self,
            max_speed: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum speed of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_speed: Maximum speed at which any stream action is executed.
            unit: Units of velocity.
        """
        request = main_pb2.StreamSetMaxSpeedRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_speed = max_speed
        request.unit = unit.value
        await call_async("device/stream_set_max_speed", request)

    def get_max_tangential_acceleration(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum tangential acceleration of the live stream.
        """
        request = main_pb2.StreamGetMaxTangentialAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxTangentialAccelerationResponse()
        call("device/stream_get_max_tangential_acceleration", request, response)
        return response.max_tangential_acceleration

    async def get_max_tangential_acceleration_async(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum tangential acceleration of the live stream.
        """
        request = main_pb2.StreamGetMaxTangentialAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxTangentialAccelerationResponse()
        await call_async("device/stream_get_max_tangential_acceleration", request, response)
        return response.max_tangential_acceleration

    def set_max_tangential_acceleration(
            self,
            max_tangential_acceleration: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_tangential_acceleration: Maximum tangential acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = main_pb2.StreamSetMaxTangentialAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_tangential_acceleration = max_tangential_acceleration
        request.unit = unit.value
        call("device/stream_set_max_tangential_acceleration", request)

    async def set_max_tangential_acceleration_async(
            self,
            max_tangential_acceleration: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum tangential acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_tangential_acceleration: Maximum tangential acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = main_pb2.StreamSetMaxTangentialAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_tangential_acceleration = max_tangential_acceleration
        request.unit = unit.value
        await call_async("device/stream_set_max_tangential_acceleration", request)

    def get_max_centripetal_acceleration(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum centripetal acceleration of the live stream.
        """
        request = main_pb2.StreamGetMaxCentripetalAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxCentripetalAccelerationResponse()
        call("device/stream_get_max_centripetal_acceleration", request, response)
        return response.max_centripetal_acceleration

    async def get_max_centripetal_acceleration_async(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Gets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            unit: Units of acceleration.

        Returns:
            The maximum centripetal acceleration of the live stream.
        """
        request = main_pb2.StreamGetMaxCentripetalAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.unit = unit.value
        response = main_pb2.StreamGetMaxCentripetalAccelerationResponse()
        await call_async("device/stream_get_max_centripetal_acceleration", request, response)
        return response.max_centripetal_acceleration

    def set_max_centripetal_acceleration(
            self,
            max_centripetal_acceleration: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_centripetal_acceleration: Maximum centripetal acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = main_pb2.StreamSetMaxCentripetalAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_centripetal_acceleration = max_centripetal_acceleration
        request.unit = unit.value
        call("device/stream_set_max_centripetal_acceleration", request)

    async def set_max_centripetal_acceleration_async(
            self,
            max_centripetal_acceleration: float,
            unit: Units = Units.NATIVE
    ) -> None:
        """
        Sets the maximum centripetal acceleration of the live stream.
        Converts the units using the first axis of the stream.

        Args:
            max_centripetal_acceleration: Maximum centripetal acceleration at which any stream action is executed.
            unit: Units of acceleration.
        """
        request = main_pb2.StreamSetMaxCentripetalAccelerationRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        request.max_centripetal_acceleration = max_centripetal_acceleration
        request.unit = unit.value
        await call_async("device/stream_set_max_centripetal_acceleration", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string which represents the stream.

        Returns:
            String which represents the stream.
        """
        request = main_pb2.StreamToStringRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        response = main_pb2.StreamToStringResponse()
        call_sync("device/stream_to_string", request, response)
        return response.to_str

    def disable(
            self
    ) -> None:
        """
        Disable the stream.
        If the stream is not setup, this command does nothing.
        Once disabled, the stream will no longer accept stream commands.
        The stream will process the rest of the commands in the queue until it is empty.
        """
        request = main_pb2.StreamDisableRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        call("device/stream_disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disable the stream.
        If the stream is not setup, this command does nothing.
        Once disabled, the stream will no longer accept stream commands.
        The stream will process the rest of the commands in the queue until it is empty.
        """
        request = main_pb2.StreamDisableRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        await call_async("device/stream_disable", request)

    def __retrieve_axes(
            self
    ) -> List[StreamAxisDefinition]:
        """
        Gets the axes of the stream.

        Returns:
            An array of axis numbers of the axes the stream is set up to control.
        """
        request = main_pb2.StreamGetAxesRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        response = main_pb2.StreamGetAxesResponse()
        call_sync("device/stream_get_axes", request, response)
        return [StreamAxisDefinition.from_protobuf(a) for a in response.axes]

    def __retrieve_mode(
            self
    ) -> StreamMode:
        """
        Get the mode of the stream.

        Returns:
            Mode of the stream.
        """
        request = main_pb2.StreamGetModeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.stream_id = self.stream_id
        response = main_pb2.StreamGetModeResponse()
        call_sync("device/stream_get_mode", request, response)
        return StreamMode(response.mode)
