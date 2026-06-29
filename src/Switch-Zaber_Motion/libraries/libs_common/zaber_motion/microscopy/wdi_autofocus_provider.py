# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

import asyncio
from typing import Generator, Any, Optional, List
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.firmware_version import FirmwareVersion
from ..dto.microscopy.wdi_autofocus_provider_status import WdiAutofocusProviderStatus
from ..exceptions.motion_lib_exception import MotionLibException


class WdiAutofocusProvider:
    """
    Class representing access to WDI Autofocus connection.
    """

    DEFAULT_TCP_PORT = 27
    """
    Default port number for TCP connections to WDI autofocus.
    """

    @property
    def provider_id(self) -> int:
        """
        The ID identifies the autofocus with the underlying library.
        """
        return self._provider_id

    @property
    def firmware_version(self) -> FirmwareVersion:
        """
        The firmware version of the connected autofocus.
        """
        return self.__retrieve_firmware_version()

    def __init__(self, provider_id: int):
        self._provider_id: int = provider_id

    @staticmethod
    def open_tcp(
            host_name: str,
            port: int = DEFAULT_TCP_PORT
    ) -> 'WdiAutofocusProvider':
        """
        Opens a TCP connection to WDI autofocus.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 27).

        Returns:
            An object representing the autofocus connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
        )
        response = call(
            "wdi/open",
            request,
            dto.IntResponse.from_binary)
        return WdiAutofocusProvider(response.value)

    @staticmethod
    def open_tcp_async(
            host_name: str,
            port: int = DEFAULT_TCP_PORT
    ) -> 'AsyncWdiAutofocusProviderOpener':
        """
        Opens a TCP connection to WDI autofocus.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 27).

        Returns:
            An object representing the autofocus connection.
        """
        request = dto.OpenInterfaceRequest(
            interface_type=dto.InterfaceType.TCP,
            host_name=host_name,
            port=port,
        )
        return AsyncWdiAutofocusProviderOpener(request)

    def close(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        call("wdi/close", request)

    async def close_async(
            self
    ) -> None:
        """
        Close the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        await call_async("wdi/close", request)

    @staticmethod
    def __free(
            provider_id: int
    ) -> None:
        """
        Frees the connection.

        Args:
            provider_id: The ID of the connection to free.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=provider_id,
        )
        call_sync("wdi/free", request)

    def __retrieve_firmware_version(
            self
    ) -> FirmwareVersion:
        """
        Returns FW version.

        Returns:
            Firmware version.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        response = call_sync(
            "wdi/get_firmware_version",
            request,
            FirmwareVersion.from_binary)
        return response

    def generic_read(
            self,
            register_id: int,
            size: int,
            count: int = 1,
            offset: int = 0,
            register_bank: str = "U"
    ) -> List[int]:
        """
        Generic read operation.

        Args:
            register_id: Register address to read from.
            size: Data size to read. Valid values are (1,2,4). Determines the data type (Byte, Word, DWord).
            count: Number of values to read (defaults to 1).
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).

        Returns:
            Array of integers read from the device.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            size=size,
            count=count,
            offset=offset,
            register_bank=register_bank,
        )
        response = call(
            "wdi/read",
            request,
            dto.IntArrayResponse.from_binary)
        return response.values

    async def generic_read_async(
            self,
            register_id: int,
            size: int,
            count: int = 1,
            offset: int = 0,
            register_bank: str = "U"
    ) -> List[int]:
        """
        Generic read operation.

        Args:
            register_id: Register address to read from.
            size: Data size to read. Valid values are (1,2,4). Determines the data type (Byte, Word, DWord).
            count: Number of values to read (defaults to 1).
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).

        Returns:
            Array of integers read from the device.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            size=size,
            count=count,
            offset=offset,
            register_bank=register_bank,
        )
        response = await call_async(
            "wdi/read",
            request,
            dto.IntArrayResponse.from_binary)
        return response.values

    def generic_write(
            self,
            register_id: int,
            size: int = 0,
            data: List[int] = [],
            offset: int = 0,
            register_bank: str = "U"
    ) -> None:
        """
        Generic write operation.

        Args:
            register_id: Register address to write to.
            size: Data size to write. Valid values are (0,1,2,4). Determines the data type (Nil, Byte, Word, DWord).
            data: Array of values to write to the register. Empty array is allowed.
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            size=size,
            data=data,
            offset=offset,
            register_bank=register_bank,
        )
        call("wdi/write", request)

    async def generic_write_async(
            self,
            register_id: int,
            size: int = 0,
            data: List[int] = [],
            offset: int = 0,
            register_bank: str = "U"
    ) -> None:
        """
        Generic write operation.

        Args:
            register_id: Register address to write to.
            size: Data size to write. Valid values are (0,1,2,4). Determines the data type (Nil, Byte, Word, DWord).
            data: Array of values to write to the register. Empty array is allowed.
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            size=size,
            data=data,
            offset=offset,
            register_bank=register_bank,
        )
        await call_async("wdi/write", request)

    def generic_read_float(
            self,
            register_id: int,
            count: int = 1,
            offset: int = 0,
            register_bank: str = "U"
    ) -> List[float]:
        """
        Generic read operation.

        Args:
            register_id: Register address to read from.
            count: Number of values to read (defaults to 1).
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).

        Returns:
            Array of floats read from the device.
        """
        request = dto.WdiGenericFloatRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            count=count,
            offset=offset,
            register_bank=register_bank,
        )
        response = call(
            "wdi/read_float",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    async def generic_read_float_async(
            self,
            register_id: int,
            count: int = 1,
            offset: int = 0,
            register_bank: str = "U"
    ) -> List[float]:
        """
        Generic read operation.

        Args:
            register_id: Register address to read from.
            count: Number of values to read (defaults to 1).
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).

        Returns:
            Array of floats read from the device.
        """
        request = dto.WdiGenericFloatRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            count=count,
            offset=offset,
            register_bank=register_bank,
        )
        response = await call_async(
            "wdi/read_float",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    def generic_write_float(
            self,
            register_id: int,
            data: List[float] = [],
            offset: int = 0,
            register_bank: str = "U"
    ) -> None:
        """
        Generic write operation.

        Args:
            register_id: Register address to write to.
            data: Array of values to write to the register. Empty array is allowed.
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).
        """
        request = dto.WdiGenericFloatRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            data=data,
            offset=offset,
            register_bank=register_bank,
        )
        call("wdi/write_float", request)

    async def generic_write_float_async(
            self,
            register_id: int,
            data: List[float] = [],
            offset: int = 0,
            register_bank: str = "U"
    ) -> None:
        """
        Generic write operation.

        Args:
            register_id: Register address to write to.
            data: Array of values to write to the register. Empty array is allowed.
            offset: Offset within the register (defaults to 0).
            register_bank: Register bank letter (defaults to U for user bank).
        """
        request = dto.WdiGenericFloatRequest(
            interface_id=self.provider_id,
            register_id=register_id,
            data=data,
            offset=offset,
            register_bank=register_bank,
        )
        await call_async("wdi/write_float", request)

    def enable_laser(
            self
    ) -> None:
        """
        Enables the laser.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=1,
        )
        call("wdi/write", request)

    async def enable_laser_async(
            self
    ) -> None:
        """
        Enables the laser.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=1,
        )
        await call_async("wdi/write", request)

    def disable_laser(
            self
    ) -> None:
        """
        Disables the laser.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=2,
        )
        call("wdi/write", request)

    async def disable_laser_async(
            self
    ) -> None:
        """
        Disables the laser.
        """
        request = dto.WdiGenericRequest(
            interface_id=self.provider_id,
            register_id=2,
        )
        await call_async("wdi/write", request)

    def get_status(
            self
    ) -> WdiAutofocusProviderStatus:
        """
        Gets the status of the autofocus.

        Returns:
            The status of the autofocus.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        response = call(
            "wdi/get_status",
            request,
            dto.WdiGetStatusResponse.from_binary)
        return response.status

    async def get_status_async(
            self
    ) -> WdiAutofocusProviderStatus:
        """
        Gets the status of the autofocus.

        Returns:
            The status of the autofocus.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        response = await call_async(
            "wdi/get_status",
            request,
            dto.WdiGetStatusResponse.from_binary)
        return response.status

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the autofocus connection.

        Returns:
            A string that represents the connection.
        """
        request = dto.InterfaceEmptyRequest(
            interface_id=self.provider_id,
        )
        response = call_sync(
            "wdi/to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def __enter__(self) -> 'WdiAutofocusProvider':
        """ __enter__ """
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        """ __exit__ """
        self.close()

    def __del__(self) -> None:
        WdiAutofocusProvider.__free(self._provider_id)


class AsyncWdiAutofocusProviderOpener:
    '''Async context manager for WdiAutofocusProvider.'''
    def __init__(self, request: dto.OpenInterfaceRequest) -> None:
        self._request = request
        self._resource: Optional[WdiAutofocusProvider] = None

    async def _create_resource(self) -> WdiAutofocusProvider:
        task = asyncio.ensure_future(call_async(
            "wdi/open",
            self._request,
            dto.IntResponse.from_binary))

        try:
            response = await asyncio.shield(task)
        except asyncio.CancelledError:
            async def cancel() -> None:
                try:
                    response = await task
                    await WdiAutofocusProvider(response.value).close_async()
                except MotionLibException:
                    pass

            asyncio.ensure_future(cancel())
            raise

        return WdiAutofocusProvider(response.value)

    def __await__(self) -> Generator[Any, None, 'WdiAutofocusProvider']:
        return self._create_resource().__await__()

    async def __aenter__(self) -> 'WdiAutofocusProvider':
        self._resource = await self._create_resource()
        return self._resource

    async def __aexit__(self, exc_type: Any, exc: Any, trace: Any) -> None:
        if self._resource is not None:
            await self._resource.close_async()
