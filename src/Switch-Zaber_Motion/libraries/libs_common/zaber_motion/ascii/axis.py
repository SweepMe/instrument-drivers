# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.axis_identity import AxisIdentity
from ..dto.ascii.axis_type import AxisType
from ..dto.ascii.response import Response
from ..dto.ascii.set_state_axis_response import SetStateAxisResponse
from ..dto.cyclic_direction import CyclicDirection
from ..dto.firmware_version import FirmwareVersion
from ..dto.measurement import Measurement
from ..dto.unit_conversion_descriptor import UnitConversionDescriptor
from ..units import Units, LengthUnits, VelocityUnits, AccelerationUnits, TimeUnits
from .axis_settings import AxisSettings
from .axis_storage import AxisStorage
from .warnings import Warnings

if TYPE_CHECKING:
    from .device import Device


class Axis:
    """
    Represents an axis of motion associated with a device.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this axis.
        """
        return self._device

    @property
    def axis_number(self) -> int:
        """
        The axis number identifies the axis on the device.
        The first axis has the number one.
        """
        return self._axis_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this axis.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this axis.
        Requires at least Firmware 7.30.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this axis.
        """
        return self._warnings

    @property
    def identity(self) -> AxisIdentity:
        """
        Identity of the axis.
        """
        return self.__retrieve_identity()

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """
        return self.identity.peripheral_id

    @property
    def peripheral_name(self) -> str:
        """
        Name of the peripheral.
        """
        return self.identity.peripheral_name

    @property
    def peripheral_serial_number(self) -> int:
        """
        Serial number of the peripheral, or 0 when not applicable.
        """
        return self.identity.peripheral_serial_number

    @property
    def is_peripheral(self) -> bool:
        """
        Indicates whether the axis is a peripheral or part of an integrated device.
        """
        return self.identity.is_peripheral

    @property
    def axis_type(self) -> AxisType:
        """
        Determines the type of an axis and units it accepts.
        """
        return self.identity.axis_type

    @property
    def resolution(self) -> int:
        """
        The number of microsteps per full step for motion axes. Always equal to 0 for non-motion axes.
        """
        return self.identity.resolution

    @property
    def label(self) -> str:
        """
        User-assigned label of the peripheral.
        """
        return self.__retrieve_label()

    def __init__(self, device: 'Device', axis_number: int):
        self._device: 'Device' = device
        self._axis_number: int = axis_number
        self._settings: AxisSettings = AxisSettings(self)
        self._storage: AxisStorage = AxisStorage(self)
        self._warnings: Warnings = Warnings(device, axis_number)

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.DeviceHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        call("device/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.DeviceHomeRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/home", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        call("device/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/stop", request)

    def park(
            self
    ) -> None:
        """
        Parks the axis in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        call("device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the axis in anticipation of turning the power off.
        It can later be powered on, unparked, and moved without first having to home it.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        await call_async("device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        call("device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        await call_async("device/unpark", request)

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.DeviceWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            throw_error_on_fault=throw_error_on_fault,
        )
        call("device/wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = dto.DeviceWaitUntilIdleRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            throw_error_on_fault=throw_error_on_fault,
        )
        await call_async("device/wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def is_homed(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis has position reference and was homed.

        Returns:
            True if the axis has position reference and was homed.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_homed_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis has position reference and was homed.

        Returns:
            True if the axis has position reference and was homed.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def move_absolute(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE,
            cyclic_direction: Optional[CyclicDirection] = None,
            extra_cycles: Optional[int] = None
    ) -> None:
        """
        Move axis to absolute position.

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
            cyclic_direction: Which direction a cyclic device should take to get to the target position.
            extra_cycles: Number of extra cycles to complete before stopping at the target.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
            cyclic_direction=cyclic_direction,
            extra_cycles=extra_cycles,
        )
        call("device/move", request)

    async def move_absolute_async(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE,
            cyclic_direction: Optional[CyclicDirection] = None,
            extra_cycles: Optional[int] = None
    ) -> None:
        """
        Move axis to absolute position.

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
            cyclic_direction: Which direction a cyclic device should take to get to the target position.
            extra_cycles: Number of extra cycles to complete before stopping at the target.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
            cyclic_direction=cyclic_direction,
            extra_cycles=extra_cycles,
        )
        await call_async("device/move", request)

    def move_max(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the maximum position as specified by limit.max.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.MAX,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/move", request)

    async def move_max_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the maximum position as specified by limit.max.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.MAX,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/move", request)

    def move_min(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the minimum position as specified by limit.min.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.MIN,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/move", request)

    async def move_min_async(
            self,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to the minimum position as specified by limit.min.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.MIN,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/move", request)

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
        Move axis to position relative to current position.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/move", request)

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
        Move axis to position relative to current position.

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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/move", request)

    def move_velocity(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/move", request)

    async def move_velocity_async(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
            acceleration: Movement acceleration.
                Default value of 0 indicates that the accel setting is used instead.
                Requires at least Firmware 7.25.
            acceleration_unit: Units of acceleration.
        """
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/move", request)

    def get_position(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            setting="pos",
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_position_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            setting="pos",
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_number_of_index_positions(
            self
    ) -> int:
        """
        Gets number of index positions of the axis.

        Returns:
            Number of index positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_number_of_index_positions_async(
            self
    ) -> int:
        """
        Gets number of index positions of the axis.

        Returns:
            Number of index positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_index_position(
            self
    ) -> int:
        """
        Returns current axis index position.

        Returns:
            Index position starting from 1 or 0 if the position is not an index position.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_index_position_async(
            self
    ) -> int:
        """
        Returns current axis index position.

        Returns:
            Index position starting from 1 or 0 if the position is not an index position.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def move_index(
            self,
            index: int,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to index position.

        Args:
            index: Index position. Index positions are numbered from 1.
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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.INDEX,
            arg_int=index,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        call("device/move", request)

    async def move_index_async(
            self,
            index: int,
            wait_until_idle: bool = True,
            velocity: float = 0,
            velocity_unit: VelocityUnits = Units.NATIVE,
            acceleration: float = 0,
            acceleration_unit: AccelerationUnits = Units.NATIVE
    ) -> None:
        """
        Moves the axis to index position.

        Args:
            index: Index position. Index positions are numbered from 1.
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
        request = dto.DeviceMoveRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            type=dto.AxisMoveType.INDEX,
            arg_int=index,
            wait_until_idle=wait_until_idle,
            velocity=velocity,
            velocity_unit=velocity_unit,
            acceleration=acceleration,
            acceleration_unit=acceleration_unit,
        )
        await call_async("device/move", request)

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = call(
            "interface/generic_command",
            request,
            Response.from_binary)
        return response

    async def generic_command_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = await call_async(
            "interface/generic_command",
            request,
            Response.from_binary)
        return response

    def generic_command_multi_response(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = call(
            "interface/generic_command_multi_response",
            request,
            dto.GenericCommandResponseCollection.from_binary)
        return response.responses

    async def generic_command_multi_response_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = await call_async(
            "interface/generic_command_multi_response",
            request,
            dto.GenericCommandResponseCollection.from_binary)
        return response.responses

    def generic_command_no_response(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
        )
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
        )
        await call_async("interface/generic_command_no_response", request)

    def prepare_command(
            self,
            command_template: str,
            *parameters: Measurement
    ) -> str:
        """
        Formats parameters into a command and performs unit conversions.
        Parameters in the command template are denoted by a question mark.
        Command returned is only valid for this axis and this device.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of a command to prepare. Parameters are denoted by question marks.
            parameters: Variable number of command parameters.

        Returns:
            Command with converted parameters.
        """
        request = dto.PrepareCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command_template=command_template,
            parameters=list(parameters),
        )
        response = call_sync(
            "device/prepare_command",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def has_command(
            self,
            command: str,
            allow_partial: bool = False
    ) -> bool:
        """
        Checks whether the axis supports the given command.

        Args:
            command: Command to check.
                Parameters can be denoted by question marks, valid values, or the parameter name.
            allow_partial: If true, also matches commands that are a prefix of a supported command.

        Returns:
            True if the command is supported.
        """
        request = dto.DeviceHasCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command=command,
            allow_partial=allow_partial,
        )
        response = call_sync(
            "device/has_command",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_command_unit_conversion_descriptors(
            self,
            command_template: str
    ) -> List[Optional[UnitConversionDescriptor]]:
        """
        Retrieves unit conversion descriptors for a command, allowing unit conversion without a device.
        The descriptors can be used with the ConvertTo/FromNativeUnits methods of the UnitTable class.
        Parameters in the command template are denoted by a question mark.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of the command. Parameters are denoted by question marks.

        Returns:
            Unit conversion descriptor for each parameter in the command. Nil if a parameter does not have conversion.
        """
        request = dto.PrepareCommandRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            command_template=command_template,
        )
        response = call_sync(
            "device/get_command_unit_conversion",
            request,
            dto.GetCommandUnitConversionResponse.from_binary)
        return response.value

    def set_label(
            self,
            label: str
    ) -> None:
        """
        Sets the user-assigned peripheral label.
        The label is stored on the controller and recognized by other software.

        Args:
            label: Label to set.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            value=label,
        )
        call("device/set_label", request)

    async def set_label_async(
            self,
            label: str
    ) -> None:
        """
        Sets the user-assigned peripheral label.
        The label is stored on the controller and recognized by other software.

        Args:
            label: Label to set.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            value=label,
        )
        await call_async("device/set_label", request)

    def __retrieve_label(
            self
    ) -> str:
        """
        Gets the peripheral name.

        Returns:
            The label.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call_sync(
            "device/get_label",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axis.

        Returns:
            A string that represents the axis.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call_sync(
            "device/axis_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current axis state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the axis.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call(
            "device/get_state",
            request,
            dto.StringResponse.from_binary)
        return response.value

    async def get_state_async(
            self
    ) -> str:
        """
        Returns a serialization of the current axis state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the axis.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = await call_async(
            "device/get_state",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def set_state(
            self,
            state: str
    ) -> SetStateAxisResponse:
        """
        Applies a saved state to this axis.

        Args:
            state: The state object to apply to this axis.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            state=state,
        )
        response = call(
            "device/set_axis_state",
            request,
            SetStateAxisResponse.from_binary)
        return response

    async def set_state_async(
            self,
            state: str
    ) -> SetStateAxisResponse:
        """
        Applies a saved state to this axis.

        Args:
            state: The state object to apply to this axis.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            state=state,
        )
        response = await call_async(
            "device/set_axis_state",
            request,
            SetStateAxisResponse.from_binary)
        return response

    def can_set_state(
            self,
            state: str,
            firmware_version: Optional[FirmwareVersion] = None
    ) -> Optional[str]:
        """
        Checks if a state can be applied to this axis.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this axis.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            state=state,
            firmware_version=firmware_version,
        )
        response = call(
            "device/can_set_axis_state",
            request,
            dto.CanSetStateAxisResponse.from_binary)
        return response.error

    async def can_set_state_async(
            self,
            state: str,
            firmware_version: Optional[FirmwareVersion] = None
    ) -> Optional[str]:
        """
        Checks if a state can be applied to this axis.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this axis.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            state=state,
            firmware_version=firmware_version,
        )
        response = await call_async(
            "device/can_set_axis_state",
            request,
            dto.CanSetStateAxisResponse.from_binary)
        return response.error

    def __retrieve_identity(
            self
    ) -> AxisIdentity:
        """
        Returns identity.

        Returns:
            Axis identity.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        response = call_sync(
            "device/get_axis_identity",
            request,
            AxisIdentity.from_binary)
        return response

    def driver_disable(
            self
    ) -> None:
        """
        Disables the driver, which prevents current from being sent to the motor or load.
        If the driver is already disabled, the driver remains disabled.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        call("device/driver_disable", request)

    async def driver_disable_async(
            self
    ) -> None:
        """
        Disables the driver, which prevents current from being sent to the motor or load.
        If the driver is already disabled, the driver remains disabled.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        await call_async("device/driver_disable", request)

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
        request = dto.DriverEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            timeout=timeout,
        )
        call("device/driver_enable", request)

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
        request = dto.DriverEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            timeout=timeout,
        )
        await call_async("device/driver_enable", request)

    def activate(
            self
    ) -> None:
        """
        Activates a peripheral on this axis.
        Removes all identity information for the device.
        Run the identify method on the device after activating to refresh the information.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        call("device/activate", request)

    async def activate_async(
            self
    ) -> None:
        """
        Activates a peripheral on this axis.
        Removes all identity information for the device.
        Run the identify method on the device after activating to refresh the information.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        await call_async("device/activate", request)

    def restore(
            self
    ) -> None:
        """
        Restores all axis settings to their default values.
        Deletes all zaber axis storage keys.
        Disables lockstep if the axis is part of one. Unparks the axis.
        Preserves storage.
        The device needs to be identified again after the restore.
        """
        request = dto.DeviceRestoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        call("device/restore", request)

    async def restore_async(
            self
    ) -> None:
        """
        Restores all axis settings to their default values.
        Deletes all zaber axis storage keys.
        Disables lockstep if the axis is part of one. Unparks the axis.
        Preserves storage.
        The device needs to be identified again after the restore.
        """
        request = dto.DeviceRestoreRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
        )
        await call_async("device/restore", request)

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
        Moves the axis in a sinusoidal trajectory.

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
        request = dto.DeviceMoveSinRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            amplitude=amplitude,
            amplitude_units=amplitude_units,
            period=period,
            period_units=period_units,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        call("device/move_sin", request)

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
        Moves the axis in a sinusoidal trajectory.

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
        request = dto.DeviceMoveSinRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            amplitude=amplitude,
            amplitude_units=amplitude_units,
            period=period,
            period_units=period_units,
            count=count,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/move_sin", request)

    def move_sin_stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the axis at the end of the sinusoidal trajectory.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        call("device/move_sin_stop", request)

    async def move_sin_stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the axis at the end of the sinusoidal trajectory.
        If the sinusoidal motion was started with an integer-plus-half cycle count,
        the motion ends at the half-way point of the sinusoidal trajectory.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished.
        """
        request = dto.DeviceStopRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            axis=self.axis_number,
            wait_until_idle=wait_until_idle,
        )
        await call_async("device/move_sin_stop", request)
