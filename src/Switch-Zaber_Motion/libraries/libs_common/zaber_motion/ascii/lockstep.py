# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..units import Units, LengthUnits, VelocityUnits, AccelerationUnits, TimeUnits

if TYPE_CHECKING:
    from .device import Device


class Lockstep:
    """
    Represents a lockstep group with this ID on a device.
    A lockstep group is a movement synchronized pair of axes on a device.
    Requires at least Firmware 6.15 or 7.11.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this lockstep group.
        """
        return self._device

    @property
    def lockstep_group_id(self) -> int:
        """
        The number that identifies the lockstep group on the device.
        """
        return self._lockstep_group_id

    def __init__(self, device: 'Device', lockstep_group_id: int):
        self._device: 'Device' = device
        self._lockstep_group_id: int = lockstep_group_id

    def enable(
            self,
            *axes: int
    ) -> None:
        """
        Activate the lockstep group on the axes specified.

        Args:
            axes: The numbers of axes in the lockstep group.
        """
        request = dto.LockstepEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            axes=list(axes),
        )
        call("device/lockstep_enable", request)

    async def enable_async(
            self,
            *axes: int
    ) -> None:
        """
        Activate the lockstep group on the axes specified.

        Args:
            axes: The numbers of axes in the lockstep group.
        """
        request = dto.LockstepEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            axes=list(axes),
        )
        await call_async("device/lockstep_enable", request)

    def disable(
            self
    ) -> None:
        """
        Disable the lockstep group.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        call("device/lockstep_disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disable the lockstep group.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        await call_async("device/lockstep_disable", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing lockstep group movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        call("device/lockstep_stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing lockstep group movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/lockstep_stop", request)

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Retracts the axes of the lockstep group until a home associated with an individual axis is detected.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        call("device/lockstep_home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Retracts the axes of the lockstep group until a home associated with an individual axis is detected.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/lockstep_home", request)

    def move_absolute(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Move the first axis of the lockstep group to an absolute position.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/lockstep_move", request)

    async def move_absolute_async(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Move the first axis of the lockstep group to an absolute position.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/lockstep_move", request)

    def move_relative(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Move the first axis of the lockstep group to a position relative to its current position.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/lockstep_move", request)

    async def move_relative_async(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Move the first axis of the lockstep group to a position relative to its current position.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/lockstep_move", request)

    def move_velocity(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the first axis of the lockstep group at the specified speed.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/lockstep_move", request)

    async def move_velocity_async(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the first axis of the lockstep group at the specified speed.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/lockstep_move", request)

    def move_sin(
            self,
            amplitude: float,
            amplitude_units: LengthUnits,
            period: float,
            period_units: TimeUnits,
            count: float = 0,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the first axis of the lockstep group in a sinusoidal trajectory.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            amplitude: Amplitude of the sinusoidal motion (half of the motion's peak-to-peak range).
            amplitude_units: Units of position.
            period: Period of the sinusoidal motion in milliseconds.
            period_units: Units of time.
            count: Number of sinusoidal cycles to complete.
                Must be a multiple of 0.5
                If count is not specified or set to 0, the axis will move indefinitely.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepMoveSinRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            amplitude=amplitude,
            amplitude_units=amplitude_units,
            period=period,
            period_units=period_units,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        call("device/lockstep_move_sin", request)

    async def move_sin_async(
            self,
            amplitude: float,
            amplitude_units: LengthUnits,
            period: float,
            period_units: TimeUnits,
            count: float = 0,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the first axis of the lockstep group in a sinusoidal trajectory.
        The other axes in the lockstep group maintain their offsets throughout movement.

        Args:
            amplitude: Amplitude of the sinusoidal motion (half of the motion's peak-to-peak range).
            amplitude_units: Units of position.
            period: Period of the sinusoidal motion in milliseconds.
            period_units: Units of time.
            count: Number of sinusoidal cycles to complete.
                Must be a multiple of 0.5
                If count is not specified or set to 0, the axis will move indefinitely.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.LockstepMoveSinRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            amplitude=amplitude,
            amplitude_units=amplitude_units,
            period=period,
            period_units=period_units,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/lockstep_move_sin", request)

    def move_sin_stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the lockstep group at the end of the sinusoidal trajectory for the first axis.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.LockstepStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        call("device/lockstep_move_sin_stop", request)

    async def move_sin_stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the lockstep group at the end of the sinusoidal trajectory for the first axis.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.LockstepStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/lockstep_move_sin_stop", request)

    def move_max(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axes to the maximum valid position.
        The axes in the lockstep group maintain their offsets throughout movement.
        Respects lim.max for all axes in the group.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.MAX,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/lockstep_move", request)

    async def move_max_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axes to the maximum valid position.
        The axes in the lockstep group maintain their offsets throughout movement.
        Respects lim.max for all axes in the group.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.MAX,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/lockstep_move", request)

    def move_min(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axes to the minimum valid position.
        The axes in the lockstep group maintain their offsets throughout movement.
        Respects lim.min for all axes in the group.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.MIN,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/lockstep_move", request)

    async def move_min_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axes to the minimum valid position.
        The axes in the lockstep group maintain their offsets throughout movement.
        Respects lim.min for all axes in the group.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            velocity: Movement velocity.
                Default value of 0 indicates that the maxspeed setting is used instead.
                Requires at least Firmware 7.25.
            velocity_unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.LockstepMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            type=dto.AxisMoveType.MIN,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/lockstep_move", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the lockstep group stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.LockstepWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        call("device/lockstep_wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the lockstep group stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.LockstepWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("device/lockstep_wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the lockstep group is executing a motion command.

        Returns:
            True if the axes are currently executing a motion command.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = call(
            "device/lockstep_is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the lockstep group is executing a motion command.

        Returns:
            True if the axes are currently executing a motion command.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = await call_async(
            "device/lockstep_is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_axis_numbers(
            self
    ) -> List[int]:
        """
        Gets the axis numbers of the lockstep group.

        Returns:
            Axis numbers in order specified when enabling lockstep.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = call(
            "device/lockstep_get_axis_numbers",
            request,
            dto.LockstepGetAxisNumbersResponse.from_binary)
        return response.axes

    async def get_axis_numbers_async(
            self
    ) -> List[int]:
        """
        Gets the axis numbers of the lockstep group.

        Returns:
            Axis numbers in order specified when enabling lockstep.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = await call_async(
            "device/lockstep_get_axis_numbers",
            request,
            dto.LockstepGetAxisNumbersResponse.from_binary)
        return response.axes

    def get_offsets(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> List[float]:
        """
        Gets the initial offsets of secondary axes of an enabled lockstep group.

        Args:
            unit: Units of position.
                Uses primary axis unit conversion.

        Returns:
            Initial offset for each axis of the lockstep group.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = call(
            "device/lockstep_get_offsets",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    async def get_offsets_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> List[float]:
        """
        Gets the initial offsets of secondary axes of an enabled lockstep group.

        Args:
            unit: Units of position.
                Uses primary axis unit conversion.

        Returns:
            Initial offset for each axis of the lockstep group.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = await call_async(
            "device/lockstep_get_offsets",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    def get_twists(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> List[float]:
        """
        Gets the twists of secondary axes of an enabled lockstep group.

        Args:
            unit: Units of position.
                Uses primary axis unit conversion.

        Returns:
            Difference between the initial offset and the actual offset for each axis of the lockstep group.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = call(
            "device/lockstep_get_twists",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    async def get_twists_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> List[float]:
        """
        Gets the twists of secondary axes of an enabled lockstep group.

        Args:
            unit: Units of position.
                Uses primary axis unit conversion.

        Returns:
            Difference between the initial offset and the actual offset for each axis of the lockstep group.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = await call_async(
            "device/lockstep_get_twists",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    def get_position(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current position of the primary axis.

        Args:
            unit: Units of the position.

        Returns:
            Primary axis position.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = call(
            "device/lockstep_get_pos",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_position_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current position of the primary axis.

        Args:
            unit: Units of the position.

        Returns:
            Primary axis position.
        """
        request = dto.LockstepGetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            unit=unit,
        )
        response = await call_async(
            "device/lockstep_get_pos",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_tolerance(
            self,
            tolerance: float,
            unit: LengthUnits = Units.NATIVE,
            axis_index: int = 0
    ) -> None:
        """
        Sets lockstep twist tolerance.
        Twist tolerances that do not match the system configuration can reduce performance or damage the system.

        Args:
            tolerance: Twist tolerance.
            unit: Units of the tolerance.
                Uses primary axis unit conversion when setting to all axes,
                otherwise uses specified secondary axis unit conversion.
            axis_index: Optional index of a secondary axis to set the tolerance for.
                If left empty or set to 0, the tolerance is set to all the secondary axes.
        """
        request = dto.LockstepSetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            value=tolerance,
            unit=unit,
            axis_index=axis_index,
        )
        call("device/lockstep_set_tolerance", request)

    async def set_tolerance_async(
            self,
            tolerance: float,
            unit: LengthUnits = Units.NATIVE,
            axis_index: int = 0
    ) -> None:
        """
        Sets lockstep twist tolerance.
        Twist tolerances that do not match the system configuration can reduce performance or damage the system.

        Args:
            tolerance: Twist tolerance.
            unit: Units of the tolerance.
                Uses primary axis unit conversion when setting to all axes,
                otherwise uses specified secondary axis unit conversion.
            axis_index: Optional index of a secondary axis to set the tolerance for.
                If left empty or set to 0, the tolerance is set to all the secondary axes.
        """
        request = dto.LockstepSetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
            value=tolerance,
            unit=unit,
            axis_index=axis_index,
        )
        await call_async("device/lockstep_set_tolerance", request)

    def is_enabled(
            self
    ) -> bool:
        """
        Checks if the lockstep group is currently enabled on the device.

        Returns:
            True if a lockstep group with this ID is enabled on the device.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = call(
            "device/lockstep_is_enabled",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_enabled_async(
            self
    ) -> bool:
        """
        Checks if the lockstep group is currently enabled on the device.

        Returns:
            True if a lockstep group with this ID is enabled on the device.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = await call_async(
            "device/lockstep_is_enabled",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string which represents the enabled lockstep group.

        Returns:
            String which represents the enabled lockstep group.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = call_sync(
            "device/lockstep_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def park(
            self
    ) -> None:
        """
        Parks lockstep group in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        call("device/lockstep_park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks lockstep group in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        await call_async("device/lockstep_park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks lockstep group. Lockstep group will now be able to move.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        call("device/lockstep_unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks lockstep group. Lockstep group will now be able to move.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        await call_async("device/lockstep_unpark", request)

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if lockstep group is parked.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = call(
            "device/lockstep_is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if lockstep group is parked.
        """
        request = dto.LockstepEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            lockstep_group_id=self.lockstep_group_id,
        )
        response = await call_async(
            "device/lockstep_is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value
