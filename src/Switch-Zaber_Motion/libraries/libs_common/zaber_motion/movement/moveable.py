# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Optional
from .. import ascii
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.accel_type import AccelType
from ..dto.cyclic_direction import CyclicDirection
from ..dto.measurement_or_value import MeasurementOrValue
from ..dto.movement.default_motion_units import DefaultMotionUnits
from ..units import LengthUnits, VelocityUnits, AccelerationUnits

if TYPE_CHECKING:
    from ..ascii.axis import Axis
    from ..ascii.device import Device
    from ..ascii.lockstep import Lockstep


class Moveable:
    """
    Represents something that moves: either an axis of a device, or a lockstep group.
    """

    @property
    def moveable_id(self) -> int:
        """
        The identifier for the moveable instance.
        """
        return self._moveable_id

    @property
    def device(self) -> 'Device':
        """
        The device this moveable is on.
        """
        return self._device

    def __init__(self, moveable_id: int, device: 'Device'):
        self._moveable_id: int = moveable_id
        self._device: 'Device' = device

    @staticmethod
    def from_axis(
            axis: 'Axis',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a given axis.

        Args:
            axis: Axis to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified axis.
        """
        request = dto.MoveableSetupRequest(
            interface_id=axis.device.connection.interface_id,
            moveable_number=axis.axis_number,
            moveable_type=dto.MoveableType.AXIS,
            device=axis.device.device_address,
            default_units=units,
        )
        response = call(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, axis.device)

    @staticmethod
    async def from_axis_async(
            axis: 'Axis',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a given axis.

        Args:
            axis: Axis to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified axis.
        """
        request = dto.MoveableSetupRequest(
            interface_id=axis.device.connection.interface_id,
            moveable_number=axis.axis_number,
            moveable_type=dto.MoveableType.AXIS,
            device=axis.device.device_address,
            default_units=units,
        )
        response = await call_async(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, axis.device)

    @staticmethod
    def from_lockstep(
            lockstep: 'Lockstep',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a given lockstep group.

        Args:
            lockstep: Lockstep group to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified lockstep group.
        """
        request = dto.MoveableSetupRequest(
            interface_id=lockstep.device.connection.interface_id,
            moveable_number=lockstep.lockstep_group_id,
            moveable_type=dto.MoveableType.LOCKSTEP,
            device=lockstep.device.device_address,
            default_units=units,
        )
        response = call(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, lockstep.device)

    @staticmethod
    async def from_lockstep_async(
            lockstep: 'Lockstep',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a given lockstep group.

        Args:
            lockstep: Lockstep group to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified lockstep group.
        """
        request = dto.MoveableSetupRequest(
            interface_id=lockstep.device.connection.interface_id,
            moveable_number=lockstep.lockstep_group_id,
            moveable_type=dto.MoveableType.LOCKSTEP,
            device=lockstep.device.device_address,
            default_units=units,
        )
        response = await call_async(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, lockstep.device)

    @staticmethod
    def from_device(
            device: 'Device',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a single-axis device.

        Args:
            device: Device to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified device.
        """
        request = dto.MoveableSetupRequest(
            interface_id=device.connection.interface_id,
            moveable_number=1,
            moveable_type=dto.MoveableType.DEVICE,
            device=device.device_address,
            default_units=units,
        )
        response = call(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, device)

    @staticmethod
    async def from_device_async(
            device: 'Device',
            units: Optional[DefaultMotionUnits] = None
    ) -> 'Moveable':
        """
        Creates a Moveable instance for a single-axis device.

        Args:
            device: Device to create a Moveable for.
            units: Default units of measurement used for movement operations.

        Returns:
            A Moveable instance for the specified device.
        """
        request = dto.MoveableSetupRequest(
            interface_id=device.connection.interface_id,
            moveable_number=1,
            moveable_type=dto.MoveableType.DEVICE,
            device=device.device_address,
            default_units=units,
        )
        response = await call_async(
            "moveable/setup",
            request,
            dto.IntResponse.from_binary)
        return Moveable(response.value, device)

    def move_absolute(
            self,
            position: MeasurementOrValue,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True,
            cyclic_direction: Optional[CyclicDirection] = None,
            extra_cycles: Optional[int] = None
    ) -> None:
        """
        Moves to an absolute position.

        Args:
            position: Absolute position to move to.
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            cyclic_direction: Which direction a cyclic device should take to get to the target position.
            extra_cycles: Number of extra cycles to complete before stopping at the target.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            position=position,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
            cyclic_direction=cyclic_direction,
            extra_cycles=extra_cycles,
        )
        call("moveable/move_abs", request)

    async def move_absolute_async(
            self,
            position: MeasurementOrValue,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True,
            cyclic_direction: Optional[CyclicDirection] = None,
            extra_cycles: Optional[int] = None
    ) -> None:
        """
        Moves to an absolute position.

        Args:
            position: Absolute position to move to.
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
            cyclic_direction: Which direction a cyclic device should take to get to the target position.
            extra_cycles: Number of extra cycles to complete before stopping at the target.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            position=position,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
            cyclic_direction=cyclic_direction,
            extra_cycles=extra_cycles,
        )
        await call_async("moveable/move_abs", request)

    def move_relative(
            self,
            position: MeasurementOrValue,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves by a relative amount from the current position.

        Args:
            position: Relative displacement to move by.
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            position=position,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_rel", request)

    async def move_relative_async(
            self,
            position: MeasurementOrValue,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves by a relative amount from the current position.

        Args:
            position: Relative displacement to move by.
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            position=position,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_rel", request)

    def move_velocity(
            self,
            velocity: MeasurementOrValue,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Begins moving at a specified velocity.

        Args:
            velocity: Velocity to move at.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_vel", request)

    async def move_velocity_async(
            self,
            velocity: MeasurementOrValue,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Begins moving at a specified velocity.

        Args:
            velocity: Velocity to move at.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_vel", request)

    def move_max(
            self,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves to the end of travel.

        Args:
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_max", request)

    async def move_max_async(
            self,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves to the end of travel.

        Args:
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_max", request)

    def move_min(
            self,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves to the beginning of travel.

        Args:
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_min", request)

    async def move_min_async(
            self,
            velocity: Optional[MeasurementOrValue] = None,
            acceleration: Optional[MeasurementOrValue] = None,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves to the beginning of travel.

        Args:
            velocity: Movement velocity. If not specified, the maximum velocity setting is used.
            acceleration: Movement acceleration. If not specified, the default acceleration setting is used.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            velocity=velocity,
            acceleration=acceleration,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_min", request)

    def get_position(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the current position of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Current position.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_position_async(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the current position of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Current position.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_encoder_position(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the current encoder position of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Current encoder position.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_encoder_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_encoder_position_async(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the current encoder position of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Current encoder position.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_encoder_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the moveable to the home position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the moveable to the home position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/home", request)

    def is_homed(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable has position reference and was homed.

        Returns:
            True if the moveable has position reference and was homed.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = call(
            "moveable/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_homed_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable has position reference and was homed.

        Returns:
            True if the moveable has position reference and was homed.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = await call_async(
            "moveable/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable is executing a motion command.

        Returns:
            True if the moveable is currently executing a motion command.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = call(
            "moveable/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable is executing a motion command.

        Returns:
            True if the moveable is currently executing a motion command.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = await call_async(
            "moveable/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable is parked.

        Returns:
            True if the moveable is parked.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = call(
            "moveable/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the moveable is parked.

        Returns:
            True if the moveable is parked.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = await call_async(
            "moveable/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing movement of the moveable.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing movement of the moveable.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/stop", request)

    def move_sin(
            self,
            amplitude: MeasurementOrValue,
            period: MeasurementOrValue,
            count: float = 0,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the moveable in a sinusoidal trajectory.

        Args:
            amplitude: Amplitude of the sinusoidal motion (half of the motion's peak-to-peak range).
            period: Period of the sinusoidal motion.
            count: Number of sinusoidal cycles to complete.
                Must be a multiple of 0.5.
                If count is not specified or set to 0, the moveable will move indefinitely.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveSinRequest(
            moveable_id=self.moveable_id,
            amplitude=amplitude,
            period=period,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_sin", request)

    async def move_sin_async(
            self,
            amplitude: MeasurementOrValue,
            period: MeasurementOrValue,
            count: float = 0,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the moveable in a sinusoidal trajectory.

        Args:
            amplitude: Amplitude of the sinusoidal motion (half of the motion's peak-to-peak range).
            period: Period of the sinusoidal motion.
            count: Number of sinusoidal cycles to complete.
                Must be a multiple of 0.5.
                If count is not specified or set to 0, the moveable will move indefinitely.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.MoveableMoveSinRequest(
            moveable_id=self.moveable_id,
            amplitude=amplitude,
            period=period,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_sin", request)

    def move_sin_stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the moveable at the end of the sinusoidal trajectory.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        call("moveable/move_sin_stop", request)

    async def move_sin_stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the moveable at the end of the sinusoidal trajectory.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.MoveableMoveRequest(
            moveable_id=self.moveable_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("moveable/move_sin_stop", request)

    def park(
            self
    ) -> None:
        """
        Parks the moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        call("moveable/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        await call_async("moveable/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks the moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        call("moveable/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks the moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        await call_async("moveable/unpark", request)

    def get_velocity(
            self,
            unit: Optional[VelocityUnits] = None
    ) -> float:
        """
        Returns the current velocity of the moveable.

        Args:
            unit: Units of velocity. If not specified, the default velocity unit is used.

        Returns:
            Current velocity.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_velocity",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_velocity_async(
            self,
            unit: Optional[VelocityUnits] = None
    ) -> float:
        """
        Returns the current velocity of the moveable.

        Args:
            unit: Units of velocity. If not specified, the default velocity unit is used.

        Returns:
            Current velocity.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_velocity",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_max_speed(
            self,
            unit: Optional[VelocityUnits] = None
    ) -> float:
        """
        Returns the maximum speed that this moveable will execute moves at by default.
        If a different velocity is specified on a move command, that will override
        this value for that command only.

        Args:
            unit: Units of velocity. If not specified, the default velocity unit is used.

        Returns:
            Maximum speed.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_max_speed",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_max_speed_async(
            self,
            unit: Optional[VelocityUnits] = None
    ) -> float:
        """
        Returns the maximum speed that this moveable will execute moves at by default.
        If a different velocity is specified on a move command, that will override
        this value for that command only.

        Args:
            unit: Units of velocity. If not specified, the default velocity unit is used.

        Returns:
            Maximum speed.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_max_speed",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_max_speed(
            self,
            speed: MeasurementOrValue
    ) -> None:
        """
        Sets the maximum speed of the moveable. For a lockstep group, sets the value on all axes.

        Args:
            speed: Maximum speed to set.
        """
        request = dto.MoveableSetSettingRequest(
            moveable_id=self.moveable_id,
            value=speed,
        )
        call("moveable/set_max_speed", request)

    async def set_max_speed_async(
            self,
            speed: MeasurementOrValue
    ) -> None:
        """
        Sets the maximum speed of the moveable. For a lockstep group, sets the value on all axes.

        Args:
            speed: Maximum speed to set.
        """
        request = dto.MoveableSetSettingRequest(
            moveable_id=self.moveable_id,
            value=speed,
        )
        await call_async("moveable/set_max_speed", request)

    def get_max_acceleration(
            self,
            accel_type: Optional[AccelType] = None,
            unit: Optional[AccelerationUnits] = None
    ) -> float:
        """
        Returns the maximum acceleration of the moveable. For a lockstep group, returns the lowest value across all axes.

        Args:
            accel_type: Which acceleration ramp to return. Defaults to AccelDecel.
            unit: Units of acceleration. If not specified, the default acceleration unit is used.

        Returns:
            Maximum acceleration.
        """
        request = dto.MoveableGetAccelerationRequest(
            moveable_id=self.moveable_id,
            accel_type=accel_type,
            unit=unit,
        )
        response = call(
            "moveable/get_max_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_max_acceleration_async(
            self,
            accel_type: Optional[AccelType] = None,
            unit: Optional[AccelerationUnits] = None
    ) -> float:
        """
        Returns the maximum acceleration of the moveable. For a lockstep group, returns the lowest value across all axes.

        Args:
            accel_type: Which acceleration ramp to return. Defaults to AccelDecel.
            unit: Units of acceleration. If not specified, the default acceleration unit is used.

        Returns:
            Maximum acceleration.
        """
        request = dto.MoveableGetAccelerationRequest(
            moveable_id=self.moveable_id,
            accel_type=accel_type,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_max_acceleration",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_max_acceleration(
            self,
            accel: MeasurementOrValue,
            accel_type: Optional[AccelType] = None
    ) -> None:
        """
        Sets the maximum acceleration of the moveable. For a lockstep group, sets the value on all axes.

        Args:
            accel: Maximum acceleration to set.
            accel_type: Which acceleration ramp to set. Defaults to AccelDecel.
        """
        request = dto.MoveableSetAccelerationRequest(
            moveable_id=self.moveable_id,
            accel=accel,
            accel_type=accel_type,
        )
        call("moveable/set_max_acceleration", request)

    async def set_max_acceleration_async(
            self,
            accel: MeasurementOrValue,
            accel_type: Optional[AccelType] = None
    ) -> None:
        """
        Sets the maximum acceleration of the moveable. For a lockstep group, sets the value on all axes.

        Args:
            accel: Maximum acceleration to set.
            accel_type: Which acceleration ramp to set. Defaults to AccelDecel.
        """
        request = dto.MoveableSetAccelerationRequest(
            moveable_id=self.moveable_id,
            accel=accel,
            accel_type=accel_type,
        )
        await call_async("moveable/set_max_acceleration", request)

    def get_limit_min(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the minimum limit of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Minimum limit.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_limit_min",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_limit_min_async(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the minimum limit of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Minimum limit.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_limit_min",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_limit_max(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the maximum limit of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Maximum limit.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = call(
            "moveable/get_limit_max",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_limit_max_async(
            self,
            unit: Optional[LengthUnits] = None
    ) -> float:
        """
        Returns the maximum limit of the moveable.

        Args:
            unit: Units of position. If not specified, the default position unit is used.

        Returns:
            Maximum limit.
        """
        request = dto.MoveableGetSettingRequest(
            moveable_id=self.moveable_id,
            unit=unit,
        )
        response = await call_async(
            "moveable/get_limit_max",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_lockstep(
            self
    ) -> Optional['Lockstep']:
        """
        Returns the lockstep group this moveable represents, or null if it is not a lockstep moveable.

        Returns:
            Lockstep instance, or null if this is not a lockstep moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = call(
            "moveable/get_lockstep",
            request,
            dto.IntResponse.from_binary)
        return ascii.Lockstep(self.device, response.value) if response.value != 0 else None

    async def get_lockstep_async(
            self
    ) -> Optional['Lockstep']:
        """
        Returns the lockstep group this moveable represents, or null if it is not a lockstep moveable.

        Returns:
            Lockstep instance, or null if this is not a lockstep moveable.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = await call_async(
            "moveable/get_lockstep",
            request,
            dto.IntResponse.from_binary)
        return ascii.Lockstep(self.device, response.value) if response.value != 0 else None

    def get_axis(
            self
    ) -> 'Axis':
        """
        Returns the axis this moveable represents.
        For a lockstep moveable, returns the primary axis of the lockstep group.

        Returns:
            Axis this moveable is based on.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = call(
            "moveable/get_axis",
            request,
            dto.IntResponse.from_binary)
        return ascii.Axis(self.device, response.value)

    async def get_axis_async(
            self
    ) -> 'Axis':
        """
        Returns the axis this moveable represents.
        For a lockstep moveable, returns the primary axis of the lockstep group.

        Returns:
            Axis this moveable is based on.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        response = await call_async(
            "moveable/get_axis",
            request,
            dto.IntResponse.from_binary)
        return ascii.Axis(self.device, response.value)

    def driver_disable(
            self
    ) -> None:
        """
        Disables the driver, which prevents current from being sent to the motor or load.
        If the driver is already disabled, the driver remains disabled.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        call("moveable/driver_disable", request)

    async def driver_disable_async(
            self
    ) -> None:
        """
        Disables the driver, which prevents current from being sent to the motor or load.
        If the driver is already disabled, the driver remains disabled.
        """
        request = dto.MoveableIdRequest(
            moveable_id=self.moveable_id,
        )
        await call_async("moveable/driver_disable", request)

    def driver_enable(
            self,
            timeout: float = 10
    ) -> None:
        """
        Attempts to enable the driver repeatedly for the specified timeout.
        If the driver is already enabled, the driver remains enabled.

        Args:
            timeout: Timeout in seconds. Specify 0 to attempt to enable the driver once.
        """
        request = dto.MoveableDriverEnableRequest(
            moveable_id=self.moveable_id,
            timeout=timeout,
        )
        call("moveable/driver_enable", request)

    async def driver_enable_async(
            self,
            timeout: float = 10
    ) -> None:
        """
        Attempts to enable the driver repeatedly for the specified timeout.
        If the driver is already enabled, the driver remains enabled.

        Args:
            timeout: Timeout in seconds. Specify 0 to attempt to enable the driver once.
        """
        request = dto.MoveableDriverEnableRequest(
            moveable_id=self.moveable_id,
            timeout=timeout,
        )
        await call_async("moveable/driver_enable", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the moveable stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.MoveableWaitUntilIdleRequest(
            moveable_id=self.moveable_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        call("moveable/wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until the moveable stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.MoveableWaitUntilIdleRequest(
            moveable_id=self.moveable_id,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("moveable/wait_until_idle", request)

    @staticmethod
    def __free(
            moveable_id: int
    ) -> None:
        """
        Frees the moveable instance.

        Args:
            moveable_id: The ID of the moveable to free.
        """
        request = dto.MoveableIdRequest(
            moveable_id=moveable_id,
        )
        call_sync("moveable/free", request)

    def __del__(self) -> None:
        Moveable.__free(self._moveable_id)
