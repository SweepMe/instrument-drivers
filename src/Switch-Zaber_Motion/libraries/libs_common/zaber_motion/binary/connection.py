# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

import asyncio
from typing import Generator, List, Any, Optional, TypeVar
from reactivex import operators as rxop, Observable
from reactivex.subject import ReplaySubject
from ..call import call, call_async, call_sync
from ..convert_exception import convert_exception
from ..dto import requests as dto
from ..dto.binary.command_code import CommandCode
from ..dto.binary.message import Message
from ..dto.binary.reply_only_event import ReplyOnlyEvent
from ..dto.binary.unknown_response_event import UnknownResponseEvent
from ..events import filter_events
from ..exceptions.motion_lib_exception import MotionLibException
from .device import Device


TConnectionEvents = TypeVar(
    "TConnectionEvents",
    dto.UnknownBinaryResponseEventWrapper,
    dto.BinaryReplyOnlyEventWrapper,
    dto.DisconnectedEvent)


class Connection:
    """
    Class representing access to particular connection (serial port, TCP connection) using the legacy Binary protocol.
    """

    @property
    def unknown_response(self) -> Observable[UnknownResponseEvent]:
        """
        Event invoked when a response from a device cannot be matched to any known request.
        """
        return self._unknown_response

    @property
    def reply_only(self) -> Observable[ReplyOnlyEvent]:
        """
        Event invoked when a reply-only command such as a move tracking message is received from a device.
        """
        return self._reply_only

    @property
    def disconnected(self) -> Observable[MotionLibException]:
        """
        Event invoked when connection is interrupted or closed.
        """
        return self._disconnected

    DEFAULT_BAUD_RATE = 9600
    """
    Default baud rate for serial connections.
    """

    TCP_PORT_CHAIN = 55550
    """
    Commands sent over this port are forwarded to the device chain.
    The bandwidth may be limited as the commands are forwarded over a serial connection.
    """

    TCP_PORT_DEVICE_ONLY = 55551
    """
    Commands send over this port are processed only by the device
    and not forwarded to the rest of the chain.
    Using this port typically makes the communication faster.
    """

    @property
    def interface_id(self) -> int:
        """
        The interface ID identifies thisConnection instance with the underlying library.
        """
        return self._interface_id

    @property
    def is_open(self) -> bool:
        """
        Returns whether the connection is open.
        Does not guarantee that the subsequent requests will succeed.
        """
        return self.__retrieve_is_open()

    def __init__(self, interface_id: int):
        self._interface_id: int = interface_id
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
        request = dto.OpenBinaryInterfaceRequest(
            interface_type=dto.InterfaceType.SERIAL_PORT,
            port_name=port_name,
            baud_rate=baud_rate,
            use_message_ids=use_message_ids,
        )
        response = call(
            "binary/interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_serial_port_async(
            port_name: str,
            baud_rate: int = DEFAULT_BAUD_RATE,
            use_message_ids: bool = False
    ) -> 'AsyncConnectionOpener':
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
        request = dto.OpenBinaryInterfaceRequest(
            interface_type=dto.InterfaceType.SERIAL_PORT,
            port_name=port_name,
            baud_rate=baud_rate,
            use_message_ids=use_message_ids,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_tcp(
            host_name: str,
            port: int = TCP_PORT_CHAIN,
            use_message_ids: bool = False
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 55550).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenBinaryInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
            use_message_ids=use_message_ids,
        )
        response = call(
            "binary/interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_tcp_async(
            host_name: str,
            port: int = TCP_PORT_CHAIN,
            use_message_ids: bool = False
    ) -> 'AsyncConnectionOpener':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 55550).
            use_message_ids: Enable use of message IDs (defaults to disabled).
                All your devices must be pre-configured to match.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenBinaryInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
            use_message_ids=use_message_ids,
        )
        return AsyncConnectionOpener(request)

    def close(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        call("interface/close", request)

    async def close_async(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
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
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            device=device,
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
            device: int,
            command: CommandCode,
            data: int = 0,
            timeout: float = 0.0,
            check_errors: bool = True
    ) -> Message:
        """
        Sends a generic Binary command to this connection.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for a response from the device. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when the device rejects the command.

        Returns:
            A response to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            device=device,
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
            device: int,
            command: CommandCode,
            data: int = 0
    ) -> None:
        """
        Sends a generic Binary command to this connection without expecting a response.
        For more information please refer to the
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            device=device,
            command=command,
            data=data,
        )
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
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            device: Device address to send the command to. Use zero for broadcast.
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            device=device,
            command=command,
            data=data,
        )
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
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for all responses from the device chain. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when any device rejects the command.

        Returns:
            All responses to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            command=command,
            data=data,
            timeout=timeout,
            check_errors=check_errors,
        )
        response = call(
            "binary/interface/generic_command_multi_response",
            request,
            dto.BinaryMessageCollection.from_binary)
        return response.messages

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
        Binary Protocol Manual (https://www.zaber.com/protocol-manual?protocol=Binary#topic_quick_command_reference).

        Args:
            command: Command to send.
            data: Optional data argument to the command. Defaults to zero.
            timeout: Number of seconds to wait for all responses from the device chain. 0 or negative defaults to 0.5s.
            check_errors: Controls whether to throw an exception when any device rejects the command.

        Returns:
            All responses to the command.
        """
        request = dto.GenericBinaryRequest(
            interface_id=self.interface_id,
            command=command,
            data=data,
            timeout=timeout,
            check_errors=check_errors,
        )
        response = await call_async(
            "binary/interface/generic_command_multi_response",
            request,
            dto.BinaryMessageCollection.from_binary)
        return response.messages

    def renumber_devices(
            self
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, you must identify devices again.

        Returns:
            Total number of devices that responded to the renumber.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call(
            "binary/device/renumber",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def renumber_devices_async(
            self
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, you must identify devices again.

        Returns:
            Total number of devices that responded to the renumber.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = await call_async(
            "binary/device/renumber",
            request,
            dto.IntResponse.from_binary)
        return response.value

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
        request = dto.BinaryDeviceDetectRequest(
            interface_id=self.interface_id,
            identify_devices=identify_devices,
        )
        response = call(
            "binary/device/detect",
            request,
            dto.BinaryDeviceDetectResponse.from_binary)
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
        request = dto.BinaryDeviceDetectRequest(
            interface_id=self.interface_id,
            identify_devices=identify_devices,
        )
        response = await call_async(
            "binary/device/detect",
            request,
            dto.BinaryDeviceDetectResponse.from_binary)
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

    def __retrieve_is_open(
            self
    ) -> bool:
        """
        Returns is open.

        Returns:
            Is open.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call_sync(
            "interface/get_is_open",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the connection.

        Returns:
            A string that represents the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call_sync(
            "interface/to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    @staticmethod
    def __free(
            interface_id: int
    ) -> None:
        """
        Releases native resources of the connection.

        Args:
            interface_id: The ID of the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=interface_id,
        )
        call_sync("interface/free", request)

    def __setup_events(self) -> None:
        # Bind the interface ID into a local so the closure below does not capture self.
        interface_id = self._interface_id

        def filter_connection_event(
            data: TConnectionEvents,
        ) -> bool:
            return data.interface_id == interface_id

        self._disconnected = ReplaySubject[MotionLibException]()  # terminates all the events

        unknown_response = filter_events('binary/interface/unknown_response', dto.UnknownBinaryResponseEventWrapper)
        self._unknown_response = unknown_response.pipe(
            rxop.filter(filter_connection_event),
            rxop.take_until(self.disconnected),
            rxop.map(map_unknown_response)
        )

        reply_only = filter_events('binary/interface/reply_only', dto.BinaryReplyOnlyEventWrapper)
        self._reply_only = reply_only.pipe(
            rxop.filter(filter_connection_event),
            rxop.take_until(self.disconnected),
            rxop.map(map_reply_only)
        )

        disconnected = filter_events('interface/disconnected', dto.DisconnectedEvent)
        disconnected.pipe(
            rxop.filter(filter_connection_event),
            rxop.take(1),
            rxop.map(map_disconnect)
        ).subscribe(self._disconnected)

    def __enter__(self) -> 'Connection':
        """ __enter__ """
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        """ __exit__ """
        self.close()

    def __del__(self) -> None:
        Connection.__free(self._interface_id)


def map_unknown_response(event: dto.UnknownBinaryResponseEventWrapper) -> UnknownResponseEvent:
    return event.unknown_response


def map_reply_only(event: dto.BinaryReplyOnlyEventWrapper) -> ReplyOnlyEvent:
    return event.reply


def map_disconnect(event: dto.DisconnectedEvent) -> MotionLibException:
    return convert_exception(event.error_type, event.error_message)


class AsyncConnectionOpener:
    '''Async context manager for Connection.'''
    def __init__(self, request: dto.OpenBinaryInterfaceRequest) -> None:
        self._request = request
        self._resource: Optional[Connection] = None

    async def _create_resource(self) -> Connection:
        task = asyncio.ensure_future(call_async(
            "binary/interface/open",
            self._request,
            dto.OpenInterfaceResponse.from_binary))

        try:
            response = await asyncio.shield(task)
        except asyncio.CancelledError:
            async def cancel() -> None:
                try:
                    response = await task
                    await Connection(response.interface_id).close_async()
                except MotionLibException:
                    pass

            asyncio.ensure_future(cancel())
            raise

        return Connection(response.interface_id)

    def __await__(self) -> Generator[Any, None, 'Connection']:
        return self._create_resource().__await__()

    async def __aenter__(self) -> 'Connection':
        self._resource = await self._create_resource()
        return self._resource

    async def __aexit__(self, exc_type: Any, exc: Any, trace: Any) -> None:
        if self._resource is not None:
            await self._resource.close_async()
