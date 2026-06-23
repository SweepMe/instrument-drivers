# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.measurement_sequence import MeasurementSequence
from ..dto.ascii.pvt_axis_definition import PvtAxisDefinition
from ..dto.ascii.pvt_csv_data import PvtCsvData
from ..dto.ascii.pvt_partial_csv_data import PvtPartialCsvData
from ..dto.ascii.pvt_mode import PvtMode
from ..dto.ascii.pvt_sequence_item import PvtSequenceItem
from ..dto.ascii.pvt_partial_sequence_item import PvtPartialSequenceItem
from ..dto.measurement import Measurement
from .pvt_buffer import PvtBuffer
from .pvt_io import PvtIo

if TYPE_CHECKING:
    from .device import Device


class PvtSequence:
    """
    A handle for a PVT sequence with this number on the device.
    PVT sequences provide a way execute or store trajectory
    consisting of points with defined position, velocity, and time.
    PVT sequence methods append actions to a queue which executes
    or stores actions in a first in, first out order.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this PVT sequence.
        """
        return self._device

    @property
    def pvt_id(self) -> int:
        """
        The number that identifies the PVT sequence on the device.
        """
        return self._pvt_id

    @property
    def mode(self) -> PvtMode:
        """
        Current mode of the PVT sequence.
        """
        return self.__retrieve_mode()

    @property
    def axes(self) -> List[PvtAxisDefinition]:
        """
        An array of axes definitions the PVT sequence is set up to control.
        """
        return self.__retrieve_axes()

    @property
    def io(self) -> PvtIo:
        """
        Gets an object that provides access to I/O for this sequence.
        """
        return self._io

    def __init__(self, device: 'Device', pvt_id: int):
        self._device: 'Device' = device
        self._pvt_id: int = pvt_id
        self._io: PvtIo = PvtIo(device, pvt_id)

    def setup_live_composite(
            self,
            *pvt_axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_axes: Definition of the PVT sequence axes.
        """
        request = dto.StreamSetupLiveCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_axes=list(pvt_axes),
        )
        call("device/stream_setup_live_composite", request)

    async def setup_live_composite_async(
            self,
            *pvt_axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_axes: Definition of the PVT sequence axes.
        """
        request = dto.StreamSetupLiveCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_axes=list(pvt_axes),
        )
        await call_async("device/stream_setup_live_composite", request)

    def setup_live(
            self,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = dto.StreamSetupLiveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            axes=list(axes),
        )
        call("device/stream_setup_live", request)

    async def setup_live_async(
            self,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to control the specified axes and to queue actions on the device.

        Args:
            axes: Numbers of physical axes to setup the PVT sequence on.
        """
        request = dto.StreamSetupLiveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            axes=list(axes),
        )
        await call_async("device/stream_setup_live", request)

    def setup_store_composite(
            self,
            pvt_buffer: PvtBuffer,
            *pvt_axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            pvt_axes: Definition of the PVT sequence axes.
        """
        request = dto.StreamSetupStoreCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
            pvt_axes=list(pvt_axes),
        )
        call("device/stream_setup_store_composite", request)

    async def setup_store_composite_async(
            self,
            pvt_buffer: PvtBuffer,
            *pvt_axes: PvtAxisDefinition
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.
        Allows use of lockstep axes in a PVT sequence.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            pvt_axes: Definition of the PVT sequence axes.
        """
        request = dto.StreamSetupStoreCompositeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
            pvt_axes=list(pvt_axes),
        )
        await call_async("device/stream_setup_store_composite", request)

    def setup_store(
            self,
            pvt_buffer: PvtBuffer,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: The axis numbers of the physical axes to setup the PVT sequence on.
        """
        request = dto.StreamSetupStoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
            axes=list(axes),
        )
        call("device/stream_setup_store", request)

    async def setup_store_async(
            self,
            pvt_buffer: PvtBuffer,
            *axes: int
    ) -> None:
        """
        Setup the PVT sequence to use the specified axes and queue actions into a PVT buffer.

        Args:
            pvt_buffer: The PVT buffer to queue actions in.
            axes: The axis numbers of the physical axes to setup the PVT sequence on.
        """
        request = dto.StreamSetupStoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
            axes=list(axes),
        )
        await call_async("device/stream_setup_store", request)

    def call(
            self,
            pvt_buffer: PvtBuffer
    ) -> None:
        """
        Append the actions in a PVT buffer to the sequence's queue.

        Args:
            pvt_buffer: The PVT buffer to call.
        """
        request = dto.StreamCallRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
        )
        call("device/stream_call", request)

    async def call_async(
            self,
            pvt_buffer: PvtBuffer
    ) -> None:
        """
        Append the actions in a PVT buffer to the sequence's queue.

        Args:
            pvt_buffer: The PVT buffer to call.
        """
        request = dto.StreamCallRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            pvt_buffer=pvt_buffer.buffer_number,
        )
        await call_async("device/stream_call", request)

    def point(
            self,
            positions: List[Measurement],
            velocities: List[Optional[Measurement]],
            time: Measurement
    ) -> None:
        """
        Queues a point with absolute coordinates in the PVT sequence.
        If some or all velocities are not provided, the sequence calculates the velocities
        from surrounding points using finite difference.
        If time value is zero, the device must already be idle at the specified position
        and the specified velocity must be zero.
        The last point of the sequence must have defined velocity (likely zero).

        Args:
            positions: Positions for the axes to move through, relative to their home positions.
            velocities: The axes velocities at the given point.
                Specify an empty array or null for specific axes to make the sequence calculate the velocity.
            time: The duration between the previous point in the sequence and this one.
        """
        request = dto.PvtPointRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.ABS,
            positions=positions,
            velocities=velocities,
            time=time,
        )
        call("device/stream_point", request)

    async def point_async(
            self,
            positions: List[Measurement],
            velocities: List[Optional[Measurement]],
            time: Measurement
    ) -> None:
        """
        Queues a point with absolute coordinates in the PVT sequence.
        If some or all velocities are not provided, the sequence calculates the velocities
        from surrounding points using finite difference.
        If time value is zero, the device must already be idle at the specified position
        and the specified velocity must be zero.
        The last point of the sequence must have defined velocity (likely zero).

        Args:
            positions: Positions for the axes to move through, relative to their home positions.
            velocities: The axes velocities at the given point.
                Specify an empty array or null for specific axes to make the sequence calculate the velocity.
            time: The duration between the previous point in the sequence and this one.
        """
        request = dto.PvtPointRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.ABS,
            positions=positions,
            velocities=velocities,
            time=time,
        )
        await call_async("device/stream_point", request)

    def points(
            self,
            positions: List[MeasurementSequence],
            velocities: List[MeasurementSequence],
            times: MeasurementSequence
    ) -> None:
        """
        Deprecated: This method is being replaced by the new SubmitSequenceData method.

        Queues points with absolute coordinates in the PVT sequence.
        Each point must have its time value measured relative to the previous point
        or unexpected behavior will result.

        Note that if the first time value is zero, the device must already be idle at
        the position of the first point and the velocity of that point must be zero.
        All other time values must be greater than zero.

        Args:
            positions: Per-axis sequences of positions.
            velocities: Per-axis sequences of velocities.
                For velocities [v0, v1, ...] and positions [p0, p1, ...], v1 is the target velocity at point p1.
            times: Segment times from one point to another.
                For times [t0, t1, ...] and positions [p0, p1, ...], t1 is the time it takes to move from p0 to p1.
        """
        request = dto.PvtPointsRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.ABS,
            positions=positions,
            velocities=velocities,
            times=times,
        )
        call("device/stream_points", request)

    async def points_async(
            self,
            positions: List[MeasurementSequence],
            velocities: List[MeasurementSequence],
            times: MeasurementSequence
    ) -> None:
        """
        Deprecated: This method is being replaced by the new SubmitSequenceData method.

        Queues points with absolute coordinates in the PVT sequence.
        Each point must have its time value measured relative to the previous point
        or unexpected behavior will result.

        Note that if the first time value is zero, the device must already be idle at
        the position of the first point and the velocity of that point must be zero.
        All other time values must be greater than zero.

        Args:
            positions: Per-axis sequences of positions.
            velocities: Per-axis sequences of velocities.
                For velocities [v0, v1, ...] and positions [p0, p1, ...], v1 is the target velocity at point p1.
            times: Segment times from one point to another.
                For times [t0, t1, ...] and positions [p0, p1, ...], t1 is the time it takes to move from p0 to p1.
        """
        request = dto.PvtPointsRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.ABS,
            positions=positions,
            velocities=velocities,
            times=times,
        )
        await call_async("device/stream_points", request)

    def point_relative(
            self,
            positions: List[Measurement],
            velocities: List[Optional[Measurement]],
            time: Measurement
    ) -> None:
        """
        Queues a point with coordinates relative to the previous point in the PVT sequence.
        If some or all velocities are not provided, the sequence calculates the velocities
        from surrounding points using finite difference.

        The time value must be greater than zero, and each point must have its time value
        measured relative to the previous point or unexpected behavior will result.

        The last point of the sequence must have defined velocity (likely zero).

        Args:
            positions: Positions for the axes to move through, relative to the previous point.
            velocities: The axes velocities at the given point.
                Specify an empty array or null for specific axes to make the sequence calculate the velocity.
            time: The duration between the previous point in the sequence and this one.
        """
        request = dto.PvtPointRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.REL,
            positions=positions,
            velocities=velocities,
            time=time,
        )
        call("device/stream_point", request)

    async def point_relative_async(
            self,
            positions: List[Measurement],
            velocities: List[Optional[Measurement]],
            time: Measurement
    ) -> None:
        """
        Queues a point with coordinates relative to the previous point in the PVT sequence.
        If some or all velocities are not provided, the sequence calculates the velocities
        from surrounding points using finite difference.

        The time value must be greater than zero, and each point must have its time value
        measured relative to the previous point or unexpected behavior will result.

        The last point of the sequence must have defined velocity (likely zero).

        Args:
            positions: Positions for the axes to move through, relative to the previous point.
            velocities: The axes velocities at the given point.
                Specify an empty array or null for specific axes to make the sequence calculate the velocity.
            time: The duration between the previous point in the sequence and this one.
        """
        request = dto.PvtPointRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.REL,
            positions=positions,
            velocities=velocities,
            time=time,
        )
        await call_async("device/stream_point", request)

    def points_relative(
            self,
            positions: List[MeasurementSequence],
            velocities: List[MeasurementSequence],
            times: MeasurementSequence
    ) -> None:
        """
        Deprecated: This method is being replaced by the new SubmitSequenceData method.

        Queues points with coordinates relative to the previous point in the PVT sequence.
        All time values must be greater than zero and each point must have its time value
        measured relative to the previous point or unexpected behavior will result.

        Args:
            positions: Per-axis sequences of positions.
            velocities: Per-axis sequences of velocities.
                For velocities [v0, v1, ...] and positions [p0, p1, ...], v1 is the target velocity at point p1.
            times: Segment times from one point to another.
                For times [t0, t1, ...] and positions [p0, p1, ...], t1 is the time it takes to move from p0 to p1.
        """
        request = dto.PvtPointsRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.REL,
            positions=positions,
            velocities=velocities,
            times=times,
        )
        call("device/stream_points", request)

    async def points_relative_async(
            self,
            positions: List[MeasurementSequence],
            velocities: List[MeasurementSequence],
            times: MeasurementSequence
    ) -> None:
        """
        Deprecated: This method is being replaced by the new SubmitSequenceData method.

        Queues points with coordinates relative to the previous point in the PVT sequence.
        All time values must be greater than zero and each point must have its time value
        measured relative to the previous point or unexpected behavior will result.

        Args:
            positions: Per-axis sequences of positions.
            velocities: Per-axis sequences of velocities.
                For velocities [v0, v1, ...] and positions [p0, p1, ...], v1 is the target velocity at point p1.
            times: Segment times from one point to another.
                For times [t0, t1, ...] and positions [p0, p1, ...], t1 is the time it takes to move from p0 to p1.
        """
        request = dto.PvtPointsRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            type=dto.StreamSegmentType.REL,
            positions=positions,
            velocities=velocities,
            times=times,
        )
        await call_async("device/stream_points", request)

    @staticmethod
    def generate_velocities(
            sequence_items: List[PvtPartialSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Generates velocities for a sequence of positions and times, and (optionally) a partially defined sequence
        of velocities. Note that if some velocities are defined, the solver will NOT modify them in any way.
        If all velocities are defined, the solver will simply return the same velocities.
        This function calculates velocities by enforcing that acceleration be continuous at each segment transition.
        The function does not modify the input positions or times.

        Also note that if the first position is relative, all following points must be relative.
        If the start position is absolute, then the sequence can include a mix of relative and absolute positions.
        Additionally, all times must be relative to the previous point.
        Please see the ConvertTimeAbsoluteToRelativePartial function for conversions.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the positions, optional velocities, and times for the sequence.
                Each point should have positions defined for each axis. Velocities are optional.
                Times must be defined for each point.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        request = dto.PvtGenerateVelocitiesRequest(
            sequence_items=sequence_items,
        )
        response = call(
            "device/pvt_generate_velocities",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def generate_velocities_async(
            sequence_items: List[PvtPartialSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Generates velocities for a sequence of positions and times, and (optionally) a partially defined sequence
        of velocities. Note that if some velocities are defined, the solver will NOT modify them in any way.
        If all velocities are defined, the solver will simply return the same velocities.
        This function calculates velocities by enforcing that acceleration be continuous at each segment transition.
        The function does not modify the input positions or times.

        Also note that if the first position is relative, all following points must be relative.
        If the start position is absolute, then the sequence can include a mix of relative and absolute positions.
        Additionally, all times must be relative to the previous point.
        Please see the ConvertTimeAbsoluteToRelativePartial function for conversions.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the positions, optional velocities, and times for the sequence.
                Each point should have positions defined for each axis. Velocities are optional.
                Times must be defined for each point.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        request = dto.PvtGenerateVelocitiesRequest(
            sequence_items=sequence_items,
        )
        response = await call_async(
            "device/pvt_generate_velocities",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    @staticmethod
    def generate_positions(
            sequence_items: List[PvtPartialSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Generates positions for a sequence of velocities and times. This function calculates
        positions by enforcing that acceleration be continuous at each segment transition.

        This function does not modify the input velocities or times, and outputs absolute
        positions. If your initial point has a time of zero, it will be considered a starting
        position when submitted to the device, and you must already have moved the device
        to that position. Additionally, all times must be relative to the previous point.
        Please see the ConvertTimeAbsoluteToRelativePartial function for conversions.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the velocities and times for the sequence.
                Each point should have velocities defined for each axis.
                Times must be defined for each point.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        request = dto.PvtGeneratePositionsRequest(
            sequence_items=sequence_items,
        )
        response = call(
            "device/pvt_generate_positions",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def generate_positions_async(
            sequence_items: List[PvtPartialSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Generates positions for a sequence of velocities and times. This function calculates
        positions by enforcing that acceleration be continuous at each segment transition.

        This function does not modify the input velocities or times, and outputs absolute
        positions. If your initial point has a time of zero, it will be considered a starting
        position when submitted to the device, and you must already have moved the device
        to that position. Additionally, all times must be relative to the previous point.
        Please see the ConvertTimeAbsoluteToRelativePartial function for conversions.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the velocities and times for the sequence.
                Each point should have velocities defined for each axis.
                Times must be defined for each point.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        request = dto.PvtGeneratePositionsRequest(
            sequence_items=sequence_items,
        )
        response = await call_async(
            "device/pvt_generate_positions",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    @staticmethod
    def generate_velocities_and_times(
            sequence_items: List[PvtPartialSequenceItem],
            target_speed: Measurement,
            target_acceleration: Measurement,
            resample_number: Optional[int] = None
    ) -> List[PvtSequenceItem]:
        """
        Generates sequences of velocities and times for a sequence of positions.
        This function fits a geometric spline (not-a-knot cubic for sequences of >3 points,
        natural cubic for 3, and a straight line for 2) over the position sequence
        and then calculates the velocity and time information by traversing it using a
        trapezoidal motion profile.

        This generation scheme attempts to keep speed and acceleration less than the
        specified target values, but does not guarantee it. Generally speaking, a higher
        resample number will bring the generated trajectory closer to respecting these
        limits.

        Note that consecutive duplicate points will be automatically removed as they
        have no geometric significance without additional time information. Also note that
        for multi-dimensional paths this function expects axes to be linear and orthogonal,
        however for paths of a single dimension rotary units are accepted.
        Additionally, if the first positions of the input sequence is relative,
        all following positions must also be relative. If the first position is absolute,
        the sequence may contain a mix of relative and absolute positions.
        Resampling a sequence which contains relative positions is not allowed.

        This function outputs points with absolute positions and relative times, with the
        first time equal to zero, meaning it will be treated as a start position when
        executing on a device. You must move the device to that position before submitting
        the sequence, or change the first point's time to a value greater than zero.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the positions for the sequence.
                Each point should have positions defined for each axis.
            target_speed: The target speed used to generate positions and times.
            target_acceleration: The target acceleration used to generate positions and times.
            resample_number: The number of points to resample the sequence by.
                Leave undefined to use the specified points.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        if target_speed.value <= 0 or target_acceleration.value <= 0:
            raise ValueError('Target speed and acceleration values must be greater than zero.')

        request = dto.PvtGenerateVelocitiesAndTimesRequest(
            sequence_items=sequence_items,
            target_speed=target_speed,
            target_acceleration=target_acceleration,
            resample_number=resample_number,
        )
        response = call(
            "device/pvt_generate_velocities_and_times",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def generate_velocities_and_times_async(
            sequence_items: List[PvtPartialSequenceItem],
            target_speed: Measurement,
            target_acceleration: Measurement,
            resample_number: Optional[int] = None
    ) -> List[PvtSequenceItem]:
        """
        Generates sequences of velocities and times for a sequence of positions.
        This function fits a geometric spline (not-a-knot cubic for sequences of >3 points,
        natural cubic for 3, and a straight line for 2) over the position sequence
        and then calculates the velocity and time information by traversing it using a
        trapezoidal motion profile.

        This generation scheme attempts to keep speed and acceleration less than the
        specified target values, but does not guarantee it. Generally speaking, a higher
        resample number will bring the generated trajectory closer to respecting these
        limits.

        Note that consecutive duplicate points will be automatically removed as they
        have no geometric significance without additional time information. Also note that
        for multi-dimensional paths this function expects axes to be linear and orthogonal,
        however for paths of a single dimension rotary units are accepted.
        Additionally, if the first positions of the input sequence is relative,
        all following positions must also be relative. If the first position is absolute,
        the sequence may contain a mix of relative and absolute positions.
        Resampling a sequence which contains relative positions is not allowed.

        This function outputs points with absolute positions and relative times, with the
        first time equal to zero, meaning it will be treated as a start position when
        executing on a device. You must move the device to that position before submitting
        the sequence, or change the first point's time to a value greater than zero.

        Does not support native units.

        Args:
            sequence_items: Partial PVT points defining the positions for the sequence.
                Each point should have positions defined for each axis.
            target_speed: The target speed used to generate positions and times.
            target_acceleration: The target acceleration used to generate positions and times.
            resample_number: The number of points to resample the sequence by.
                Leave undefined to use the specified points.

        Returns:
            Array of points and actions containing the generated PVT sequence. Note returned times are always relative.
        """
        if target_speed.value <= 0 or target_acceleration.value <= 0:
            raise ValueError('Target speed and acceleration values must be greater than zero.')

        request = dto.PvtGenerateVelocitiesAndTimesRequest(
            sequence_items=sequence_items,
            target_speed=target_speed,
            target_acceleration=target_acceleration,
            resample_number=resample_number,
        )
        response = await call_async(
            "device/pvt_generate_velocities_and_times",
            request,
            dto.PvtGenerateSequenceResponse.from_binary)
        return response.sequence_data

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live PVT sequence executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.StreamWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            throw_error_on_fault=throw_error_on_fault,
        )
        call("device/stream_wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the live PVT sequence executes all queued actions.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.StreamWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("device/stream_wait_until_idle", request)

    def cork(
            self
    ) -> None:
        """
        Cork the front of the PVT sequences's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent PVT commands reaching the device late.
        You can only cork an idle live PVT sequence.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        call("device/stream_cork", request)

    async def cork_async(
            self
    ) -> None:
        """
        Cork the front of the PVT sequences's action queue, blocking execution.
        Execution resumes upon uncorking the queue, or when the number of queued actions reaches its limit.
        Corking eliminates discontinuities in motion due to subsequent PVT commands reaching the device late.
        You can only cork an idle live PVT sequence.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        await call_async("device/stream_cork", request)

    def uncork(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live PVT sequence that is corked.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        call("device/stream_uncork", request)

    async def uncork_async(
            self
    ) -> None:
        """
        Uncork the front of the queue, unblocking command execution.
        You can only uncork an idle live PVT sequence that is corked.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        await call_async("device/stream_uncork", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns a boolean value indicating whether the live PVT sequence is executing a queued action.

        Returns:
            True if the PVT sequence is executing a queued action.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
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
        Returns a boolean value indicating whether the live PVT sequence is executing a queued action.

        Returns:
            True if the PVT sequence is executing a queued action.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        response = await call_async(
            "device/stream_is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string which represents the PVT sequence.

        Returns:
            String which represents the PVT sequence.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
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
        Disables the PVT sequence.
        If the PVT sequence is not setup, this command does nothing.
        Once disabled, the PVT sequence will no longer accept PVT commands.
        The PVT sequence will process the rest of the commands in the queue until it is empty.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        call("device/stream_disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disables the PVT sequence.
        If the PVT sequence is not setup, this command does nothing.
        Once disabled, the PVT sequence will no longer accept PVT commands.
        The PVT sequence will process the rest of the commands in the queue until it is empty.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        await call_async("device/stream_disable", request)

    def generic_command(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the PVT sequence.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = dto.StreamGenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            command=command,
        )
        call("device/stream_generic_command", request)

    async def generic_command_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to the PVT sequence.
        Keeps resending the command while the device rejects with AGAIN reason.

        Args:
            command: Command and its parameters.
        """
        request = dto.StreamGenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            command=command,
        )
        await call_async("device/stream_generic_command", request)

    def generic_command_batch(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the PVT sequence.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = dto.StreamGenericCommandBatchRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            batch=batch,
        )
        call("device/stream_generic_command_batch", request)

    async def generic_command_batch_async(
            self,
            batch: List[str]
    ) -> None:
        """
        Sends a batch of generic ASCII commands to the PVT sequence.
        Keeps resending command while the device rejects with AGAIN reason.
        The batch is atomic in terms of thread safety.

        Args:
            batch: Array of commands.
        """
        request = dto.StreamGenericCommandBatchRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
            batch=batch,
        )
        await call_async("device/stream_generic_command_batch", request)

    def check_disabled(
            self
    ) -> bool:
        """
        Queries the PVT sequence status from the device
        and returns boolean indicating whether the PVT sequence is disabled.
        Useful to determine if execution was interrupted by other movements.

        Returns:
            True if the PVT sequence is disabled.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
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
        Queries the PVT sequence status from the device
        and returns boolean indicating whether the PVT sequence is disabled.
        Useful to determine if execution was interrupted by other movements.

        Returns:
            True if the PVT sequence is disabled.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
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
        Makes the PVT sequence throw PvtDiscontinuityException when it encounters discontinuities (ND warning flag).
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        call_sync("device/stream_treat_discontinuities", request)

    def ignore_current_discontinuity(
            self
    ) -> None:
        """
        Prevents PvtDiscontinuityException as a result of expected discontinuity when resuming the sequence.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        call_sync("device/stream_ignore_discontinuity", request)

    def __retrieve_axes(
            self
    ) -> List[PvtAxisDefinition]:
        """
        Gets the axes of the PVT sequence.

        Returns:
            An array of axis numbers of the axes the PVT sequence is set up to control.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        response = call_sync(
            "device/stream_get_axes",
            request,
            dto.StreamGetAxesResponse.from_binary)
        return response.pvt_axes

    def __retrieve_mode(
            self
    ) -> PvtMode:
        """
        Get the mode of the PVT sequence.

        Returns:
            Mode of the PVT sequence.
        """
        request = dto.StreamEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            pvt=True,
        )
        response = call_sync(
            "device/stream_get_mode",
            request,
            dto.StreamModeResponse.from_binary)
        return response.pvt_mode

    @staticmethod
    def save_sequence_data(
            sequence_data: List[PvtSequenceItem],
            path: str,
            dimension_names: Optional[List[str]] = None
    ) -> None:
        """
        Saves PvtSequenceItem array as a csv file.
        Save format is compatible with Zaber Launcher PVT Editor App.

        Normally a sequence in memory should have relative time values on the points.
        If you want to store absolute times instead, you can use the
        ConvertTimeRelativeToAbsolute function to convert before saving.

        Throws InvalidArgumentException if fields are undefined or inconsistent.
        For example, position and velocity arrays must have the same dimensions.
        Sequence lengths must be consistent for positions, velocities and times.

        Args:
            sequence_data: The PVT sequence data to save.
            path: The path to save the file to.
            dimension_names: Optional csv column names for each series.
                If not provided, the default names will be used: Series 1, Series 2, etc..
                Length of this array must be equal to number of dimensions in sequence data.
        """
        request = dto.PvtSaveCsvRequest(
            sequence_data=sequence_data,
            path=path,
            dimension_names=dimension_names,
        )
        call("device/stream_pvt_save_csv", request)

    @staticmethod
    async def save_sequence_data_async(
            sequence_data: List[PvtSequenceItem],
            path: str,
            dimension_names: Optional[List[str]] = None
    ) -> None:
        """
        Saves PvtSequenceItem array as a csv file.
        Save format is compatible with Zaber Launcher PVT Editor App.

        Normally a sequence in memory should have relative time values on the points.
        If you want to store absolute times instead, you can use the
        ConvertTimeRelativeToAbsolute function to convert before saving.

        Throws InvalidArgumentException if fields are undefined or inconsistent.
        For example, position and velocity arrays must have the same dimensions.
        Sequence lengths must be consistent for positions, velocities and times.

        Args:
            sequence_data: The PVT sequence data to save.
            path: The path to save the file to.
            dimension_names: Optional csv column names for each series.
                If not provided, the default names will be used: Series 1, Series 2, etc..
                Length of this array must be equal to number of dimensions in sequence data.
        """
        request = dto.PvtSaveCsvRequest(
            sequence_data=sequence_data,
            path=path,
            dimension_names=dimension_names,
        )
        await call_async("device/stream_pvt_save_csv", request)

    @staticmethod
    def load_sequence_data(
            path: str
    ) -> PvtCsvData:
        """
        Load PVT Sequence data from CSV file.
        This function expects complete data in the CSV files (a time column and
        both position and velocity columns for each series).
        If your CSV file has partial data, use LoadPartialSequenceData instead.

        The CSV data can include a header (recommended).
        There are two possible header formats:

        1. A time column with named position and velocity columns.
        For example, "Time (ms),X Position (cm),X Velocity (cm/s),...".
        In this case, position, velocity and time columns are all optional.
        Also, order does not matter, but position and velocity names must be consistent.
        This is our recommended CSV format.

        2. A time column with alternating position and velocity columns.
        For example, "Time (ms),Position (cm),Velocity (cm/s),...".
        In this case, only the time column is optional and order does matter.

        Units must be wrapped in parens or square braces: ie. (µm/s), [µm/s].
        Additionally, native units are the default if no units are specified.
        Time values default to milliseconds if no units are provided.
        If no header is included, then column order is assumed to be "T,P1,V1,P2,V2,...".
        In this case the number of columns must be odd.

        Users can add a column named "Relative" with true/false values to
        indicate whether each point's position is relative or absolute.
        If this column is not included, all points will be assumed to be absolute.

        If the first point has time = zero, it is considered the start position
        and treated specially. It must have an absolute position, and the device
        must already be idle at that position when the sequence is submitted.
        The velocity of the start position is ignored, and should normally be zero.
        Sequences with nonzero time for the first point do not have these constraints.

        Buffer calls and I/O actions can be added into the CSV file by
        adding a column titled "Actions", containing the ASCII protocol command(s)
        shortened by everything up to the PVT stream number, for example
        "call 2" or "io set do 1 1". If you want to insert multiple actions
        after a point, put them in the same cell separated by a semicolon.
        See the ASCII Protocol Manual
        PVT command reference (https://www.zaber.com/protocol-manual?protocol=ASCII#topic_command_pvt)
        section for the list of available commands. Unit symbols are not supported;
        analog output voltages are always in volts and schedule delay times are
        always in milliseconds.

        Note that the Relative and Actions columns are not automatically
        detected, so if you include them you must include a header row.

        Time values should always be relative when sent to a device or to the
        various Generate... functions on this class. If you want to store
        absolute times in a CSV file, you can use the ConvertTimeRelativeToAbsolute
        function to convert after loading the file.

        Args:
            path: The path to the csv file to load.

        Returns:
            The PVT csv data loaded from the file.
        """
        request = dto.PvtLoadCsvRequest(
            path=path,
        )
        response = call(
            "device/stream_pvt_load_csv",
            request,
            PvtCsvData.from_binary)
        return response

    @staticmethod
    async def load_sequence_data_async(
            path: str
    ) -> PvtCsvData:
        """
        Load PVT Sequence data from CSV file.
        This function expects complete data in the CSV files (a time column and
        both position and velocity columns for each series).
        If your CSV file has partial data, use LoadPartialSequenceData instead.

        The CSV data can include a header (recommended).
        There are two possible header formats:

        1. A time column with named position and velocity columns.
        For example, "Time (ms),X Position (cm),X Velocity (cm/s),...".
        In this case, position, velocity and time columns are all optional.
        Also, order does not matter, but position and velocity names must be consistent.
        This is our recommended CSV format.

        2. A time column with alternating position and velocity columns.
        For example, "Time (ms),Position (cm),Velocity (cm/s),...".
        In this case, only the time column is optional and order does matter.

        Units must be wrapped in parens or square braces: ie. (µm/s), [µm/s].
        Additionally, native units are the default if no units are specified.
        Time values default to milliseconds if no units are provided.
        If no header is included, then column order is assumed to be "T,P1,V1,P2,V2,...".
        In this case the number of columns must be odd.

        Users can add a column named "Relative" with true/false values to
        indicate whether each point's position is relative or absolute.
        If this column is not included, all points will be assumed to be absolute.

        If the first point has time = zero, it is considered the start position
        and treated specially. It must have an absolute position, and the device
        must already be idle at that position when the sequence is submitted.
        The velocity of the start position is ignored, and should normally be zero.
        Sequences with nonzero time for the first point do not have these constraints.

        Buffer calls and I/O actions can be added into the CSV file by
        adding a column titled "Actions", containing the ASCII protocol command(s)
        shortened by everything up to the PVT stream number, for example
        "call 2" or "io set do 1 1". If you want to insert multiple actions
        after a point, put them in the same cell separated by a semicolon.
        See the ASCII Protocol Manual
        PVT command reference (https://www.zaber.com/protocol-manual?protocol=ASCII#topic_command_pvt)
        section for the list of available commands. Unit symbols are not supported;
        analog output voltages are always in volts and schedule delay times are
        always in milliseconds.

        Note that the Relative and Actions columns are not automatically
        detected, so if you include them you must include a header row.

        Time values should always be relative when sent to a device or to the
        various Generate... functions on this class. If you want to store
        absolute times in a CSV file, you can use the ConvertTimeRelativeToAbsolute
        function to convert after loading the file.

        Args:
            path: The path to the csv file to load.

        Returns:
            The PVT csv data loaded from the file.
        """
        request = dto.PvtLoadCsvRequest(
            path=path,
        )
        response = await call_async(
            "device/stream_pvt_load_csv",
            request,
            PvtCsvData.from_binary)
        return response

    @staticmethod
    def load_partial_sequence_data(
            path: str
    ) -> PvtPartialCsvData:
        """
        Load PVT Sequence data from CSV file, allowing for some combinations of incomplete data.
        Output from this function cannot be enqueued on a device until the missing data has
        been filled in using the GenerateVelocities, GeneratePositions or
        GenerateVelocitiesAndTimes functions.

        The CSV data can include a header (recommended).
        There are two possible header formats:

        1. A time column with named position and velocity columns.
        For example, "Time (ms),X Position (cm),X Velocity (cm/s),...".
        In this case, position, velocity and time columns are all optional.
        Also, order does not matter, but position and velocity names must be consistent.
        This is our recommended CSV format.

        2. A time column with alternating position and velocity columns.
        For example, "Time (ms),Position (cm),Velocity (cm/s),...".
        In this case, only the time column is optional and order does matter.

        Units must be wrapped in parens or square braces: ie. (µm/s), [µm/s].
        Additionally, native units are the default if no units are specified.
        Time values default to milliseconds if no units are provided.
        If no header is included, then column order is assumed to be "T,P1,V1,P2,V2,...".
        In this case the number of columns must be odd.

        Users can add a column named "Relative" with true/false values to
        indicate whether each point's position is relative or absolute.
        If this column is not included, all points will be assumed to be absolute.

        If the first point has time = zero, it is considered the start position
        and treated specially. It must have an absolute position, and the device
        must already be idle at that position when the sequence is submitted.
        The velocity of the start position is ignored, and should normally be zero.
        Sequences with nonzero time for the first point do not have these constraints.

        Buffer calls and I/O actions can be added into the CSV file by
        adding a column titled "Actions", containing the ASCII protocol command(s)
        shortened by everything up to the PVT stream number, for example
        "call 2" or "io set do 1 1". If you want to insert multiple actions
        after a point, put them in the same cell separated by a semicolon.
        See the ASCII Protocol Manual
        PVT command reference (https://www.zaber.com/protocol-manual?protocol=ASCII#topic_command_pvt)
        section for the list of available commands. Unit symbols are not supported;
        analog output voltages are always in volts and schedule delay times are
        always in milliseconds.

        Note that the Relative and Actions columns are not automatically
        detected, so if you include them you must include a header row.

        Time values should always be relative when sent to a device or to the
        various Generate... functions on this class. If you want to store
        absolute times in a CSV file, you can use the ConvertTimeRelativeToAbsolute
        function to convert after loading the file.

        Args:
            path: The path to the csv file to load.

        Returns:
            The PVT csv data loaded from the file.
        """
        request = dto.PvtLoadCsvRequest(
            path=path,
        )
        response = call(
            "device/stream_pvt_load_partial_csv",
            request,
            PvtPartialCsvData.from_binary)
        return response

    @staticmethod
    async def load_partial_sequence_data_async(
            path: str
    ) -> PvtPartialCsvData:
        """
        Load PVT Sequence data from CSV file, allowing for some combinations of incomplete data.
        Output from this function cannot be enqueued on a device until the missing data has
        been filled in using the GenerateVelocities, GeneratePositions or
        GenerateVelocitiesAndTimes functions.

        The CSV data can include a header (recommended).
        There are two possible header formats:

        1. A time column with named position and velocity columns.
        For example, "Time (ms),X Position (cm),X Velocity (cm/s),...".
        In this case, position, velocity and time columns are all optional.
        Also, order does not matter, but position and velocity names must be consistent.
        This is our recommended CSV format.

        2. A time column with alternating position and velocity columns.
        For example, "Time (ms),Position (cm),Velocity (cm/s),...".
        In this case, only the time column is optional and order does matter.

        Units must be wrapped in parens or square braces: ie. (µm/s), [µm/s].
        Additionally, native units are the default if no units are specified.
        Time values default to milliseconds if no units are provided.
        If no header is included, then column order is assumed to be "T,P1,V1,P2,V2,...".
        In this case the number of columns must be odd.

        Users can add a column named "Relative" with true/false values to
        indicate whether each point's position is relative or absolute.
        If this column is not included, all points will be assumed to be absolute.

        If the first point has time = zero, it is considered the start position
        and treated specially. It must have an absolute position, and the device
        must already be idle at that position when the sequence is submitted.
        The velocity of the start position is ignored, and should normally be zero.
        Sequences with nonzero time for the first point do not have these constraints.

        Buffer calls and I/O actions can be added into the CSV file by
        adding a column titled "Actions", containing the ASCII protocol command(s)
        shortened by everything up to the PVT stream number, for example
        "call 2" or "io set do 1 1". If you want to insert multiple actions
        after a point, put them in the same cell separated by a semicolon.
        See the ASCII Protocol Manual
        PVT command reference (https://www.zaber.com/protocol-manual?protocol=ASCII#topic_command_pvt)
        section for the list of available commands. Unit symbols are not supported;
        analog output voltages are always in volts and schedule delay times are
        always in milliseconds.

        Note that the Relative and Actions columns are not automatically
        detected, so if you include them you must include a header row.

        Time values should always be relative when sent to a device or to the
        various Generate... functions on this class. If you want to store
        absolute times in a CSV file, you can use the ConvertTimeRelativeToAbsolute
        function to convert after loading the file.

        Args:
            path: The path to the csv file to load.

        Returns:
            The PVT csv data loaded from the file.
        """
        request = dto.PvtLoadCsvRequest(
            path=path,
        )
        response = await call_async(
            "device/stream_pvt_load_partial_csv",
            request,
            PvtPartialCsvData.from_binary)
        return response

    def submit_sequence_data(
            self,
            sequence_data: List[PvtSequenceItem]
    ) -> None:
        """
        Writes the contents of a PvtSequenceItem array to the sequence.
        Each point must have its time value measured relative to the previous point
        or unexpected behavior will result. If your point times are absolute (measured
        from the start of the sequence), use the ConvertTimeAbsoluteToRelative
        function to convert them before submitting.

        If the first point in the sequence has a time value of zero, it is
        considered the starting position. It must have an absolute position,
        zero velocity, and the device must already be idle at the specified position.

        Args:
            sequence_data: The PVT sequence data to submit.
        """
        request = dto.PvtSubmitSequenceDataRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            sequence_data=sequence_data,
        )
        call("device/stream_pvt_submit_sequence_data", request)

    async def submit_sequence_data_async(
            self,
            sequence_data: List[PvtSequenceItem]
    ) -> None:
        """
        Writes the contents of a PvtSequenceItem array to the sequence.
        Each point must have its time value measured relative to the previous point
        or unexpected behavior will result. If your point times are absolute (measured
        from the start of the sequence), use the ConvertTimeAbsoluteToRelative
        function to convert them before submitting.

        If the first point in the sequence has a time value of zero, it is
        considered the starting position. It must have an absolute position,
        zero velocity, and the device must already be idle at the specified position.

        Args:
            sequence_data: The PVT sequence data to submit.
        """
        request = dto.PvtSubmitSequenceDataRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            stream_id=self.pvt_id,
            sequence_data=sequence_data,
        )
        await call_async("device/stream_pvt_submit_sequence_data", request)

    @staticmethod
    def convert_time_absolute_to_relative(
            sequence_data: List[PvtSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Converts the time values in a PvtSequenceItem array from absolute to relative.
        Points passed to the Generate functions or sent to devices must have relative time values.

        Args:
            sequence_data: The sequence data for which to convert times from absolute to relative.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from absolute to relative.
        """
        request = dto.PvtConvertTimeRequest(
            from_absolute=True,
            sequence_data=sequence_data,
        )
        response = call(
            "device/stream_pvt_convert_time",
            request,
            dto.PvtConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def convert_time_absolute_to_relative_async(
            sequence_data: List[PvtSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Converts the time values in a PvtSequenceItem array from absolute to relative.
        Points passed to the Generate functions or sent to devices must have relative time values.

        Args:
            sequence_data: The sequence data for which to convert times from absolute to relative.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from absolute to relative.
        """
        request = dto.PvtConvertTimeRequest(
            from_absolute=True,
            sequence_data=sequence_data,
        )
        response = await call_async(
            "device/stream_pvt_convert_time",
            request,
            dto.PvtConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    def convert_time_relative_to_absolute(
            sequence_data: List[PvtSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Converts the time values in a PvtSequenceItem array from relative to absolute.

        Args:
            sequence_data: The sequence data for which to convert times from relative to absolute.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from relative to absolute.
        """
        request = dto.PvtConvertTimeRequest(
            from_absolute=False,
            sequence_data=sequence_data,
        )
        response = call(
            "device/stream_pvt_convert_time",
            request,
            dto.PvtConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def convert_time_relative_to_absolute_async(
            sequence_data: List[PvtSequenceItem]
    ) -> List[PvtSequenceItem]:
        """
        Converts the time values in a PvtSequenceItem array from relative to absolute.

        Args:
            sequence_data: The sequence data for which to convert times from relative to absolute.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from relative to absolute.
        """
        request = dto.PvtConvertTimeRequest(
            from_absolute=False,
            sequence_data=sequence_data,
        )
        response = await call_async(
            "device/stream_pvt_convert_time",
            request,
            dto.PvtConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    def convert_time_absolute_to_relative_partial(
            sequence_data: List[PvtPartialSequenceItem]
    ) -> List[PvtPartialSequenceItem]:
        """
        Converts the time values in a PvtPartialSequenceItem array from absolute to relative.
        Points passed to the Generate functions or sent to devices must have relative time values.

        Args:
            sequence_data: The sequence data for which to convert times from absolute to relative.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from absolute to relative.
        """
        request = dto.PvtPartialConvertTimeRequest(
            from_absolute=True,
            sequence_data=sequence_data,
        )
        response = call(
            "device/stream_pvt_convert_time_partial",
            request,
            dto.PvtPartialConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def convert_time_absolute_to_relative_partial_async(
            sequence_data: List[PvtPartialSequenceItem]
    ) -> List[PvtPartialSequenceItem]:
        """
        Converts the time values in a PvtPartialSequenceItem array from absolute to relative.
        Points passed to the Generate functions or sent to devices must have relative time values.

        Args:
            sequence_data: The sequence data for which to convert times from absolute to relative.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from absolute to relative.
        """
        request = dto.PvtPartialConvertTimeRequest(
            from_absolute=True,
            sequence_data=sequence_data,
        )
        response = await call_async(
            "device/stream_pvt_convert_time_partial",
            request,
            dto.PvtPartialConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    def convert_time_relative_to_absolute_partial(
            sequence_data: List[PvtPartialSequenceItem]
    ) -> List[PvtPartialSequenceItem]:
        """
        Converts the time values in a PvtPartialSequenceItem array from relative to absolute.

        Args:
            sequence_data: The sequence data for which to convert times from relative to absolute.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from relative to absolute.
        """
        request = dto.PvtPartialConvertTimeRequest(
            from_absolute=False,
            sequence_data=sequence_data,
        )
        response = call(
            "device/stream_pvt_convert_time_partial",
            request,
            dto.PvtPartialConvertTimeResponse.from_binary)
        return response.sequence_data

    @staticmethod
    async def convert_time_relative_to_absolute_partial_async(
            sequence_data: List[PvtPartialSequenceItem]
    ) -> List[PvtPartialSequenceItem]:
        """
        Converts the time values in a PvtPartialSequenceItem array from relative to absolute.

        Args:
            sequence_data: The sequence data for which to convert times from relative to absolute.
                Point times must all be in the same units.

        Returns:
            The sequence data with times converted from relative to absolute.
        """
        request = dto.PvtPartialConvertTimeRequest(
            from_absolute=False,
            sequence_data=sequence_data,
        )
        response = await call_async(
            "device/stream_pvt_convert_time_partial",
            request,
            dto.PvtPartialConvertTimeResponse.from_binary)
        return response.sequence_data
