# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Optional
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.binary.binary_settings import BinarySettings
from ..dto.binary.command_code import CommandCode
from ..dto.binary.device_identity import DeviceIdentity
from ..dto.binary.device_type import DeviceType
from ..dto.binary.message import Message
from ..dto.firmware_version import FirmwareVersion
from ..units import UnitsAndLiterals, Units, LengthUnits, VelocityUnits
from .device_settings import DeviceSettings

if TYPE_CHECKING:
    from .connection import Connection


class Device:
    """
    Represents a device using the binary protocol.
    """

    DEFAULT_MOVEMENT_TIMEOUT = 60
    """
    Default timeout for move commands in seconds.
    """

    @property
    def connection(self) -> 'Connection':
        """
        Connection of this device.
        """
        return self._connection

    @property
    def settings(self) -> DeviceSettings:
        """
        Settings and properties of this axis.
        """
        return self._settings

    @property
    def device_address(self) -> int:
        """
        The device address uniquely identifies the device on the connection.
        It can be configured or automatically assigned by the renumber command.
        """
        return self._device_address

    @property
    def identity(self) -> DeviceIdentity:
        """
        Identity of the device.
        """
        return self.__retrieve_identity()

    @property
    def is_identified(self) -> bool:
        """
        Indicates whether or not the device has been identified.
        """
        return self.__retrieve_is_identified()

    @property
    def device_id(self) -> int:
        """
        Unique ID of the device hardware.
        """
        return self.identity.device_id

    @property
    def serial_number(self) -> int:
        """
        Serial number of the device.
        Requires at least Firmware 6.15 for devices or 6.24 for peripherals.
        """
        return self.identity.serial_number

    @property
    def name(self) -> str:
        """
        Name of the product.
        """
        return self.identity.name

    @property
    def firmware_version(self) -> FirmwareVersion:
        """
        Version of the firmware.
        """
        return self.identity.firmware_version

    @property
    def is_peripheral(self) -> bool:
        """
        Indicates whether the device is a peripheral or part of an integrated device.
        """
        return self.identity.is_peripheral

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """
        return self.identity.peripheral_id

    @property
    def peripheral_name(self) -> str:
        """
        Name of the peripheral hardware.
        """
        return self.identity.peripheral_name

    @property
    def device_type(self) -> DeviceType:
        """
        Determines the type of an device and units it accepts.
        """
        return self.identity.device_type

    def __init__(self, connection: 'Connection', device_address: int):
        self._connection: 'Connection' = connection
        self._settings: DeviceSettings = DeviceSettings(self)
        self._device_address: int = device_address

    def generic_command(
            self,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> Message:
        """
        Sends a generic Binary command to this device.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
            timeout=timeout,
            check_errors=check_errors,
        )
        response = call(
            "binary/interface/generic_command",
            request,
            Message.from_binary)
        return response

    async def generic_command_async(
            self,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> Message:
        """
        Sends a generic Binary command to this device.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
            timeout=timeout,
            check_errors=check_errors,
        )
        response = await call_async(
            "binary/interface/generic_command",
            request,
            Message.from_binary)
        return response

    def generic_command_no_response(
            self,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this device without expecting a response.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
        )
        call("binary/interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this device without expecting a response.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
        )
        await call_async("binary/interface/generic_command_no_response", request)

    def generic_command_with_units(
            self,
            command: CommandCode,
            data: float = 0,
            from_unit: UnitsAndLiterals = Units.NATIVE,
            to_unit: UnitsAndLiterals = Units.NATIVE,
            timeout: float = 0.0
    ) -> float:
        """
        Sends a generic Binary command to this device with unit conversions for both sent data and retrieved data.

        Args:
            command: Command to send.
            data: Data argument to the command. Defaults to zero.
            from_unit: Unit to convert sent data from.
            to_unit: Unit to convert retrieved data to.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.

        Returns:
            Data that has been converted to the provided unit.
        """
        request = dto.BinaryGenericWithUnitsRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
            from_unit=from_unit,
            to_unit=to_unit,
            timeout=timeout,
        )
        response = call(
            "binary/device/generic_command_with_units",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def generic_command_with_units_async(
            self,
            command: CommandCode,
            data: float = 0,
            from_unit: UnitsAndLiterals = Units.NATIVE,
            to_unit: UnitsAndLiterals = Units.NATIVE,
            timeout: float = 0.0
    ) -> float:
        """
        Sends a generic Binary command to this device with unit conversions for both sent data and retrieved data.

        Args:
            command: Command to send.
            data: Data argument to the command. Defaults to zero.
            from_unit: Unit to convert sent data from.
            to_unit: Unit to convert retrieved data to.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.

        Returns:
            Data that has been converted to the provided unit.
        """
        request = dto.BinaryGenericWithUnitsRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            data=data,
            from_unit=from_unit,
            to_unit=to_unit,
            timeout=timeout,
        )
        response = await call_async(
            "binary/device/generic_command_with_units",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def home(
            self,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Homes device. Device returns to its homing position.

        Args:
            unit: Unit to convert returned position to.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceHomeRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            unit=unit,
            timeout=timeout,
        )
        response = call(
            "binary/device/home",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def home_async(
            self,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Homes device. Device returns to its homing position.

        Args:
            unit: Unit to convert returned position to.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceHomeRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            unit=unit,
            timeout=timeout,
        )
        response = await call_async(
            "binary/device/home",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def stop(
            self,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Stops ongoing device movement. Decelerates until zero speed.

        Args:
            unit: Unit to convert returned position to.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceStopRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            unit=unit,
            timeout=timeout,
        )
        response = call(
            "binary/device/stop",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def stop_async(
            self,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Stops ongoing device movement. Decelerates until zero speed.

        Args:
            unit: Unit to convert returned position to.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceStopRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            unit=unit,
            timeout=timeout,
        )
        response = await call_async(
            "binary/device/stop",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def move_absolute(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Move device to absolute position.

        Args:
            position: Absolute position.
            unit: Unit for the provided position as well as position returned by the device.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            timeout=timeout,
        )
        response = call(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def move_absolute_async(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Move device to absolute position.

        Args:
            position: Absolute position.
            unit: Unit for the provided position as well as position returned by the device.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.ABS,
            arg=position,
            unit=unit,
            timeout=timeout,
        )
        response = await call_async(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def move_relative(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Move device to position relative to current position.

        Args:
            position: Relative position.
            unit: Unit for the provided position as well as position returned by the device.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            timeout=timeout,
        )
        response = call(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def move_relative_async(
            self,
            position: float,
            unit: LengthUnits = Units.NATIVE,
            timeout: float = DEFAULT_MOVEMENT_TIMEOUT
    ) -> float:
        """
        Move device to position relative to current position.

        Args:
            position: Relative position.
            unit: Unit for the provided position as well as position returned by the device.
            timeout: Number of seconds to wait for response from the device chain (defaults to 60s).

        Returns:
            Current position that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.REL,
            arg=position,
            unit=unit,
            timeout=timeout,
        )
        response = await call_async(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def move_velocity(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE
    ) -> float:
        """
        Begins to move device at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Unit to convert returned velocity to.

        Returns:
            Device velocity that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
        )
        response = call(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def move_velocity_async(
            self,
            velocity: float,
            unit: VelocityUnits = Units.NATIVE
    ) -> float:
        """
        Begins to move device at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Unit to convert returned velocity to.

        Returns:
            Device velocity that has been converted to the provided unit.
        """
        request = dto.BinaryDeviceMoveRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            type=dto.AxisMoveType.VEL,
            arg=velocity,
            unit=unit,
        )
        response = await call_async(
            "binary/device/move",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def wait_until_idle(
            self
    ) -> None:
        """
        Waits until device stops moving.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        call("binary/device/wait_until_idle", request)

    async def wait_until_idle_async(
            self
    ) -> None:
        """
        Waits until device stops moving.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        await call_async("binary/device/wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Check whether the device is moving.

        Returns:
            True if the device is currently executing a motion command.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call(
            "binary/device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Check whether the device is moving.

        Returns:
            True if the device is currently executing a motion command.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = await call_async(
            "binary/device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def identify(
            self,
            assume_version: Optional[FirmwareVersion] = None
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Args:
            assume_version: The identification assumes the specified firmware version
                instead of the version queried from the device.
                Providing this argument can lead to unexpected compatibility issues.

        Returns:
            Device identification data.
        """
        request = dto.DeviceIdentifyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            assume_version=assume_version,
        )
        response = call(
            "binary/device/identify",
            request,
            DeviceIdentity.from_binary)
        return response

    async def identify_async(
            self,
            assume_version: Optional[FirmwareVersion] = None
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Args:
            assume_version: The identification assumes the specified firmware version
                instead of the version queried from the device.
                Providing this argument can lead to unexpected compatibility issues.

        Returns:
            Device identification data.
        """
        request = dto.DeviceIdentifyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            assume_version=assume_version,
        )
        response = await call_async(
            "binary/device/identify",
            request,
            DeviceIdentity.from_binary)
        return response

    def park(
            self
    ) -> None:
        """
        Parks the axis.
        Motor drivers remain enabled and hold current continues to be applied until the device is powered off.
        It can later be unparked and moved without first having to home it.
        Requires at least Firmware 6.06.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        call("binary/device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the axis.
        Motor drivers remain enabled and hold current continues to be applied until the device is powered off.
        It can later be unparked and moved without first having to home it.
        Requires at least Firmware 6.06.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        await call_async("binary/device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        Requires at least Firmware 6.06.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        call("binary/device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        Requires at least Firmware 6.06.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        await call_async("binary/device/unpark", request)

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.
        Requires at least Firmware 6.06.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call(
            "binary/device/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.
        Requires at least Firmware 6.06.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = await call_async(
            "binary/device/is_parked",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_position(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current device position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = dto.BinaryDeviceGetSettingRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            setting=BinarySettings.CURRENT_POSITION,
            unit=unit,
        )
        response = call(
            "binary/device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_position_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Returns current device position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = dto.BinaryDeviceGetSettingRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            setting=BinarySettings.CURRENT_POSITION,
            unit=unit,
        )
        response = await call_async(
            "binary/device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call_sync(
            "binary/device/device_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def __retrieve_identity(
            self
    ) -> DeviceIdentity:
        """
        Returns identity.

        Returns:
            Device identity.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call_sync(
            "binary/device/get_identity",
            request,
            DeviceIdentity.from_binary)
        return response

    def __retrieve_is_identified(
            self
    ) -> bool:
        """
        Returns whether or not the device have been identified.

        Returns:
            True if the device has already been identified. False otherwise.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call_sync(
            "binary/device/get_is_identified",
            request,
            dto.BoolResponse.from_binary)
        return response.value
