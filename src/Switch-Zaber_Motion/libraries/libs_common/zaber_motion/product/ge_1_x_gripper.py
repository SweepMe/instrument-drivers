# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Any, Optional, Generator
import asyncio
from ..call import call, call_sync, call_async
from ..exceptions.motion_lib_exception import MotionLibException
from ..dto import requests as dto
from ..dto.product import Ge1xGripperState, Ge1xGripperError, Ge1xGripperDirection


class Ge1xGripper:
    """
    Class representing a gripper in the GE1x series.
    """

    DEFAULT_DEVICE_ADDRESS = 1
    """
    The default device address for a gripper in the GE1x series.
    """

    @property
    def connection_id(self) -> int:
        """
        The identifier for the connection.
        """
        return self._connection_id

    def __init__(self, connection_id: int):
        self._connection_id: int = connection_id

    @staticmethod
    def open_connection(
            port_name: str,
            device_address: int = DEFAULT_DEVICE_ADDRESS,
            timeout: int = 500
    ) -> 'Ge1xGripper':
        """
        Opens a serial connection to a gripper.

        Args:
            port_name: The name of the serial port to connect to.
            device_address: The address of the gripper to connect to.
            timeout: The timeout in milliseconds for any request sent using this connection.

        Returns:
            A Ge1xGripper instance representing the connection to the gripper.
        """
        request = dto.Ge1xGripperOpenConnectionRequest(
            port_name=port_name,
            device_address=device_address,
            timeout=timeout,
        )
        response = call(
            "ge1x_gripper/open_connection",
            request,
            dto.IntResponse.from_binary)
        return Ge1xGripper(response.value)

    @staticmethod
    def open_connection_async(
            port_name: str,
            device_address: int = DEFAULT_DEVICE_ADDRESS,
            timeout: int = 500
    ) -> 'AsyncGe1xGripperOpener':
        """
        Opens a serial connection to a gripper.

        Args:
            port_name: The name of the serial port to connect to.
            device_address: The address of the gripper to connect to.
            timeout: The timeout in milliseconds for any request sent using this connection.

        Returns:
            A Ge1xGripper instance representing the connection to the gripper.
        """
        request = dto.Ge1xGripperOpenConnectionRequest(
            port_name=port_name,
            device_address=device_address,
            timeout=timeout,
        )
        return AsyncGe1xGripperOpener(request)

    def close(
            self
    ) -> None:
        """
        Closes the connection to the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/close_connection", request)

    async def close_async(
            self
    ) -> None:
        """
        Closes the connection to the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/close_connection", request)

    def read_register(
            self,
            register_address: int
    ) -> int:
        """
        Reads a single register value from the gripper.

        Args:
            register_address: The address of the register to read.

        Returns:
            The data at the specified register address.
        """
        request = dto.Ge1xGripperReadRegisterRequest(
            connection_id=self.connection_id,
            register_address=register_address,
        )
        response = call(
            "ge1x_gripper/read_register",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def read_register_async(
            self,
            register_address: int
    ) -> int:
        """
        Reads a single register value from the gripper.

        Args:
            register_address: The address of the register to read.

        Returns:
            The data at the specified register address.
        """
        request = dto.Ge1xGripperReadRegisterRequest(
            connection_id=self.connection_id,
            register_address=register_address,
        )
        response = await call_async(
            "ge1x_gripper/read_register",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def write_register(
            self,
            register_address: int,
            data: int
    ) -> None:
        """
        Writes a single register value to the gripper.

        Args:
            register_address: The address of the register to write.
            data: The data to write to the specified register address.
        """
        request = dto.Ge1xGripperWriteRegisterRequest(
            connection_id=self.connection_id,
            register_address=register_address,
            data=data,
        )
        call("ge1x_gripper/write_register", request)

    async def write_register_async(
            self,
            register_address: int,
            data: int
    ) -> None:
        """
        Writes a single register value to the gripper.

        Args:
            register_address: The address of the register to write.
            data: The data to write to the specified register address.
        """
        request = dto.Ge1xGripperWriteRegisterRequest(
            connection_id=self.connection_id,
            register_address=register_address,
            data=data,
        )
        await call_async("ge1x_gripper/write_register", request)

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes gripper by moving it to its homing position.

        Args:
            wait_until_idle: Wait until homing has completed before returning.
        """
        request = dto.Ge1xGripperWaitUntilIdleRequest(
            connection_id=self.connection_id,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes gripper by moving it to its homing position.

        Args:
            wait_until_idle: Wait until homing has completed before returning.
        """
        request = dto.Ge1xGripperWaitUntilIdleRequest(
            connection_id=self.connection_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/home", request)

    def wait_until_idle(
            self
    ) -> None:
        """
        Waits until the gripper has stopped moving.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/wait_until_idle", request)

    async def wait_until_idle_async(
            self
    ) -> None:
        """
        Waits until the gripper has stopped moving.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/wait_until_idle", request)

    def move(
            self,
            position: float,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to a specified position.

        Args:
            position: The target position for the gripper as a percentage, where 0 is closed and 100 is open.
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=position,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/move", request)

    async def move_async(
            self,
            position: float,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to a specified position.

        Args:
            position: The target position for the gripper as a percentage, where 0 is closed and 100 is open.
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=position,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/move", request)

    def move_open(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to the open position.

        Args:
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=100,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/move", request)

    async def move_open_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to the open position.

        Args:
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=100,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/move", request)

    def move_close(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to the closed position.

        Args:
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=0,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/move", request)

    async def move_close_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Moves the gripper to the closed position.

        Args:
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperMoveRequest(
            connection_id=self.connection_id,
            position=0,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/move", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the gripper from moving.

        Args:
            wait_until_idle: Wait until the gripper has stopped before returning.
        """
        request = dto.Ge1xGripperWaitUntilIdleRequest(
            connection_id=self.connection_id,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops the gripper from moving.

        Args:
            wait_until_idle: Wait until the gripper has stopped before returning.
        """
        request = dto.Ge1xGripperWaitUntilIdleRequest(
            connection_id=self.connection_id,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/stop", request)

    def set_force(
            self,
            force: int
    ) -> None:
        """
        Sets the gripping force of the gripper.

        Args:
            force: The gripping force as a percentage from 20 to 100.
        """
        request = dto.Ge1xGripperSetForceRequest(
            connection_id=self.connection_id,
            force=force,
        )
        call("ge1x_gripper/set_force", request)

    async def set_force_async(
            self,
            force: int
    ) -> None:
        """
        Sets the gripping force of the gripper.

        Args:
            force: The gripping force as a percentage from 20 to 100.
        """
        request = dto.Ge1xGripperSetForceRequest(
            connection_id=self.connection_id,
            force=force,
        )
        await call_async("ge1x_gripper/set_force", request)

    def set_speed(
            self,
            speed: int
    ) -> None:
        """
        Sets the maximum speed of the gripper.

        Args:
            speed: The maximum speed as a percentage from 1 to 100.
        """
        request = dto.Ge1xGripperSetSpeedRequest(
            connection_id=self.connection_id,
            speed=speed,
        )
        call("ge1x_gripper/set_speed", request)

    async def set_speed_async(
            self,
            speed: int
    ) -> None:
        """
        Sets the maximum speed of the gripper.

        Args:
            speed: The maximum speed as a percentage from 1 to 100.
        """
        request = dto.Ge1xGripperSetSpeedRequest(
            connection_id=self.connection_id,
            speed=speed,
        )
        await call_async("ge1x_gripper/set_speed", request)

    def driver_enable(
            self
    ) -> None:
        """
        Enables the gripper driver.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/driver_enable", request)

    async def driver_enable_async(
            self
    ) -> None:
        """
        Enables the gripper driver.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/driver_enable", request)

    def driver_disable(
            self
    ) -> None:
        """
        Disables the gripper driver.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/driver_disable", request)

    async def driver_disable_async(
            self
    ) -> None:
        """
        Disables the gripper driver.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/driver_disable", request)

    def calibrate(
            self
    ) -> None:
        """
        Performs a calibration of the travel range by moving to the fully open and fully closed positions.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/calibrate", request)

    async def calibrate_async(
            self
    ) -> None:
        """
        Performs a calibration of the travel range by moving to the fully open and fully closed positions.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/calibrate", request)

    def get_state(
            self
    ) -> Ge1xGripperState:
        """
        Gets the current state of the gripper.

        Returns:
            The current state of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/get_state",
            request,
            dto.Ge1xGripperGetStateResponse.from_binary)
        return response.value

    async def get_state_async(
            self
    ) -> Ge1xGripperState:
        """
        Gets the current state of the gripper.

        Returns:
            The current state of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/get_state",
            request,
            dto.Ge1xGripperGetStateResponse.from_binary)
        return response.value

    def get_error(
            self
    ) -> Ge1xGripperError:
        """
        Gets the current error of the gripper.

        Returns:
            The current error of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/get_error",
            request,
            dto.Ge1xGripperGetErrorResponse.from_binary)
        return response.value

    async def get_error_async(
            self
    ) -> Ge1xGripperError:
        """
        Gets the current error of the gripper.

        Returns:
            The current error of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/get_error",
            request,
            dto.Ge1xGripperGetErrorResponse.from_binary)
        return response.value

    def clear_error(
            self
    ) -> None:
        """
        Clears the current error of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        call("ge1x_gripper/clear_error", request)

    async def clear_error_async(
            self
    ) -> None:
        """
        Clears the current error of the gripper.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        await call_async("ge1x_gripper/clear_error", request)

    def is_homed(
            self
    ) -> bool:
        """
        Checks if the gripper has been homed.

        Returns:
            True if the gripper is homed, false otherwise.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_homed_async(
            self
    ) -> bool:
        """
        Checks if the gripper has been homed.

        Returns:
            True if the gripper is homed, false otherwise.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/is_homed",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_position(
            self
    ) -> float:
        """
        Gets the current position of the gripper.

        Returns:
            The current position of the gripper as a percentage, where 0 is closed and 100 is open.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/get_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_position_async(
            self
    ) -> float:
        """
        Gets the current position of the gripper.

        Returns:
            The current position of the gripper as a percentage, where 0 is closed and 100 is open.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/get_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_current(
            self
    ) -> int:
        """
        Gets the current current of the gripper.

        Returns:
            The current current of the gripper in milliamps.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/get_current",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_current_async(
            self
    ) -> int:
        """
        Gets the current current of the gripper.

        Returns:
            The current current of the gripper in milliamps.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/get_current",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def set_home_direction(
            self,
            direction: Ge1xGripperDirection,
            save_to_flash: bool = True
    ) -> None:
        """
        Sets the home direction for the gripper.

        Args:
            direction: The home direction to set.
            save_to_flash: Save the home direction setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetHomeDirectionRequest(
            connection_id=self.connection_id,
            direction=direction,
            save_to_flash=save_to_flash,
        )
        call("ge1x_gripper/set_home_direction", request)

    async def set_home_direction_async(
            self,
            direction: Ge1xGripperDirection,
            save_to_flash: bool = True
    ) -> None:
        """
        Sets the home direction for the gripper.

        Args:
            direction: The home direction to set.
            save_to_flash: Save the home direction setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetHomeDirectionRequest(
            connection_id=self.connection_id,
            direction=direction,
            save_to_flash=save_to_flash,
        )
        await call_async("ge1x_gripper/set_home_direction", request)

    def set_auto_home(
            self,
            enabled: bool,
            save_to_flash: bool = True
    ) -> None:
        """
        Enables or disables automatic homing on power up.

        Args:
            enabled: True to enable automatic homing on power up, false to disable.
            save_to_flash: Save the auto home setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetAutoHomeRequest(
            connection_id=self.connection_id,
            enabled=enabled,
            save_to_flash=save_to_flash,
        )
        call("ge1x_gripper/set_auto_home", request)

    async def set_auto_home_async(
            self,
            enabled: bool,
            save_to_flash: bool = True
    ) -> None:
        """
        Enables or disables automatic homing on power up.

        Args:
            enabled: True to enable automatic homing on power up, false to disable.
            save_to_flash: Save the auto home setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetAutoHomeRequest(
            connection_id=self.connection_id,
            enabled=enabled,
            save_to_flash=save_to_flash,
        )
        await call_async("ge1x_gripper/set_auto_home", request)

    def set_io_enabled(
            self,
            enabled: bool,
            save_to_flash: bool = True
    ) -> None:
        """
        Enables or disables IO control for the gripper.
        When enabled, the gripper will not move to a preset position until the IO input changes.

        Args:
            enabled: True to enable IO control, false to disable.
            save_to_flash: Save the IO enabled setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetIoEnabledRequest(
            connection_id=self.connection_id,
            enabled=enabled,
            save_to_flash=save_to_flash,
        )
        call("ge1x_gripper/set_io_enabled", request)

    async def set_io_enabled_async(
            self,
            enabled: bool,
            save_to_flash: bool = True
    ) -> None:
        """
        Enables or disables IO control for the gripper.
        When enabled, the gripper will not move to a preset position until the IO input changes.

        Args:
            enabled: True to enable IO control, false to disable.
            save_to_flash: Save the IO enabled setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetIoEnabledRequest(
            connection_id=self.connection_id,
            enabled=enabled,
            save_to_flash=save_to_flash,
        )
        await call_async("ge1x_gripper/set_io_enabled", request)

    def set_io_input_filter(
            self,
            duration: int,
            save_to_flash: bool = True
    ) -> None:
        """
        Sets the debounce filter time for the gripper IO input to suppress noise.

        Args:
            duration: The IO input filter time in milliseconds.
            save_to_flash: Save the IO input filter setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetIoInputFilterRequest(
            connection_id=self.connection_id,
            duration=duration,
            save_to_flash=save_to_flash,
        )
        call("ge1x_gripper/set_io_input_filter", request)

    async def set_io_input_filter_async(
            self,
            duration: int,
            save_to_flash: bool = True
    ) -> None:
        """
        Sets the debounce filter time for the gripper IO input to suppress noise.

        Args:
            duration: The IO input filter time in milliseconds.
            save_to_flash: Save the IO input filter setting to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetIoInputFilterRequest(
            connection_id=self.connection_id,
            duration=duration,
            save_to_flash=save_to_flash,
        )
        await call_async("ge1x_gripper/set_io_input_filter", request)

    def set_preset(
            self,
            preset_number: int,
            position: float,
            force: int = 100,
            speed: int = 100,
            save_to_flash: bool = True
    ) -> None:
        """
        Saves a position, force, and speed as a preset that can be enabled using I/O or the activatePreset() method.
        Note that presets are only activated by I/O when the I/O input changes to that preset number.

        Args:
            preset_number: The preset number to save the preset to, from 1 to 4.
            position: The target position for the preset as a percentage, where 0 is closed and 100 is open.
            force: The gripping force for the preset as a percentage from 20 to 100.
            speed: The maximum speed for the preset as a percentage from 1 to 100.
            save_to_flash: Save the preset to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetPresetRequest(
            connection_id=self.connection_id,
            preset_number=preset_number,
            position=position,
            force=force,
            speed=speed,
            save_to_flash=save_to_flash,
        )
        call("ge1x_gripper/set_preset", request)

    async def set_preset_async(
            self,
            preset_number: int,
            position: float,
            force: int = 100,
            speed: int = 100,
            save_to_flash: bool = True
    ) -> None:
        """
        Saves a position, force, and speed as a preset that can be enabled using I/O or the activatePreset() method.
        Note that presets are only activated by I/O when the I/O input changes to that preset number.

        Args:
            preset_number: The preset number to save the preset to, from 1 to 4.
            position: The target position for the preset as a percentage, where 0 is closed and 100 is open.
            force: The gripping force for the preset as a percentage from 20 to 100.
            speed: The maximum speed for the preset as a percentage from 1 to 100.
            save_to_flash: Save the preset to flash memory so it is retained on power cycle.
        """
        request = dto.Ge1xGripperSetPresetRequest(
            connection_id=self.connection_id,
            preset_number=preset_number,
            position=position,
            force=force,
            speed=speed,
            save_to_flash=save_to_flash,
        )
        await call_async("ge1x_gripper/set_preset", request)

    def activate_preset(
            self,
            preset_number: int,
            wait_until_idle: bool = True
    ) -> None:
        """
        Activates a preset, causing the gripper to move to the preset position using the preset force and speed.

        Args:
            preset_number: The preset number to activate, from 1 to 4.
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperActivatePresetRequest(
            connection_id=self.connection_id,
            preset_number=preset_number,
            wait_until_idle=wait_until_idle,
        )
        call("ge1x_gripper/activate_preset", request)

    async def activate_preset_async(
            self,
            preset_number: int,
            wait_until_idle: bool = True
    ) -> None:
        """
        Activates a preset, causing the gripper to move to the preset position using the preset force and speed.

        Args:
            preset_number: The preset number to activate, from 1 to 4.
            wait_until_idle: Wait until the move has completed before returning.
        """
        request = dto.Ge1xGripperActivatePresetRequest(
            connection_id=self.connection_id,
            preset_number=preset_number,
            wait_until_idle=wait_until_idle,
        )
        await call_async("ge1x_gripper/activate_preset", request)

    def get_io_input_preset_number(
            self
    ) -> int:
        """
        Gets the preset number currently activated by the gripper IO input.

        Returns:
            The current preset number activated by the gripper IO input.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = call(
            "ge1x_gripper/get_io_input_preset_number",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_io_input_preset_number_async(
            self
    ) -> int:
        """
        Gets the preset number currently activated by the gripper IO input.

        Returns:
            The current preset number activated by the gripper IO input.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=self.connection_id,
        )
        response = await call_async(
            "ge1x_gripper/get_io_input_preset_number",
            request,
            dto.IntResponse.from_binary)
        return response.value

    @staticmethod
    def __free(
            connection_id: int
    ) -> None:
        """
        Frees the connection instance.

        Args:
            connection_id: Connection ID to be freed.
        """
        request = dto.Ge1xGripperEmptyRequest(
            connection_id=connection_id,
        )
        call_sync("ge1x_gripper/free_connection", request)

    def __enter__(self) -> 'Ge1xGripper':
        """ __enter__ """
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        """ __exit__ """
        self.close()

    def __del__(self) -> None:
        Ge1xGripper.__free(self._connection_id)


class AsyncGe1xGripperOpener:
    '''Async context manager for Ge1xGripper.'''
    def __init__(self, request: dto.Ge1xGripperOpenConnectionRequest) -> None:
        self._request = request
        self._resource: Optional[Ge1xGripper] = None

    async def _create_resource(self) -> Ge1xGripper:
        task = asyncio.ensure_future(call_async(
            "ge1x_gripper/open_connection",
            self._request,
            dto.IntResponse.from_binary))

        try:
            response = await asyncio.shield(task)
        except asyncio.CancelledError:
            async def cancel() -> None:
                try:
                    response = await task
                    await Ge1xGripper(response.value).close_async()
                except MotionLibException:
                    pass

            asyncio.ensure_future(cancel())
            raise

        return Ge1xGripper(response.value)

    def __await__(self) -> Generator[Any, None, 'Ge1xGripper']:
        return self._create_resource().__await__()

    async def __aenter__(self) -> 'Ge1xGripper':
        self._resource = await self._create_resource()
        return self._resource

    async def __aexit__(self, exc_type: Any, exc: Any, trace: Any) -> None:
        if self._resource is not None:
            await self._resource.close_async()
