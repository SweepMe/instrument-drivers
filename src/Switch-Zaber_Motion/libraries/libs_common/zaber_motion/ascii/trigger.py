# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Optional
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.io_port_type import IoPortType
from ..dto.ascii.trigger_action import TriggerAction
from ..dto.ascii.trigger_condition import TriggerCondition
from ..dto.ascii.trigger_enabled_state import TriggerEnabledState
from ..dto.ascii.trigger_operation import TriggerOperation
from ..dto.ascii.trigger_state import TriggerState
from ..units import Units, LengthUnits, UnitsAndLiterals, TimeUnits

if TYPE_CHECKING:
    from .device import Device


class Trigger:
    """
    A handle for a trigger with this number on the device.
    Triggers allow setting up actions that occur when a certain condition has been met or an event has occurred.
    Please note that the Triggers API is currently an experimental feature.
    Requires at least Firmware 7.06.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that this trigger belongs to.
        """
        return self._device

    @property
    def trigger_number(self) -> int:
        """
        Number of this trigger.
        """
        return self._trigger_number

    def __init__(self, device: 'Device', trigger_number: int):
        self._device: 'Device' = device
        self._trigger_number: int = trigger_number

    def enable(
            self,
            count: int = 0
    ) -> None:
        """
        Enables the trigger.
        Once a trigger is enabled, it will fire whenever its condition transitions from false to true.
        If a trigger condition is true when a disabled trigger is enabled, the trigger will fire immediately.

        Args:
            count: Number of times the trigger will fire before disabling itself.
                If count is not specified, or 0, the trigger will fire indefinitely.
        """
        if count < 0:
            raise ValueError('Invalid value; count must be 0 or positive.')

        request = dto.TriggerEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            count=count,
        )
        call("trigger/enable", request)

    async def enable_async(
            self,
            count: int = 0
    ) -> None:
        """
        Enables the trigger.
        Once a trigger is enabled, it will fire whenever its condition transitions from false to true.
        If a trigger condition is true when a disabled trigger is enabled, the trigger will fire immediately.

        Args:
            count: Number of times the trigger will fire before disabling itself.
                If count is not specified, or 0, the trigger will fire indefinitely.
        """
        if count < 0:
            raise ValueError('Invalid value; count must be 0 or positive.')

        request = dto.TriggerEnableRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            count=count,
        )
        await call_async("trigger/enable", request)

    def disable(
            self
    ) -> None:
        """
        Disables the trigger.
        Once disabled, the trigger will not fire and trigger actions will not run, even if trigger conditions are met.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        call("trigger/disable", request)

    async def disable_async(
            self
    ) -> None:
        """
        Disables the trigger.
        Once disabled, the trigger will not fire and trigger actions will not run, even if trigger conditions are met.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        await call_async("trigger/disable", request)

    def get_state(
            self
    ) -> TriggerState:
        """
        Gets the state of the trigger.

        Returns:
            Complete state of the trigger.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = call(
            "trigger/get_state",
            request,
            TriggerState.from_binary)
        return response

    async def get_state_async(
            self
    ) -> TriggerState:
        """
        Gets the state of the trigger.

        Returns:
            Complete state of the trigger.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = await call_async(
            "trigger/get_state",
            request,
            TriggerState.from_binary)
        return response

    def get_enabled_state(
            self
    ) -> TriggerEnabledState:
        """
        Gets the enabled state of the trigger.

        Returns:
            Whether the trigger is enabled and the number of times it will fire.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = call(
            "trigger/get_enabled_state",
            request,
            TriggerEnabledState.from_binary)
        return response

    async def get_enabled_state_async(
            self
    ) -> TriggerEnabledState:
        """
        Gets the enabled state of the trigger.

        Returns:
            Whether the trigger is enabled and the number of times it will fire.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = await call_async(
            "trigger/get_enabled_state",
            request,
            TriggerEnabledState.from_binary)
        return response

    def fire_when(
            self,
            condition: str
    ) -> None:
        """
        Set a generic trigger condition.

        Args:
            condition: The condition to set for this trigger.
        """
        request = dto.TriggerFireWhenRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            condition=condition,
        )
        call("trigger/fire_when", request)

    async def fire_when_async(
            self,
            condition: str
    ) -> None:
        """
        Set a generic trigger condition.

        Args:
            condition: The condition to set for this trigger.
        """
        request = dto.TriggerFireWhenRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            condition=condition,
        )
        await call_async("trigger/fire_when", request)

    def fire_when_encoder_distance_travelled(
            self,
            axis: int,
            distance: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition for when an encoder position has changed by a specific distance.

        Args:
            axis: The axis to monitor for this condition.
                May be set to 0 on single-axis devices only.
            distance: The measured encoder distance between trigger fires.
            unit: Units of dist.
        """
        if distance <= 0:
            raise ValueError('Invalid value; encoder distance must be a positive value.')

        request = dto.TriggerFireWhenDistanceTravelledRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            distance=distance,
            unit=unit,
        )
        call("trigger/fire_when_encoder_distance_travelled", request)

    async def fire_when_encoder_distance_travelled_async(
            self,
            axis: int,
            distance: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition for when an encoder position has changed by a specific distance.

        Args:
            axis: The axis to monitor for this condition.
                May be set to 0 on single-axis devices only.
            distance: The measured encoder distance between trigger fires.
            unit: Units of dist.
        """
        if distance <= 0:
            raise ValueError('Invalid value; encoder distance must be a positive value.')

        request = dto.TriggerFireWhenDistanceTravelledRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            distance=distance,
            unit=unit,
        )
        await call_async("trigger/fire_when_encoder_distance_travelled", request)

    def fire_when_distance_travelled(
            self,
            axis: int,
            distance: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition for when an axis position has changed by a specific distance.

        Args:
            axis: The axis to monitor for this condition.
                May be set to 0 on single-axis devices only.
            distance: The measured distance between trigger fires.
            unit: Units of dist.
        """
        if distance <= 0:
            raise ValueError('Invalid value; distance must be a positive value.')

        request = dto.TriggerFireWhenDistanceTravelledRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            distance=distance,
            unit=unit,
        )
        call("trigger/fire_when_distance_travelled", request)

    async def fire_when_distance_travelled_async(
            self,
            axis: int,
            distance: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition for when an axis position has changed by a specific distance.

        Args:
            axis: The axis to monitor for this condition.
                May be set to 0 on single-axis devices only.
            distance: The measured distance between trigger fires.
            unit: Units of dist.
        """
        if distance <= 0:
            raise ValueError('Invalid value; distance must be a positive value.')

        request = dto.TriggerFireWhenDistanceTravelledRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            distance=distance,
            unit=unit,
        )
        await call_async("trigger/fire_when_distance_travelled", request)

    def fire_when_io(
            self,
            port_type: IoPortType,
            channel: int,
            trigger_condition: TriggerCondition,
            value: float
    ) -> None:
        """
        Set a trigger condition based on an IO channel value.

        Args:
            port_type: The type of IO channel to monitor.
            channel: The IO channel to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
        """
        if channel <= 0:
            raise ValueError('Invalid value; channel must be a positive value.')

        request = dto.TriggerFireWhenIoRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            port_type=port_type,
            channel=channel,
            trigger_condition=trigger_condition,
            value=value,
        )
        call("trigger/fire_when_io", request)

    async def fire_when_io_async(
            self,
            port_type: IoPortType,
            channel: int,
            trigger_condition: TriggerCondition,
            value: float
    ) -> None:
        """
        Set a trigger condition based on an IO channel value.

        Args:
            port_type: The type of IO channel to monitor.
            channel: The IO channel to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
        """
        if channel <= 0:
            raise ValueError('Invalid value; channel must be a positive value.')

        request = dto.TriggerFireWhenIoRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            port_type=port_type,
            channel=channel,
            trigger_condition=trigger_condition,
            value=value,
        )
        await call_async("trigger/fire_when_io", request)

    def fire_when_setting(
            self,
            axis: int,
            setting: str,
            trigger_condition: TriggerCondition,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on a setting value.

        Args:
            axis: The axis to monitor for this condition.
                Set to 0 for device-scope settings.
            setting: The setting to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
            unit: Units of value.
        """
        request = dto.TriggerFireWhenSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            setting=setting,
            trigger_condition=trigger_condition,
            value=value,
            unit=unit,
        )
        call("trigger/fire_when_setting", request)

    async def fire_when_setting_async(
            self,
            axis: int,
            setting: str,
            trigger_condition: TriggerCondition,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on a setting value.

        Args:
            axis: The axis to monitor for this condition.
                Set to 0 for device-scope settings.
            setting: The setting to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
            unit: Units of value.
        """
        request = dto.TriggerFireWhenSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            setting=setting,
            trigger_condition=trigger_condition,
            value=value,
            unit=unit,
        )
        await call_async("trigger/fire_when_setting", request)

    def fire_when_absolute_setting(
            self,
            axis: int,
            setting: str,
            trigger_condition: TriggerCondition,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on an absolute setting value.

        Args:
            axis: The axis to monitor for this condition.
                Set to 0 for device-scope settings.
            setting: The setting to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
            unit: Units of value.
        """
        request = dto.TriggerFireWhenSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            setting=setting,
            trigger_condition=trigger_condition,
            value=value,
            unit=unit,
        )
        call("trigger/fire_when_setting_absolute", request)

    async def fire_when_absolute_setting_async(
            self,
            axis: int,
            setting: str,
            trigger_condition: TriggerCondition,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on an absolute setting value.

        Args:
            axis: The axis to monitor for this condition.
                Set to 0 for device-scope settings.
            setting: The setting to monitor.
            trigger_condition: Comparison operator.
            value: Comparison value.
            unit: Units of value.
        """
        request = dto.TriggerFireWhenSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            axis=axis,
            setting=setting,
            trigger_condition=trigger_condition,
            value=value,
            unit=unit,
        )
        await call_async("trigger/fire_when_setting_absolute", request)

    def fire_at_interval(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on a time interval.

        Args:
            interval: The time interval between trigger fires.
            unit: Units of time.
        """
        if interval <= 0:
            raise ValueError('Invalid value; interval must be a positive value.')

        request = dto.TriggerFireAtIntervalRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            interval=interval,
            unit=unit,
        )
        call("trigger/fire_at_interval", request)

    async def fire_at_interval_async(
            self,
            interval: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Set a trigger condition based on a time interval.

        Args:
            interval: The time interval between trigger fires.
            unit: Units of time.
        """
        if interval <= 0:
            raise ValueError('Invalid value; interval must be a positive value.')

        request = dto.TriggerFireAtIntervalRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            interval=interval,
            unit=unit,
        )
        await call_async("trigger/fire_at_interval", request)

    def on_fire(
            self,
            action: TriggerAction,
            axis: int,
            command: str
    ) -> None:
        """
        Set a command to be a trigger action.

        Args:
            action: The action number to assign the command to.
            axis: The axis to on which to run this command.
                Set to 0 for device-scope settings or to run command on all axes.
            command: The command to run when the action is triggered.
        """
        request = dto.TriggerOnFireRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            command=command,
        )
        call("trigger/on_fire", request)

    async def on_fire_async(
            self,
            action: TriggerAction,
            axis: int,
            command: str
    ) -> None:
        """
        Set a command to be a trigger action.

        Args:
            action: The action number to assign the command to.
            axis: The axis to on which to run this command.
                Set to 0 for device-scope settings or to run command on all axes.
            command: The command to run when the action is triggered.
        """
        request = dto.TriggerOnFireRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            command=command,
        )
        await call_async("trigger/on_fire", request)

    def on_fire_set(
            self,
            action: TriggerAction,
            axis: int,
            setting: str,
            operation: TriggerOperation,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger action to update a setting.

        Args:
            action: The action number to assign the command to.
            axis: The axis on which to change the setting.
                Set to 0 to change the setting for the device.
            setting: The name of the setting to change.
            operation: The operation to apply to the setting.
            value: Operation value.
            unit: Units of value.
        """
        request = dto.TriggerOnFireSetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            setting=setting,
            operation=operation,
            value=value,
            unit=unit,
        )
        call("trigger/on_fire_set", request)

    async def on_fire_set_async(
            self,
            action: TriggerAction,
            axis: int,
            setting: str,
            operation: TriggerOperation,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Set a trigger action to update a setting.

        Args:
            action: The action number to assign the command to.
            axis: The axis on which to change the setting.
                Set to 0 to change the setting for the device.
            setting: The name of the setting to change.
            operation: The operation to apply to the setting.
            value: Operation value.
            unit: Units of value.
        """
        request = dto.TriggerOnFireSetRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            setting=setting,
            operation=operation,
            value=value,
            unit=unit,
        )
        await call_async("trigger/on_fire_set", request)

    def on_fire_set_to_setting(
            self,
            action: TriggerAction,
            axis: int,
            setting: str,
            operation: TriggerOperation,
            from_axis: int,
            from_setting: str
    ) -> None:
        """
        Set a trigger action to update a setting with the value of another setting.

        Args:
            action: The action number to assign the command to.
            axis: The axis on which to change the setting.
                Set to 0 to change the setting for the device.
            setting: The name of the setting to change.
                Must have either integer or boolean type.
            operation: The operation to apply to the setting.
            from_axis: The axis from which to read the setting.
                Set to 0 to read the setting from the device.
            from_setting: The name of the setting to read.
                Must have either integer or boolean type.
        """
        request = dto.TriggerOnFireSetToSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            setting=setting,
            operation=operation,
            from_axis=from_axis,
            from_setting=from_setting,
        )
        call("trigger/on_fire_set_to_setting", request)

    async def on_fire_set_to_setting_async(
            self,
            action: TriggerAction,
            axis: int,
            setting: str,
            operation: TriggerOperation,
            from_axis: int,
            from_setting: str
    ) -> None:
        """
        Set a trigger action to update a setting with the value of another setting.

        Args:
            action: The action number to assign the command to.
            axis: The axis on which to change the setting.
                Set to 0 to change the setting for the device.
            setting: The name of the setting to change.
                Must have either integer or boolean type.
            operation: The operation to apply to the setting.
            from_axis: The axis from which to read the setting.
                Set to 0 to read the setting from the device.
            from_setting: The name of the setting to read.
                Must have either integer or boolean type.
        """
        request = dto.TriggerOnFireSetToSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
            axis=axis,
            setting=setting,
            operation=operation,
            from_axis=from_axis,
            from_setting=from_setting,
        )
        await call_async("trigger/on_fire_set_to_setting", request)

    def clear_action(
            self,
            action: TriggerAction = TriggerAction.ALL
    ) -> None:
        """
        Clear a trigger action.

        Args:
            action: The action number to clear.
                The default option is to clear all actions.
        """
        request = dto.TriggerClearActionRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
        )
        call("trigger/clear_action", request)

    async def clear_action_async(
            self,
            action: TriggerAction = TriggerAction.ALL
    ) -> None:
        """
        Clear a trigger action.

        Args:
            action: The action number to clear.
                The default option is to clear all actions.
        """
        request = dto.TriggerClearActionRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            action=action,
        )
        await call_async("trigger/clear_action", request)

    def get_label(
            self
    ) -> str:
        """
        Returns the label for the trigger.

        Returns:
            The label for the trigger.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = call(
            "trigger/get_label",
            request,
            dto.StringResponse.from_binary)
        return response.value

    async def get_label_async(
            self
    ) -> str:
        """
        Returns the label for the trigger.

        Returns:
            The label for the trigger.
        """
        request = dto.TriggerEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
        )
        response = await call_async(
            "trigger/get_label",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def set_label(
            self,
            label: Optional[str]
    ) -> None:
        """
        Sets the label for the trigger.

        Args:
            label: The label to set for this trigger.
                If no value or an empty string is provided, this label is deleted.
        """
        request = dto.TriggerSetLabelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            label=label,
        )
        call("trigger/set_label", request)

    async def set_label_async(
            self,
            label: Optional[str]
    ) -> None:
        """
        Sets the label for the trigger.

        Args:
            label: The label to set for this trigger.
                If no value or an empty string is provided, this label is deleted.
        """
        request = dto.TriggerSetLabelRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            trigger_number=self.trigger_number,
            label=label,
        )
        await call_async("trigger/set_label", request)
