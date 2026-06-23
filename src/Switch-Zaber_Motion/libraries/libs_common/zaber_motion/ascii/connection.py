# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

import asyncio
from typing import Generator, List, Any, Optional, TypeVar
from reactivex import operators as rxop, Observable
from reactivex.subject import ReplaySubject
from ..call import call, call_async, call_sync
from ..convert_exception import convert_exception
from ..dto import requests as dto
from ..dto.ascii.alert_event import AlertEvent
from ..dto.ascii.mock_device import MockDevice
from ..dto.ascii.response import Response
from ..dto.ascii.unknown_response_event import UnknownResponseEvent
from ..events import filter_events
from ..exceptions.motion_lib_exception import MotionLibException
from .device import Device
from .transport import Transport


TConnectionEvents = TypeVar(
    "TConnectionEvents",
    dto.UnknownResponseEventWrapper,
    dto.AlertEventWrapper,
    dto.DisconnectedEvent)


class Connection:
    """
    Class representing access to particular connection (serial port, TCP connection).
    """

    @property
    def unknown_response(self) -> Observable[UnknownResponseEvent]:
        """
        Event invoked when a response from a device cannot be matched to any known request.
        """
        return self._unknown_response

    @property
    def alert(self) -> Observable[AlertEvent]:
        """
        Event invoked when an alert is received from a device.
        """
        return self._alert

    @property
    def disconnected(self) -> Observable[MotionLibException]:
        """
        Event invoked when connection is interrupted or closed.
        """
        return self._disconnected

    DEFAULT_BAUD_RATE = 115200
    """
    Default baud rate for serial connections.
    """

    TCP_PORT_CHAIN = 55550
    """
    Commands sent over this port are forwarded to the device chain.
    The bandwidth may be limited as the commands are forwarded over a serial connection.
    """

    NETWORK_SHARE_PORT = 11421
    """
    Local area network share port.
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
        The interface ID identifies this Connection instance with the underlying library.
        """
        return self._interface_id

    @property
    def default_request_timeout(self) -> int:
        """
        The default timeout, in milliseconds, for a device to respond to a request.
        Setting the timeout to a too low value may cause request timeout exceptions.
        The initial value is 1000 (one second).
        """
        return self.__retrieve_timeout()

    @default_request_timeout.setter
    def default_request_timeout(self, value: int) -> None:
        """
        The default timeout, in milliseconds, for a device to respond to a request.
        Setting the timeout to a too low value may cause request timeout exceptions.
        The initial value is 1000 (one second).
        """
        self.__change_timeout(value)

    @property
    def checksum_enabled(self) -> bool:
        """
        Controls whether outgoing messages contain checksum.
        """
        return self.__retrieve_checksum_enabled()

    @checksum_enabled.setter
    def checksum_enabled(self, value: bool) -> None:
        """
        Controls whether outgoing messages contain checksum.
        """
        self.__change_checksum_enabled(value)

    @property
    def is_open(self) -> bool:
        """
        Returns whether the connection is open.
        Does not guarantee that subsequent requests will succeed.
        """
        return self.__retrieve_is_open()

    def __init__(self, interface_id: int):
        self._interface_id: int = interface_id
        self.__setup_events(0)

    @staticmethod
    def open_serial_port(
            port_name: str,
            baud_rate: int = DEFAULT_BAUD_RATE,
            direct: bool = False,
            test_port: bool = False
    ) -> 'Connection':
        """
        Opens a serial port, if Zaber Launcher controls the port, the port will be opened through Zaber Launcher.
        Zaber Launcher allows sharing of the port between multiple applications,
        If port sharing is not desirable, use the `direct` parameter.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 115200).
            direct: If true will connect to the serial port directly,
                failing if the connection is already opened by a message router instance.
            test_port: Some operating systems may allow opening a serial port that is not writable.
                Tests if the serial port is writable, and throws an exception if it is not.

        Returns:
            An object representing the port.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.SERIAL_PORT,
            port_name=port_name,
            baud_rate=baud_rate,
            reject_routed_connection=direct,
            test_port=test_port,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_serial_port_async(
            port_name: str,
            baud_rate: int = DEFAULT_BAUD_RATE,
            direct: bool = False,
            test_port: bool = False
    ) -> 'AsyncConnectionOpener':
        """
        Opens a serial port, if Zaber Launcher controls the port, the port will be opened through Zaber Launcher.
        Zaber Launcher allows sharing of the port between multiple applications,
        If port sharing is not desirable, use the `direct` parameter.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 115200).
            direct: If true will connect to the serial port directly,
                failing if the connection is already opened by a message router instance.
            test_port: Some operating systems may allow opening a serial port that is not writable.
                Tests if the serial port is writable, and throws an exception if it is not.

        Returns:
            An object representing the port.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.SERIAL_PORT,
            port_name=port_name,
            baud_rate=baud_rate,
            reject_routed_connection=direct,
            test_port=test_port,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_tcp(
            host_name: str,
            port: int = TCP_PORT_CHAIN
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 55550).

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_tcp_async(
            host_name: str,
            port: int = TCP_PORT_CHAIN
    ) -> 'AsyncConnectionOpener':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 55550).

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_custom(
            transport: Transport
    ) -> 'Connection':
        """
        Opens a connection using a custom transport.

        Args:
            transport: The custom connection transport.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.CUSTOM,
            transport=transport.transport_id,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_custom_async(
            transport: Transport
    ) -> 'AsyncConnectionOpener':
        """
        Opens a connection using a custom transport.

        Args:
            transport: The custom connection transport.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.CUSTOM,
            transport=transport.transport_id,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_iot(
            cloud_id: str,
            token: str = "unauthenticated",
            connection_name: Optional[str] = None,
            realm: Optional[str] = None,
            api: str = "https://api.zaber.io"
    ) -> 'Connection':
        """
        Opens a secured connection to a cloud connected device chain.
        Use this method to connect to devices on your account.

        Args:
            cloud_id: The cloud ID to connect to.
            token: The token to authenticate with. By default the connection will be unauthenticated.
            connection_name: The name of the connection to open.
                Can be left empty to default to the only connection present.
                Otherwise, use serial port name for serial port connection or hostname:port for TCP connection.
            realm: The realm to connect to.
                Can be left empty for the default account realm.
            api: The URL of the API to receive connection info from.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.IOT,
            cloud_id=cloud_id,
            token=token,
            connection_name=connection_name,
            realm=realm,
            api=api,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_iot_async(
            cloud_id: str,
            token: str = "unauthenticated",
            connection_name: Optional[str] = None,
            realm: Optional[str] = None,
            api: str = "https://api.zaber.io"
    ) -> 'AsyncConnectionOpener':
        """
        Opens a secured connection to a cloud connected device chain.
        Use this method to connect to devices on your account.

        Args:
            cloud_id: The cloud ID to connect to.
            token: The token to authenticate with. By default the connection will be unauthenticated.
            connection_name: The name of the connection to open.
                Can be left empty to default to the only connection present.
                Otherwise, use serial port name for serial port connection or hostname:port for TCP connection.
            realm: The realm to connect to.
                Can be left empty for the default account realm.
            api: The URL of the API to receive connection info from.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.IOT,
            cloud_id=cloud_id,
            token=token,
            connection_name=connection_name,
            realm=realm,
            api=api,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_network_share(
            host_name: str,
            port: int = NETWORK_SHARE_PORT,
            connection_name: Optional[str] = None
    ) -> 'Connection':
        """
        Opens a connection to Zaber Launcher in your Local Area Network.
        The connection is not secured.

        Args:
            host_name: Hostname or IP address.
            port: Port number.
            connection_name: The name of the connection to open.
                Can be left empty to default to the only connection present.
                Otherwise, use serial port name for serial port connection or hostname:port for TCP connection.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.NETWORK_SHARE,
            host_name=host_name,
            port=port,
            connection_name=connection_name,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_network_share_async(
            host_name: str,
            port: int = NETWORK_SHARE_PORT,
            connection_name: Optional[str] = None
    ) -> 'AsyncConnectionOpener':
        """
        Opens a connection to Zaber Launcher in your Local Area Network.
        The connection is not secured.

        Args:
            host_name: Hostname or IP address.
            port: Port number.
            connection_name: The name of the connection to open.
                Can be left empty to default to the only connection present.
                Otherwise, use serial port name for serial port connection or hostname:port for TCP connection.

        Returns:
            An object representing the connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.NETWORK_SHARE,
            host_name=host_name,
            port=port,
            connection_name=connection_name,
        )
        return AsyncConnectionOpener(request)

    @staticmethod
    def open_mock(
            devices: List[MockDevice]
    ) -> 'Connection':
        """
        Opens a mock connection with mock devices for testing purposes.
        The mock connection cannot be used for communication with mock devices.

        Args:
            devices: List of mock devices.

        Returns:
            An object representing the mock connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.MOCK,
            mock_devices=devices,
        )
        response = call(
            "interface/open",
            request,
            dto.OpenInterfaceResponse.from_binary)
        return Connection(response.interface_id)

    @staticmethod
    def open_mock_async(
            devices: List[MockDevice]
    ) -> 'AsyncConnectionOpener':
        """
        Opens a mock connection with mock devices for testing purposes.
        The mock connection cannot be used for communication with mock devices.

        Args:
            devices: List of mock devices.

        Returns:
            An object representing the mock connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.MOCK,
            mock_devices=devices,
        )
        return AsyncConnectionOpener(request)

    def reopen(
            self
    ) -> None:
        """
        Reopens the connection.
        To continue using events on the connection, you must resubscribe to event observables.
        Throws an exception if the connection is already open.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call(
            "interface/reopen",
            request,
            dto.IntResponse.from_binary)
        self.__setup_events(response.value)

    async def reopen_async(
            self
    ) -> None:
        """
        Reopens the connection.
        To continue using events on the connection, you must resubscribe to event observables.
        Throws an exception if the connection is already open.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = await call_async(
            "interface/reopen",
            request,
            dto.IntResponse.from_binary)
        self.__setup_events(response.value)

    def generic_command(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this connection.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
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
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this connection.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = await call_async(
            "interface/generic_command",
            request,
            Response.from_binary)
        return response

    def generic_command_no_response(
            self,
            command: str,
            device: int = 0,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this connection without expecting a response and without adding a message ID.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
                Specifying -1 omits the number completely.
            axis: Optional axis number to send the command to.
                Specifying -1 omits the number completely.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
        )
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str,
            device: int = 0,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this connection without expecting a response and without adding a message ID.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
                Specifying -1 omits the number completely.
            axis: Optional axis number to send the command to.
                Specifying -1 omits the number completely.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
        )
        await call_async("interface/generic_command_no_response", request)

    def generic_command_multi_response(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this connection and expect multiple responses,
        either from one device or from many devices.
        Responses are returned in order of arrival.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
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
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this connection and expect multiple responses,
        either from one device or from many devices.
        Responses are returned in order of arrival.
        For more information refer to the ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command=command,
            device=device,
            axis=axis,
            check_errors=check_errors,
            timeout=timeout,
        )
        response = await call_async(
            "interface/generic_command_multi_response",
            request,
            dto.GenericCommandResponseCollection.from_binary)
        return response.responses

    def enable_alerts(
            self
    ) -> None:
        """
        Enables alerts for all devices on the connection.
        This will change the "comm.alert" setting to 1 on all supported devices.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command="set comm.alert 1",
        )
        call("interface/generic_command_no_response", request)

    async def enable_alerts_async(
            self
    ) -> None:
        """
        Enables alerts for all devices on the connection.
        This will change the "comm.alert" setting to 1 on all supported devices.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command="set comm.alert 1",
        )
        await call_async("interface/generic_command_no_response", request)

    def disable_alerts(
            self
    ) -> None:
        """
        Disables alerts for all devices on the connection.
        This will change the "comm.alert" setting to 0 on all supported devices.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command="set comm.alert 0",
        )
        call("interface/generic_command_no_response", request)

    async def disable_alerts_async(
            self
    ) -> None:
        """
        Disables alerts for all devices on the connection.
        This will change the "comm.alert" setting to 0 on all supported devices.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.interface_id,
            command="set comm.alert 0",
        )
        await call_async("interface/generic_command_no_response", request)

    def reset_ids(
            self
    ) -> None:
        """
        Resets ASCII protocol message IDs. Only for testing purposes.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        call_sync("interface/reset_ids", request)

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

    def renumber_devices(
            self,
            first_address: int = 1
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, devices need to be identified again.

        Args:
            first_address: This is the address that the device closest to the computer is given.
                Remaining devices are numbered consecutively.

        Returns:
            Total number of devices that responded to the renumber.
        """
        if first_address <= 0:
            raise ValueError('Invalid value; device addresses are numbered from 1.')

        request = dto.RenumberRequest(
            interface_id=self.interface_id,
            address=first_address,
        )
        response = call(
            "device/renumber_all",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def renumber_devices_async(
            self,
            first_address: int = 1
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, devices need to be identified again.

        Args:
            first_address: This is the address that the device closest to the computer is given.
                Remaining devices are numbered consecutively.

        Returns:
            Total number of devices that responded to the renumber.
        """
        if first_address <= 0:
            raise ValueError('Invalid value; device addresses are numbered from 1.')

        request = dto.RenumberRequest(
            interface_id=self.interface_id,
            address=first_address,
        )
        response = await call_async(
            "device/renumber_all",
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
        request = dto.DeviceDetectRequest(
            interface_id=self.interface_id,
            identify_devices=identify_devices,
        )
        response = call(
            "device/detect",
            request,
            dto.DeviceDetectResponse.from_binary)
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
        request = dto.DeviceDetectRequest(
            interface_id=self.interface_id,
            identify_devices=identify_devices,
        )
        response = await call_async(
            "device/detect",
            request,
            dto.DeviceDetectResponse.from_binary)
        return list(map(self.get_device, response.devices))

    def forget_devices(
            self,
            except_devices: List[int] = []
    ) -> None:
        """
        Forgets all the information associated with devices on the connection.
        Useful when devices are removed from the chain indefinitely.

        Args:
            except_devices: Addresses of devices that should not be forgotten.
        """
        request = dto.ForgetDevicesRequest(
            interface_id=self.interface_id,
            except_devices=except_devices,
        )
        call_sync("device/forget", request)

    def stop_all(
            self,
            wait_until_idle: bool = True
    ) -> List[int]:
        """
        Stops all of the devices on this connection.

        Args:
            wait_until_idle: Determines whether the function should return immediately
                or wait until the devices are stopped.

        Returns:
            The addresses of the devices that were stopped by this command.
        """
        request = dto.DeviceOnAllRequest(
            interface_id=self.interface_id,
            wait_until_idle=wait_until_idle,
        )
        response = call(
            "device/stop_all",
            request,
            dto.DeviceOnAllResponse.from_binary)
        return response.device_addresses

    async def stop_all_async(
            self,
            wait_until_idle: bool = True
    ) -> List[int]:
        """
        Stops all of the devices on this connection.

        Args:
            wait_until_idle: Determines whether the function should return immediately
                or wait until the devices are stopped.

        Returns:
            The addresses of the devices that were stopped by this command.
        """
        request = dto.DeviceOnAllRequest(
            interface_id=self.interface_id,
            wait_until_idle=wait_until_idle,
        )
        response = await call_async(
            "device/stop_all",
            request,
            dto.DeviceOnAllResponse.from_binary)
        return response.device_addresses

    def home_all(
            self,
            wait_until_idle: bool = True
    ) -> List[int]:
        """
        Homes all of the devices on this connection.

        Args:
            wait_until_idle: Determines whether the function should return immediately
                or wait until the devices are homed.

        Returns:
            The addresses of the devices that were homed by this command.
        """
        request = dto.DeviceOnAllRequest(
            interface_id=self.interface_id,
            wait_until_idle=wait_until_idle,
        )
        response = call(
            "device/home_all",
            request,
            dto.DeviceOnAllResponse.from_binary)
        return response.device_addresses

    async def home_all_async(
            self,
            wait_until_idle: bool = True
    ) -> List[int]:
        """
        Homes all of the devices on this connection.

        Args:
            wait_until_idle: Determines whether the function should return immediately
                or wait until the devices are homed.

        Returns:
            The addresses of the devices that were homed by this command.
        """
        request = dto.DeviceOnAllRequest(
            interface_id=self.interface_id,
            wait_until_idle=wait_until_idle,
        )
        response = await call_async(
            "device/home_all",
            request,
            dto.DeviceOnAllResponse.from_binary)
        return response.device_addresses

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

    def __retrieve_timeout(
            self
    ) -> int:
        """
        Returns default request timeout.

        Returns:
            Default request timeout.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call_sync(
            "interface/get_timeout",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def __change_timeout(
            self,
            timeout: int
    ) -> None:
        """
        Sets default request timeout.

        Args:
            timeout: Default request timeout.
        """
        request = dto.SetInterfaceTimeoutRequest(
            interface_id=self.interface_id,
            timeout=timeout,
        )
        call_sync("interface/set_timeout", request)

    def __retrieve_checksum_enabled(
            self
    ) -> bool:
        """
        Returns checksum enabled.

        Returns:
            Checksum enabled.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.interface_id,
        )
        response = call_sync(
            "interface/get_checksum_enabled",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def __change_checksum_enabled(
            self,
            is_enabled: bool
    ) -> None:
        """
        Sets checksum enabled.

        Args:
            is_enabled: Checksum enabled.
        """
        request = dto.SetInterfaceChecksumEnabledRequest(
            interface_id=self.interface_id,
            is_enabled=is_enabled,
        )
        call_sync("interface/set_checksum_enabled", request)

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

    def __setup_events(self, session_id: int) -> None:
        # Bind the interface ID into a local so the closure below does not capture self.
        interface_id = self._interface_id

        def filter_connection_event(
            data: TConnectionEvents,
        ) -> bool:
            return data.interface_id == interface_id and data.session_id == session_id

        self._disconnected = ReplaySubject[MotionLibException]()  # terminates all the events

        unknown_response = filter_events('interface/unknown_response', dto.UnknownResponseEventWrapper)
        self._unknown_response = unknown_response.pipe(
            rxop.filter(filter_connection_event),
            rxop.take_until(self.disconnected),
            rxop.map(map_unknown_response)
        )

        alert = filter_events('interface/alert', dto.AlertEventWrapper)
        self._alert = alert.pipe(
            rxop.filter(filter_connection_event),
            rxop.take_until(self.disconnected),
            rxop.map(map_alert)
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


def map_unknown_response(event: dto.UnknownResponseEventWrapper) -> UnknownResponseEvent:
    return event.unknown_response


def map_alert(event: dto.AlertEventWrapper) -> AlertEvent:
    return event.alert


def map_disconnect(event: dto.DisconnectedEvent) -> MotionLibException:
    return convert_exception(event.error_type, event.error_message)


class AsyncConnectionOpener:
    '''Async context manager for Connection.'''
    def __init__(self, request: dto.OpenInterfaceRequest) -> None:
        self._request = request
        self._resource: Optional[Connection] = None

    async def _create_resource(self) -> Connection:
        task = asyncio.ensure_future(call_async(
            "interface/open",
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
