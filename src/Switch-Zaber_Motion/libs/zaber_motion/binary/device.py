# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

# pylint: disable=too-many-arguments

from typing import TYPE_CHECKING
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from .binary_settings import BinarySettings
from .device_identity import DeviceIdentity
from .device_settings import DeviceSettings
from .command_code import CommandCode
from .message import Message
from ..units import Units
from .device_type import DeviceType
from ..firmware_version import FirmwareVersion

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
        self._connection = connection
        self._settings = DeviceSettings(self)
        self._device_address = device_address

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
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessage()
        call("binary/interface/generic_command", request, response)
        return Message.from_protobuf(response)

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
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessage()
        await call_async("binary/interface/generic_command", request, response)
        return Message.from_protobuf(response)

    def generic_command_no_response(
            self,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this device without expecting a response.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        call("binary/interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this device without expecting a response.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        await call_async("binary/interface/generic_command_no_response", request)

    def generic_command_with_units(
            self,
            command: CommandCode,
            data: float,
            from_unit: Units = Units.NATIVE,
            to_unit: Units = Units.NATIVE,
            timeout: float = 0.0
    ) -> float:
        """
        Sends a generic Binary command to this device with unit conversions for both sent data and retrieved data.

        Args:
            command: Command to send.
            data: Data argument to the command. Set to zero if command does not require argument.
            from_unit: Unit to convert sent data from.
            to_unit: Unit to convert retrieved data to.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.

        Returns:
            Data that has been converted to the provided unit.
        """
        request = main_pb2.BinaryGenericWithUnitsRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        request.from_unit = from_unit.value
        request.to_unit = to_unit.value
        request.timeout = timeout
        response = main_pb2.BinaryGenericWithUnitsResponse()
        call("binary/device/generic_command_with_units", request, response)
        return response.data

    async def generic_command_with_units_async(
            self,
            command: CommandCode,
            data: float,
            from_unit: Units = Units.NATIVE,
            to_unit: Units = Units.NATIVE,
            timeout: float = 0.0
    ) -> float:
        """
        Sends a generic Binary command to this device with unit conversions for both sent data and retrieved data.

        Args:
            command: Command to send.
            data: Data argument to the command. Set to zero if command does not require argument.
            from_unit: Unit to convert sent data from.
            to_unit: Unit to convert retrieved data to.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.

        Returns:
            Data that has been converted to the provided unit.
        """
        request = main_pb2.BinaryGenericWithUnitsRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command.value
        request.data = data
        request.from_unit = from_unit.value
        request.to_unit = to_unit.value
        request.timeout = timeout
        response = main_pb2.BinaryGenericWithUnitsResponse()
        await call_async("binary/device/generic_command_with_units", request, response)
        return response.data

    def home(
            self,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceHomeRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        call("binary/device/home", request, response)
        return response.data

    async def home_async(
            self,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceHomeRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        await call_async("binary/device/home", request, response)
        return response.data

    def stop(
            self,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceStopRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        call("binary/device/stop", request, response)
        return response.data

    async def stop_async(
            self,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceStopRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        await call_async("binary/device/stop", request, response)
        return response.data

    def move_absolute(
            self,
            position: float,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        call("binary/device/move", request, response)
        return response.data

    async def move_absolute_async(
            self,
            position: float,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        await call_async("binary/device/move", request, response)
        return response.data

    def move_relative(
            self,
            position: float,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        call("binary/device/move", request, response)
        return response.data

    async def move_relative_async(
            self,
            position: float,
            unit: Units = Units.NATIVE,
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
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.timeout = timeout
        response = main_pb2.BinaryDeviceMovementResponse()
        await call_async("binary/device/move", request, response)
        return response.data

    def move_velocity(
            self,
            velocity: float,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Begins to move device at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Unit to convert returned velocity to.

        Returns:
            Device velocity that has been converted to the provided unit.
        """
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        response = main_pb2.BinaryDeviceMovementResponse()
        call("binary/device/move", request, response)
        return response.data

    async def move_velocity_async(
            self,
            velocity: float,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Begins to move device at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Unit to convert returned velocity to.

        Returns:
            Device velocity that has been converted to the provided unit.
        """
        request = main_pb2.BinaryDeviceMoveRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.type = main_pb2.BinaryDeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        response = main_pb2.BinaryDeviceMovementResponse()
        await call_async("binary/device/move", request, response)
        return response.data

    def wait_until_idle(
            self
    ) -> None:
        """
        Waits until device stops moving.
        """
        request = main_pb2.BinaryDeviceWaitUntilIdleRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        call("binary/device/wait_until_idle", request)

    async def wait_until_idle_async(
            self
    ) -> None:
        """
        Waits until device stops moving.
        """
        request = main_pb2.BinaryDeviceWaitUntilIdleRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        await call_async("binary/device/wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Check whether the device is moving.

        Returns:
            True if the device is currently executing a motion command.
        """
        request = main_pb2.BinaryDeviceIsBusyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceIsBusyResponse()
        call("binary/device/is_busy", request, response)
        return response.is_busy

    async def is_busy_async(
            self
    ) -> bool:
        """
        Check whether the device is moving.

        Returns:
            True if the device is currently executing a motion command.
        """
        request = main_pb2.BinaryDeviceIsBusyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceIsBusyResponse()
        await call_async("binary/device/is_busy", request, response)
        return response.is_busy

    def identify(
            self
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Returns:
            Device identification data.
        """
        request = main_pb2.BinaryDeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceIdentity()
        call("binary/device/identify", request, response)
        return DeviceIdentity.from_protobuf(response)

    async def identify_async(
            self
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Returns:
            Device identification data.
        """
        request = main_pb2.BinaryDeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceIdentity()
        await call_async("binary/device/identify", request, response)
        return DeviceIdentity.from_protobuf(response)

    def park(
            self
    ) -> None:
        """
        Parks the axis.
        Motor drivers remain enabled and hold current continues to be applied until the device is powered off.
        It can later be unparked and moved without first having to home it.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        call("binary/device/park", request)

    async def park_async(
            self
    ) -> None:
        """
        Parks the axis.
        Motor drivers remain enabled and hold current continues to be applied until the device is powered off.
        It can later be unparked and moved without first having to home it.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        await call_async("binary/device/park", request)

    def unpark(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        call("binary/device/unpark", request)

    async def unpark_async(
            self
    ) -> None:
        """
        Unparks axis. Axis will now be able to move.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        await call_async("binary/device/unpark", request)

    def is_parked(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceParkResponse()
        call("binary/device/is_parked", request, response)
        return response.is_parked

    async def is_parked_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is parked or not.

        Returns:
            True if the axis is currently parked. False otherwise.
        """
        request = main_pb2.BinaryDeviceParkRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceParkResponse()
        await call_async("binary/device/is_parked", request, response)
        return response.is_parked

    def get_position(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns current device position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.BinaryDeviceGetSettingRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.setting = BinarySettings.CURRENT_POSITION.value
        request.unit = unit.value
        response = main_pb2.BinaryDeviceGetSettingResponse()
        call("binary/device/get_setting", request, response)
        return response.value

    async def get_position_async(
            self,
            unit: Units = Units.NATIVE
    ) -> float:
        """
        Returns current device position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.BinaryDeviceGetSettingRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.setting = BinarySettings.CURRENT_POSITION.value
        request.unit = unit.value
        response = main_pb2.BinaryDeviceGetSettingResponse()
        await call_async("binary/device/get_setting", request, response)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.ToStringResponse()
        call_sync("binary/device/device_to_string", request, response)
        return response.to_str

    def __retrieve_identity(
            self
    ) -> DeviceIdentity:
        """
        Returns identity.

        Returns:
            Device identity.
        """
        request = main_pb2.BinaryDeviceGetIdentityRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceGetIdentityResponse()
        call_sync("binary/device/get_identity", request, response)
        return DeviceIdentity.from_protobuf(response.identity)

    def __retrieve_is_identified(
            self
    ) -> bool:
        """
        Returns whether or not the device have been identified.

        Returns:
            True if the device has already been identified. False otherwise.
        """
        request = main_pb2.BinaryDeviceGetIsIdentifiedRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.BinaryDeviceGetIsIdentifiedResponse()
        call_sync("binary/device/get_is_identified", request, response)
        return response.is_identified
