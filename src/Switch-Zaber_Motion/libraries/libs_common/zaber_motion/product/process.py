# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..ascii.axis import Axis
from ..ascii.axis_settings import AxisSettings
from ..ascii.axis_storage import AxisStorage
from ..ascii.warnings import Warnings
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.ascii.response import Response
from ..dto.ascii.set_state_axis_response import SetStateAxisResponse
from ..dto.firmware_version import FirmwareVersion
from ..dto.measurement import Measurement
from ..dto.product.process_controller_mode import ProcessControllerMode
from ..dto.product.process_controller_source import ProcessControllerSource
from ..units import Units, TimeUnits

if TYPE_CHECKING:
    from .process_controller import ProcessController


class Process:
    """
    Use to drive voltage for a process such as a heater, valve, Peltier device, etc.
    Requires at least Firmware 7.35.
    """

    @property
    def controller(self) -> 'ProcessController':
        """
        Controller for this process.
        """
        return self._controller

    @property
    def process_number(self) -> int:
        """
        The process number identifies the process on the controller.
        """
        return self._process_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this process.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this process.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this process.
        """
        return self._warnings

    def __init__(self, controller: 'ProcessController', process_number: int):
        self._controller: 'ProcessController' = controller
        self._process_number: int = process_number
        self._axis: Axis = Axis(controller.device, process_number)
        self._settings: AxisSettings = AxisSettings(self._axis)
        self._storage: AxisStorage = AxisStorage(self._axis)
        self._warnings: Warnings = Warnings(controller.device, process_number)

    def enable(
            self,
            enabled: bool = True
    ) -> None:
        """
        Sets the enabled state of the driver.

        Args:
            enabled: If true (default) enables drive. If false disables.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=enabled,
        )
        call("process-controller/enable", request)

    async def enable_async(
            self,
            enabled: bool = True
    ) -> None:
        """
        Sets the enabled state of the driver.

        Args:
            enabled: If true (default) enables drive. If false disables.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=enabled,
        )
        await call_async("process-controller/enable", request)

    def on(
            self,
            duration: float = 0,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Turns this process on. In manual mode, this supplies voltage; in controlled mode, it starts the control loop.

        Args:
            duration: How long to leave the process on.
            unit: Units of time.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=True,
            duration=duration,
            unit=unit,
        )
        call("process-controller/on", request)

    async def on_async(
            self,
            duration: float = 0,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Turns this process on. In manual mode, this supplies voltage; in controlled mode, it starts the control loop.

        Args:
            duration: How long to leave the process on.
            unit: Units of time.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=True,
            duration=duration,
            unit=unit,
        )
        await call_async("process-controller/on", request)

    def off(
            self
    ) -> None:
        """
        Turns this process off.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=False,
        )
        call("process-controller/on", request)

    async def off_async(
            self
    ) -> None:
        """
        Turns this process off.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=False,
        )
        await call_async("process-controller/on", request)

    def set_mode(
            self,
            mode: ProcessControllerMode
    ) -> None:
        """
        Sets the control mode of this process.

        Args:
            mode: Mode to set this process to.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            setting="process.control.mode",
            value=mode.value,
        )
        call("device/set_setting", request)

    async def set_mode_async(
            self,
            mode: ProcessControllerMode
    ) -> None:
        """
        Sets the control mode of this process.

        Args:
            mode: Mode to set this process to.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            setting="process.control.mode",
            value=mode.value,
        )
        await call_async("device/set_setting", request)

    def get_mode(
            self
    ) -> ProcessControllerMode:
        """
        Gets the control mode of this process.

        Returns:
            Control mode.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            setting="process.control.mode",
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return ProcessControllerMode(response.value)

    async def get_mode_async(
            self
    ) -> ProcessControllerMode:
        """
        Gets the control mode of this process.

        Returns:
            Control mode.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            setting="process.control.mode",
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return ProcessControllerMode(response.value)

    def get_source(
            self
    ) -> ProcessControllerSource:
        """
        Gets the source used to control this process.

        Returns:
            The source providing feedback for this process.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = call(
            "process_controller/get_source",
            request,
            ProcessControllerSource.from_binary)
        return response

    async def get_source_async(
            self
    ) -> ProcessControllerSource:
        """
        Gets the source used to control this process.

        Returns:
            The source providing feedback for this process.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = await call_async(
            "process_controller/get_source",
            request,
            ProcessControllerSource.from_binary)
        return response

    def set_source(
            self,
            source: ProcessControllerSource
    ) -> None:
        """
        Sets the source used to control this process.

        Args:
            source: Sets the source that should provide feedback for this process.
        """
        request = dto.SetProcessControllerSource(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            source=source,
        )
        call("process_controller/set_source", request)

    async def set_source_async(
            self,
            source: ProcessControllerSource
    ) -> None:
        """
        Sets the source used to control this process.

        Args:
            source: Sets the source that should provide feedback for this process.
        """
        request = dto.SetProcessControllerSource(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            source=source,
        )
        await call_async("process_controller/set_source", request)

    def get_input(
            self
    ) -> Measurement:
        """
        Gets the current value of the source used to control this process.

        Returns:
            The current value of this process's controlling source.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = call(
            "process_controller/get_input",
            request,
            Measurement.from_binary)
        return response

    async def get_input_async(
            self
    ) -> Measurement:
        """
        Gets the current value of the source used to control this process.

        Returns:
            The current value of this process's controlling source.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = await call_async(
            "process_controller/get_input",
            request,
            Measurement.from_binary)
        return response

    def bridge(
            self
    ) -> None:
        """
        Creates an H-bridge between this process and its neighbor. This method is only callable on axis 1 and 3.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=True,
        )
        call("process_controller/bridge", request)

    async def bridge_async(
            self
    ) -> None:
        """
        Creates an H-bridge between this process and its neighbor. This method is only callable on axis 1 and 3.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=True,
        )
        await call_async("process_controller/bridge", request)

    def unbridge(
            self
    ) -> None:
        """
        Breaks the H-bridge between this process and its neighbor, allowing them to be independently controlled.
        This method is only callable on axis 1 and 3.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=False,
        )
        call("process_controller/bridge", request)

    async def unbridge_async(
            self
    ) -> None:
        """
        Breaks the H-bridge between this process and its neighbor, allowing them to be independently controlled.
        This method is only callable on axis 1 and 3.
        """
        request = dto.ProcessOn(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            on=False,
        )
        await call_async("process_controller/bridge", request)

    def is_bridge(
            self
    ) -> bool:
        """
        Detects if the given process is in bridging mode.

        Returns:
            Whether this process is bridged with its neighbor.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = call(
            "process_controller/is_bridge",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_bridge_async(
            self
    ) -> bool:
        """
        Detects if the given process is in bridging mode.

        Returns:
            Whether this process is bridged with its neighbor.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
        )
        response = await call_async(
            "process_controller/is_bridge",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this process' underlying axis.
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
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Sends a generic ASCII command to this process' underlying axis.
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
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Sends a generic ASCII command to this process and expect multiple responses.
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
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Sends a generic ASCII command to this process and expect multiple responses.
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
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Sends a generic ASCII command to this process without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            command=command,
        )
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this process without expecting a response and without adding a message ID
        For more information refer to: ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = dto.GenericCommandRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            command=command,
        )
        await call_async("interface/generic_command_no_response", request)

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current process state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the process.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Returns a serialization of the current process state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the process.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Applies a saved state to this process.

        Args:
            state: The state object to apply to this process.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Applies a saved state to this process.

        Args:
            state: The state object to apply to this process.

        Returns:
            Reports of any issues that were handled, but caused the state to not be exactly restored.
        """
        request = dto.SetStateRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Checks if a state can be applied to this process.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this process.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Checks if a state can be applied to this process.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.
            firmware_version: The firmware version of the device to apply the state to.
                Use this to ensure the state will still be compatible after an update.

        Returns:
            An explanation of why this state cannot be set to this process.
        """
        request = dto.CanSetStateRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
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
        Returns a string that represents the process.

        Returns:
            A string that represents the process.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.controller.device.connection.interface_id,
            device=self.controller.device.device_address,
            axis=self.process_number,
            type_override="Process",
        )
        response = call_sync(
            "device/axis_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
