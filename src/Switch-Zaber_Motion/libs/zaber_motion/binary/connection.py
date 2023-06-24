# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

# pylint: disable=too-many-arguments

from typing import List, Any, Callable
import asyncio
from rx.subject import ReplaySubject
from rx.core import Observable
from rx import operators as rxop

from ..call import call, call_async, call_sync
from ..convert_exception import convert_exception
from ..events import events
from ..exceptions.motion_lib_exception import MotionLibException

from .device import Device
from .command_code import CommandCode
from .message import Message
from .unknown_response_event import UnknownResponseEvent
from .reply_only_event import ReplyOnlyEvent
from ..protobufs import main_pb2


class Connection:
    """
    Class representing access to particular connection (serial port, TCP connection) using the legacy Binary protocol.
    """

    @property
    def unknown_response(self) -> Observable:
        """
        Event invoked when a response from a device cannot be matched to any known request.
        """
        return self._unknown_response

    @property
    def reply_only(self) -> Observable:
        """
        Event invoked when a reply-only command such as a move tracking message is received from a device.
        """
        return self._reply_only

    @property
    def disconnected(self) -> Observable:
        """
        Event invoked when connection is interrupted or closed.
        """
        return self._disconnected

    DEFAULT_BAUD_RATE = 9600
    """
    Default baud rate for serial connections.
    """

    @property
    def interface_id(self) -> int:
        """
        The interface ID identifies thisConnection instance with the underlying library.
        """
        return self._interface_id

    def __init__(self, interface_id: int):
        self._interface_id = interface_id
        self.__setup_events()

    @staticmethod
    def open_serial_port(
            port_name: str,
            baud_rate: int = DEFAULT_BAUD_RATE,
            use_message_ids: bool = False
    ) -> 'Connection':
        """
        Opens a serial port.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 9600).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the port.
        """
        request = main_pb2.OpenBinaryInterfaceRequest()
        request.interface_type = main_pb2.SERIAL_PORT
        request.port_name = port_name
        request.baud_rate = baud_rate
        request.use_message_ids = use_message_ids
        response = main_pb2.OpenInterfaceResponse()
        call("binary/interface/open", request, response)
        return Connection(response.interface_id)

    @staticmethod
    async def open_serial_port_async(
            port_name: str,
            baud_rate: int = DEFAULT_BAUD_RATE,
            use_message_ids: bool = False
    ) -> 'Connection':
        """
        Opens a serial port.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 9600).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the port.
        """
        request = main_pb2.OpenBinaryInterfaceRequest()
        request.interface_type = main_pb2.SERIAL_PORT
        request.port_name = port_name
        request.baud_rate = baud_rate
        request.use_message_ids = use_message_ids
        response = main_pb2.OpenInterfaceResponse()
        task = asyncio.ensure_future(call_async("binary/interface/open", request, response))

        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            async def cancel() -> None:
                try:
                    await task
                    await Connection(response.interface_id).close_async()
                except MotionLibException:
                    pass

            asyncio.ensure_future(cancel())
            raise

        return Connection(response.interface_id)

    @staticmethod
    def open_tcp(
            host_name: str,
            port: int = 0,
            use_message_ids: bool = False
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 8657).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the connection.
        """
        request = main_pb2.OpenBinaryInterfaceRequest()
        request.interface_type = main_pb2.TCP
        request.host_name = host_name
        request.port = port
        request.use_message_ids = use_message_ids
        response = main_pb2.OpenInterfaceResponse()
        call("binary/interface/open", request, response)
        return Connection(response.interface_id)

    @staticmethod
    async def open_tcp_async(
            host_name: str,
            port: int = 0,
            use_message_ids: bool = False
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 8657).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the connection.
        """
        request = main_pb2.OpenBinaryInterfaceRequest()
        request.interface_type = main_pb2.TCP
        request.host_name = host_name
        request.port = port
        request.use_message_ids = use_message_ids
        response = main_pb2.OpenInterfaceResponse()
        task = asyncio.ensure_future(call_async("binary/interface/open", request, response))

        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            async def cancel() -> None:
                try:
                    await task
                    await Connection(response.interface_id).close_async()
                except MotionLibException:
                    pass

            asyncio.ensure_future(cancel())
            raise

        return Connection(response.interface_id)

    def close(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = main_pb2.CloseInterfaceRequest()
        request.interface_id = self.interface_id
        call("interface/close", request)

    async def close_async(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = main_pb2.CloseInterfaceRequest()
        request.interface_id = self.interface_id
        await call_async("interface/close", request)

    def generic_command(
            self,
            device: int,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> Message:
        """
        Sends a generic Binary command to this connection.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.device = device
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessage()
        call("binary/interface/generic_command", request, response)
        return Message.from_protobuf(response)

    async def generic_command_async(
            self,
            device: int,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> Message:
        """
        Sends a generic Binary command to this connection.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.device = device
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessage()
        await call_async("binary/interface/generic_command", request, response)
        return Message.from_protobuf(response)

    def generic_command_no_response(
            self,
            device: int,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this connection without expecting a response.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.device = device
        request.command = command.value
        request.data = data
        call("binary/interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            device: int,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this connection without expecting a response.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.device = device
        request.command = command.value
        request.data = data
        await call_async("binary/interface/generic_command_no_response", request)

    def generic_command_multi_response(
            self,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> List[Message]:
        """
        Sends a generic Binary command to this connection and expects responses from one or more devices.
        Responses are returned in order of arrival.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for all responses from the device chain. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when any device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessageCollection()
        call("binary/interface/generic_command_multi_response", request, response)
        return [Message.from_protobuf(resp) for resp in response.messages]

    async def generic_command_multi_response_async(
            self,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> List[Message]:
        """
        Sends a generic Binary command to this connection and expects responses from one or more devices.
        Responses are returned in order of arrival.
        For more information please refer to the
        [Binary Protocol Manual](https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for all responses from the device chain. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when any device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericBinaryRequest()
        request.interface_id = self.interface_id
        request.command = command.value
        request.data = data
        request.timeout = timeout
        request.check_errors = check_errors
        response = main_pb2.BinaryMessageCollection()
        await call_async("binary/interface/generic_command_multi_response", request, response)
        return [Message.from_protobuf(resp) for resp in response.messages]

    def renumber_devices(
            self
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, you must identify devices again.

        Returns:
            Total number of devices that responded to the renumber.
        """
        request = main_pb2.BinaryDeviceRenumberRequest()
        request.interface_id = self.interface_id
        response = main_pb2.BinaryDeviceRenumberResponse()
        call("binary/device/renumber", request, response)
        return response.number_devices

    async def renumber_devices_async(
            self
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, you must identify devices again.

        Returns:
            Total number of devices that responded to the renumber.
        """
        request = main_pb2.BinaryDeviceRenumberRequest()
        request.interface_id = self.interface_id
        response = main_pb2.BinaryDeviceRenumberResponse()
        await call_async("binary/device/renumber", request, response)
        return response.number_devices

    def detect_devices(
            self,
            identify_devices: bool = True
    ) -> List[Device]:
        """
        Attempts to detect any devices present on this connection.

        Args:
            identify_devices: Determines whether device identification should be performed as well.

        Returns:
            Array of detected devices.
        """
        request = main_pb2.BinaryDeviceDetectRequest()
        request.interface_id = self.interface_id
        request.identify_devices = identify_devices
        response = main_pb2.BinaryDeviceDetectResponse()
        call("binary/device/detect", request, response)
        return list(map(self.get_device, response.devices))

    async def detect_devices_async(
            self,
            identify_devices: bool = True
    ) -> List[Device]:
        """
        Attempts to detect any devices present on this connection.

        Args:
            identify_devices: Determines whether device identification should be performed as well.

        Returns:
            Array of detected devices.
        """
        request = main_pb2.BinaryDeviceDetectRequest()
        request.interface_id = self.interface_id
        request.identify_devices = identify_devices
        response = main_pb2.BinaryDeviceDetectResponse()
        await call_async("binary/device/detect", request, response)
        return list(map(self.get_device, response.devices))

    def get_device(
            self,
            device_address: int
    ) -> Device:
        """
        Gets a Device class instance which allows you to control a particular device on this connection.
        Devices are numbered from 1.

        Args:
            device_address: Address of device intended to control. Address is configured for each device.

        Returns:
            Device instance.
        """
        if device_address <= 0:
            raise ValueError('Invalid value; physical devices are numbered from 1.')

        return Device(self, device_address)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the connection.

        Returns:
            A string that represents the connection.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.interface_id
        response = main_pb2.ToStringResponse()
        call_sync("interface/to_string", request, response)
        return response.to_str

    def __enter__(self) -> 'Connection':
        """ __enter__ """
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        """ __exit__ """
        self.close()

    def __filter_event(self, event_name: str) -> Callable[[Any], bool]:
        def filter_event(event: Any) -> bool:
            return event[0] == event_name and event[1].interface_id == self._interface_id  # type: ignore
        return filter_event

    def __setup_events(self) -> None:
        self._disconnected = ReplaySubject()  # terminates all the events

        self._unknown_response = events.pipe(
            rxop.take_until(self.disconnected),
            rxop.filter(self.__filter_event('binary/interface/unknown_response')),
            rxop.map(lambda ev: UnknownResponseEvent.from_protobuf(ev[1]))
        )

        self._reply_only = events.pipe(
            rxop.take_until(self.disconnected),
            rxop.filter(self.__filter_event('binary/interface/reply_only')),
            rxop.map(lambda ev: ReplyOnlyEvent.from_protobuf(ev[1]))
        )

        events.pipe(
            rxop.filter(self.__filter_event('interface/disconnected')),
            rxop.take(1),
            rxop.map(lambda ev: convert_exception(ev[1].error_type, ev[1].error_message))
        ).subscribe(self._disconnected)
