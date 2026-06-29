# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.can_set_state_device_response import CanSetStateDeviceResponse
from ..dto.ascii.device_identity import DeviceIdentity
from ..dto.ascii.response import Response
from ..dto.ascii.set_state_device_response import SetStateDeviceResponse
from ..dto.firmware_version import FirmwareVersion
from ..dto.measurement import Measurement
from ..dto.unit_conversion_descriptor import UnitConversionDescriptor
from .all_axes import AllAxes
from .axis import Axis
from .device_io import DeviceIO
from .device_settings import DeviceSettings
from .device_storage import DeviceStorage
from .lockstep import Lockstep
from .oscilloscope import Oscilloscope
from .pvt import Pvt
from .streams import Streams
from .triggers import Triggers
from .warnings import Warnings

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
    def storage(self) -> DeviceStorage:
        """
        Key-value storage of this device.
        """
        return self._storage

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
    def oscilloscope(self) -> Oscilloscope:
        """
        Oscilloscope recording helper for this device.
        Requires at least Firmware 7.00.
        """
        return self._oscilloscope

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

    @property
    def is_integrated(self) -> bool:
        """
        The device is an integrated product.
        """
        return self.identity.is_integrated

    @property
    def label(self) -> str:
        """
        User-assigned label of the device.
        """
        return self.__retrieve_label()

    @property
    def triggers(self) -> Triggers:
        """
        Triggers for this device.
        Requires at least Firmware 7.06.
        """
        return self._triggers

    @property
    def streams(self) -> Streams:
        """
        Gets an object that provides access to Streams on this device.
        Requires at least Firmware 7.05.
        """
        return self._streams

    @property
    def pvt(self) -> Pvt:
        """
        Gets an object that provides access to PVT functions of this device.
        Note that as of ZML v5.0.0, this returns a Pvt object and NOT a PvtSequence object.
        The PvtSequence can now be obtained from the Pvt object.
        Requires at least Firmware 7.33.
        """
        return self._pvt

    def __init__(self, connection: 'Connection', device_address: int):
        self._connection: 'Connection' = connection
        self._device_address: int = device_address
        self._settings: DeviceSettings = DeviceSettings(self)
        self._storage: DeviceStorage = DeviceStorage(self)
        self._io: DeviceIO = DeviceIO(self)
        self._all_axes: AllAxes = AllAxes(self)
        self._warnings: Warnings = Warnings(self, 0)
        self._oscilloscope: Oscilloscope = Oscilloscope(self)
        self._triggers: Triggers = Triggers(self)
        self._streams: Streams = Streams(self)
        self._pvt: Pvt = Pvt(self)

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
            "device/identify",
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
            "device/identify",
            request,
            DeviceIdentity.from_binary)
        return response

    def generic_command(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
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
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            axis=axis,
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
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
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
            axis: int = 0,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            axis=axis,
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
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
                Specifying -1 omits the number completely.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            axis=axis,
        )
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            axis: Optional axis number to send the command to.
                Specifying -1 omits the number completely.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            command=command,
            axis=axis,
        )
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
        Requires at least Firmware 6.15 or 7.11.

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
        Unit conversion is not supported for commands where axes can be remapped, such as stream and PVT commands.
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of a command to prepare. Parameters are denoted by question marks.
            parameters: Variable number of command parameters.

        Returns:
            Command with converted parameters.
        """
        request = dto.PrepareCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
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
        Checks whether the device supports the given command.

        Args:
            command: Command to check.
                Parameters can be denoted by question marks, valid values, or the parameter name.
            allow_partial: If true, also matches commands that are a prefix of a supported command.

        Returns:
            True if the command is supported.
        """
        request = dto.DeviceHasCommandRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
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
            interface_id=self.connection.interface_id,
            device=self.device_address,
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
        Sets the user-assigned device label.
        The label is stored on the controller and recognized by other software.

        Args:
            label: Label to set.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            value=label,
        )
        call("device/set_label", request)

    async def set_label_async(
            self,
            label: str
    ) -> None:
        """
        Sets the user-assigned device label.
        The label is stored on the controller and recognized by other software.

        Args:
            label: Label to set.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            value=label,
        )
        await call_async("device/set_label", request)

    def __retrieve_label(
            self
    ) -> str:
        """
        Gets the device name.

        Returns:
            The label.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
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
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = call_sync(
            "device/device_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current device state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the device.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
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
        Returns a serialization of the current device state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the device.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
        )
        response = await call_async(
            "device/get_state",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def set_state(
            self,
            state: str,
            device_only: bool = False
    ) -> SetStateDeviceResponse:
        """
        Applies a saved state to this device.

        Args:
            state: The state object to apply to this device.
            device_only: If true, only device scope settings and features will be set.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            state=state,
            device_only=device_only,
        )
        response = call(
            "device/set_device_state",
            request,
            SetStateDeviceResponse.from_binary)
        return response

    async def set_state_async(
            self,
            state: str,
            device_only: bool = False
    ) -> SetStateDeviceResponse:
        """
        Applies a saved state to this device.

        Args:
            state: The state object to apply to this device.
            device_only: If true, only device scope settings and features will be set.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            state=state,
            device_only=device_only,
        )
        response = await call_async(
            "device/set_device_state",
            request,
            SetStateDeviceResponse.from_binary)
        return response

    def can_set_state(
            self,
            state: str,
            firmware_version: Optional[FirmwareVersion] = None
    ) -> CanSetStateDeviceResponse:
        """
        Checks if a state can be applied to this device.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An object listing errors that come up when trying to set the state.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            state=state,
            firmware_version=firmware_version,
        )
        response = call(
            "device/can_set_state",
            request,
            CanSetStateDeviceResponse.from_binary)
        return response

    async def can_set_state_async(
            self,
            state: str,
            firmware_version: Optional[FirmwareVersion] = None
    ) -> CanSetStateDeviceResponse:
        """
        Checks if a state can be applied to this device.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An object listing errors that come up when trying to set the state.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            state=state,
            firmware_version=firmware_version,
        )
        response = await call_async(
            "device/can_set_state",
            request,
            CanSetStateDeviceResponse.from_binary)
        return response

    def wait_to_respond(
            self,
            timeout: float
    ) -> None:
        """
        Waits for the device to start responding to messages.
        Useful to call after resetting the device.
        Throws RequestTimeoutException upon timeout.

        Args:
            timeout: For how long to wait in milliseconds for the device to start responding.
        """
        request = dto.WaitToRespondRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            timeout=timeout,
        )
        call("device/wait_to_respond", request)

    async def wait_to_respond_async(
            self,
            timeout: float
    ) -> None:
        """
        Waits for the device to start responding to messages.
        Useful to call after resetting the device.
        Throws RequestTimeoutException upon timeout.

        Args:
            timeout: For how long to wait in milliseconds for the device to start responding.
        """
        request = dto.WaitToRespondRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            timeout=timeout,
        )
        await call_async("device/wait_to_respond", request)

    def renumber(
            self,
            address: int
    ) -> 'Device':
        """
        Changes the address of this device.
        After the address is successfully changed, the existing device class instance no longer represents the device.
        Instead, use the new device instance returned by this method.

        Args:
            address: The new address to assign to the device.

        Returns:
            New device instance with the new address.
        """
        if address < 1 or address > 99:
            raise ValueError('Invalid value; device addresses are numbered from 1 to 99.')

        request = dto.RenumberRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            address=address,
        )
        response = call(
            "device/renumber",
            request,
            dto.IntResponse.from_binary)
        return Device(self.connection, response.value)

    async def renumber_async(
            self,
            address: int
    ) -> 'Device':
        """
        Changes the address of this device.
        After the address is successfully changed, the existing device class instance no longer represents the device.
        Instead, use the new device instance returned by this method.

        Args:
            address: The new address to assign to the device.

        Returns:
            New device instance with the new address.
        """
        if address < 1 or address > 99:
            raise ValueError('Invalid value; device addresses are numbered from 1 to 99.')

        request = dto.RenumberRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            address=address,
        )
        response = await call_async(
            "device/renumber",
            request,
            dto.IntResponse.from_binary)
        return Device(self.connection, response.value)

    def restore(
            self,
            hard: bool = False
    ) -> None:
        """
        Restores most of the settings to their default values.
        Deletes all triggers, stream and PVT buffers, servo tunings.
        Deletes all zaber storage keys.
        Disables locksteps, unparks axes.
        Preserves storage, communication settings, peripherals (unless hard is specified).
        The device needs to be identified again after the restore.

        Args:
            hard: If true, completely erases device's memory. The device also resets.
        """
        request = dto.DeviceRestoreRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            hard=hard,
        )
        call("device/restore", request)

    async def restore_async(
            self,
            hard: bool = False
    ) -> None:
        """
        Restores most of the settings to their default values.
        Deletes all triggers, stream and PVT buffers, servo tunings.
        Deletes all zaber storage keys.
        Disables locksteps, unparks axes.
        Preserves storage, communication settings, peripherals (unless hard is specified).
        The device needs to be identified again after the restore.

        Args:
            hard: If true, completely erases device's memory. The device also resets.
        """
        request = dto.DeviceRestoreRequest(
            interface_id=self.connection.interface_id,
            device=self.device_address,
            hard=hard,
        )
        await call_async("device/restore", request)

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
            "device/get_identity",
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
            "device/get_is_identified",
            request,
            dto.BoolResponse.from_binary)
        return response.value
