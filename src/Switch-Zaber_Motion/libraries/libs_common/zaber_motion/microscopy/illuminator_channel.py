# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..ascii import Axis, AxisSettings, AxisStorage, Warnings
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.response import Response
from ..dto.ascii.set_state_axis_response import SetStateAxisResponse
from ..dto.firmware_version import FirmwareVersion
from ..dto.measurement import Measurement

if TYPE_CHECKING:
    from .illuminator import Illuminator


class IlluminatorChannel:
    """
    Use to control a channel (LED lamp) on an illuminator.
    Requires at least Firmware 7.09.
    """

    @property
    def illuminator(self) -> 'Illuminator':
        """
        Illuminator of this channel.
        """
        return self._illuminator

    @property
    def channel_number(self) -> int:
        """
        The channel number identifies the channel on the illuminator.
        """
        return self._channel_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this channel.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this channel.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this channel.
        """
        return self._warnings

    def __init__(self, illuminator: 'Illuminator', channel_number: int):
        self._illuminator: 'Illuminator' = illuminator
        self._channel_number: int = channel_number
        self._axis: Axis = Axis(illuminator.device, channel_number)
        self._settings: AxisSettings = AxisSettings(self._axis)
        self._storage: AxisStorage = AxisStorage(self._axis)
        self._warnings: Warnings = Warnings(illuminator.device, channel_number)

    def on(
            self,
            duration: Optional[Measurement] = None
    ) -> None:
        """
        Turns this channel on.

        Args:
            duration: Duration for which to turn the channel on.
                If not specified, the channel remains on until turned off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=True,
            duration=duration,
        )
        call("illuminator/on", request)

    async def on_async(
            self,
            duration: Optional[Measurement] = None
    ) -> None:
        """
        Turns this channel on.

        Args:
            duration: Duration for which to turn the channel on.
                If not specified, the channel remains on until turned off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=True,
            duration=duration,
        )
        await call_async("illuminator/on", request)

    def off(
            self
    ) -> None:
        """
        Turns this channel off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=False,
        )
        call("illuminator/on", request)

    async def off_async(
            self
    ) -> None:
        """
        Turns this channel off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=False,
        )
        await call_async("illuminator/on", request)

    def set_on(
            self,
            on: bool
    ) -> None:
        """
        Turns this channel on or off.

        Args:
            on: True to turn channel on, false to turn it off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=on,
        )
        call("illuminator/on", request)

    async def set_on_async(
            self,
            on: bool
    ) -> None:
        """
        Turns this channel on or off.

        Args:
            on: True to turn channel on, false to turn it off.
        """
        request = dto.ChannelOn(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            on=on,
        )
        await call_async("illuminator/on", request)

    def is_on(
            self
    ) -> bool:
        """
        Checks if this channel is on.

        Returns:
            True if channel is on, false otherwise.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
        )
        response = call(
            "illuminator/is_on",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_on_async(
            self
    ) -> bool:
        """
        Checks if this channel is on.

        Returns:
            True if channel is on, false otherwise.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
        )
        response = await call_async(
            "illuminator/is_on",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def set_intensity(
            self,
            intensity: float
    ) -> None:
        """
        Sets channel intensity as a fraction of the maximum flux.

        Args:
            intensity: Fraction of intensity to set (between 0 and 1).
        """
        request = dto.ChannelSetIntensity(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            intensity=intensity,
        )
        call("illuminator/set_intensity", request)

    async def set_intensity_async(
            self,
            intensity: float
    ) -> None:
        """
        Sets channel intensity as a fraction of the maximum flux.

        Args:
            intensity: Fraction of intensity to set (between 0 and 1).
        """
        request = dto.ChannelSetIntensity(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            intensity=intensity,
        )
        await call_async("illuminator/set_intensity", request)

    def get_intensity(
            self
    ) -> float:
        """
        Gets the current intensity of this channel.

        Returns:
            Current intensity as fraction of maximum flux.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
        )
        response = call(
            "illuminator/get_intensity",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_intensity_async(
            self
    ) -> float:
        """
        Gets the current intensity of this channel.

        Returns:
            Current intensity as fraction of maximum flux.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
        )
        response = await call_async(
            "illuminator/get_intensity",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this channel.
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
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Sends a generic ASCII command to this channel.
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
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Sends a generic ASCII command to this channel and expects multiple responses.
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
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Sends a generic ASCII command to this channel and expects multiple responses.
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
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Sends a generic ASCII command to this channel without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            command=command,
        )
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this channel without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            command=command,
        )
        await call_async("interface/generic_command_no_response", request)

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current channel state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the channel.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Returns a serialization of the current channel state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the channel.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Applies a saved state to this channel.

        Args:
            state: The state object to apply to this channel.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Applies a saved state to this channel.

        Args:
            state: The state object to apply to this channel.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Checks if a state can be applied to this channel.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this channel.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
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
        Checks if a state can be applied to this channel.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this channel.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            state=state,
            firmware_version=firmware_version,
        )
        response = await call_async(
            "device/can_set_axis_state",
            request,
            dto.CanSetStateAxisResponse.from_binary)
        return response.error

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the channel.

        Returns:
            A string that represents the channel.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.illuminator.device.connection.interface_id,
            device=self.illuminator.device.device_address,
            axis=self.channel_number,
            type_override="Channel",
        )
        response = call_sync(
            "device/axis_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
