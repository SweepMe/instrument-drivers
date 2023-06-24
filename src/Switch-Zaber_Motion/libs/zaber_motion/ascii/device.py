# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from .device_settings import DeviceSettings
from .axis import Axis
from .all_axes import AllAxes
from .warnings import Warnings
from .device_identity import DeviceIdentity
from .device_io import DeviceIO
from .response import Response
from .lockstep import Lockstep
from .stream import Stream
from .stream_buffer import StreamBuffer
from ..firmware_version import FirmwareVersion
from ..measurement import Measurement

if TYPE_CHECKING:
    from .connection import Connection


class Device:
    """
    Represents the controller part of one device - may be either a standalone controller or an integrated controller.
    """

    @property
    def connection(self) -> 'Connection':
        """
        Connection of this device.
        """
        return self._connection

    @property
    def device_address(self) -> int:
        """
        The device address uniquely identifies the device on the connection.
        It can be configured or automatically assigned by the renumber command.
        """
        return self._device_address

    @property
    def settings(self) -> DeviceSettings:
        """
        Settings and properties of this device.
        """
        return self._settings

    @property
    def io(self) -> DeviceIO:
        """
        I/O channels of this device.
        """
        return self._io

    @property
    def all_axes(self) -> AllAxes:
        """
        Virtual axis which allows you to target all axes of this device.
        """
        return self._all_axes

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this device and all its axes.
        """
        return self._warnings

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
    def axis_count(self) -> int:
        """
        Number of axes this device has.
        """
        return self.identity.axis_count

    @property
    def firmware_version(self) -> FirmwareVersion:
        """
        Version of the firmware.
        """
        return self.identity.firmware_version

    def __init__(self, connection: 'Connection', device_address: int):
        self._connection = connection
        self._device_address = device_address
        self._settings = DeviceSettings(self)
        self._io = DeviceIO(self)
        self._all_axes = AllAxes(self)
        self._warnings = Warnings(self, 0)

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
        request = main_pb2.DeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceIdentity()
        call("device/identify", request, response)
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
        request = main_pb2.DeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceIdentity()
        await call_async("device/identify", request, response)
        return DeviceIdentity.from_protobuf(response)

    def generic_command(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_multi_response(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    def generic_command_no_response(
            self,
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        await call_async("interface/generic_command_no_response", request)

    def get_axis(
            self,
            axis_number: int
    ) -> Axis:
        """
        Gets an Axis class instance which allows you to control a particular axis on this device.
        Axes are numbered from 1.

        Args:
            axis_number: Number of axis intended to control.

        Returns:
            Axis instance.
        """
        if axis_number <= 0:
            raise ValueError('Invalid value; physical axes are numbered from 1.')

        return Axis(self, axis_number)

    def get_lockstep(
            self,
            lockstep_group_id: int
    ) -> Lockstep:
        """
        Gets a Lockstep class instance which allows you to control a particular lockstep group on the device.

        Args:
            lockstep_group_id: The ID of the lockstep group to control. Lockstep group IDs start at one.

        Returns:
            Lockstep instance.
        """
        if lockstep_group_id <= 0:
            raise ValueError('Invalid value; lockstep groups are numbered from 1.')

        return Lockstep(self, lockstep_group_id)

    def prepare_command(
            self,
            command_template: str,
            *parameters: Measurement
    ) -> str:
        """
        Formats parameters into a command and performs unit conversions.
        Parameters in the command template are denoted by a question mark.
        Command returned is only valid for this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of a command to prepare. Parameters are denoted by question marks.
            parameters: Variable number of command parameters.

        Returns:
            Command with converted parameters.
        """
        request = main_pb2.PrepareCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command_template = command_template
        request.parameters.extend([Measurement.to_protobuf(p) for p in parameters])
        response = main_pb2.PrepareCommandResponse()
        call_sync("device/prepare_command", request, response)
        return response.command

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
        call_sync("device/device_to_string", request, response)
        return response.to_str

    def get_stream(
            self,
            stream_id: int
    ) -> Stream:
        """
        Gets a Stream class instance which allows you to control a particular stream on the device.

        Args:
            stream_id: The ID of the stream to control. Stream IDs start at one.

        Returns:
            Stream instance.
        """
        if stream_id <= 0:
            raise ValueError('Invalid value; streams are numbered from 1.')

        return Stream(self, stream_id)

    def get_stream_buffer(
            self,
            stream_buffer_id: int
    ) -> StreamBuffer:
        """
        Gets a StreamBuffer class instance which is a handle for a stream buffer on the device.

        Args:
            stream_buffer_id: The ID of the stream buffer to control. Stream buffer IDs start at one.

        Returns:
            StreamBuffer instance.
        """
        if stream_buffer_id <= 0:
            raise ValueError('Invalid value; stream buffers are numbered from 1.')

        return StreamBuffer(self, stream_buffer_id)

    def __retrieve_identity(
            self
    ) -> DeviceIdentity:
        """
        Returns identity.

        Returns:
            Device identity.
        """
        request = main_pb2.DeviceGetIdentityRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceGetIdentityResponse()
        call_sync("device/get_identity", request, response)
        return DeviceIdentity.from_protobuf(response.identity)

    def __retrieve_is_identified(
            self
    ) -> bool:
        """
        Returns whether or not the device have been identified.

        Returns:
            True if the device has already been identified. False otherwise.
        """
        request = main_pb2.DeviceGetIsIdentifiedRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceGetIsIdentifiedResponse()
        call_sync("device/get_is_identified", request, response)
        return response.is_identified
