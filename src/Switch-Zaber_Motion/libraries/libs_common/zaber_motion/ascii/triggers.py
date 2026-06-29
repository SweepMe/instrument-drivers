# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.trigger_enabled_state import TriggerEnabledState
from ..dto.ascii.trigger_state import TriggerState
from .trigger import Trigger

if TYPE_CHECKING:
    from .device import Device


class Triggers:
    """
    Class providing access to device triggers.
    Please note that the Triggers API is currently an experimental feature.
    Requires at least Firmware 7.06.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that these triggers belong to.
        """
        return self._device

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def get_number_of_triggers(
            self
    ) -> int:
        """
        Get the number of triggers for this device.

        Returns:
            Number of triggers for this device.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="trigger.numtriggers",
        )
        response = call(
            "triggers/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_number_of_triggers_async(
            self
    ) -> int:
        """
        Get the number of triggers for this device.

        Returns:
            Number of triggers for this device.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="trigger.numtriggers",
        )
        response = await call_async(
            "triggers/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_number_of_actions(
            self
    ) -> int:
        """
        Get the number of actions for each trigger for this device.

        Returns:
            Number of actions for each trigger for this device.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="trigger.numactions",
        )
        response = call(
            "triggers/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_number_of_actions_async(
            self
    ) -> int:
        """
        Get the number of actions for each trigger for this device.

        Returns:
            Number of actions for each trigger for this device.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
            setting="trigger.numactions",
        )
        response = await call_async(
            "triggers/get_setting",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_trigger(
            self,
            trigger_number: int
    ) -> 'Trigger':
        """
        Get a specific trigger for this device.

        Args:
            trigger_number: The number of the trigger to control. Trigger numbers start at 1.

        Returns:
            Trigger instance.
        """
        if trigger_number <= 0:
            raise ValueError('Invalid value; triggers are numbered from 1.')

        return Trigger(self.device, trigger_number)

    def get_trigger_states(
            self
    ) -> List[TriggerState]:
        """
        Get the state for every trigger for this device.

        Returns:
            Complete state for every trigger.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = call(
            "triggers/get_trigger_states",
            request,
            dto.TriggerStates.from_binary)
        return response.states

    async def get_trigger_states_async(
            self
    ) -> List[TriggerState]:
        """
        Get the state for every trigger for this device.

        Returns:
            Complete state for every trigger.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = await call_async(
            "triggers/get_trigger_states",
            request,
            dto.TriggerStates.from_binary)
        return response.states

    def get_enabled_states(
            self
    ) -> List[TriggerEnabledState]:
        """
        Gets the enabled state for every trigger for this device.

        Returns:
            Whether triggers are enabled and the number of times they will fire.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = call(
            "triggers/get_enabled_states",
            request,
            dto.TriggerEnabledStates.from_binary)
        return response.states

    async def get_enabled_states_async(
            self
    ) -> List[TriggerEnabledState]:
        """
        Gets the enabled state for every trigger for this device.

        Returns:
            Whether triggers are enabled and the number of times they will fire.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = await call_async(
            "triggers/get_enabled_states",
            request,
            dto.TriggerEnabledStates.from_binary)
        return response.states

    def get_all_labels(
            self
    ) -> List[str]:
        """
        Gets the labels for every trigger for this device.

        Returns:
            The labels for every trigger for this device. If a trigger has no label, the value will be an empty string.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = call(
            "triggers/get_all_labels",
            request,
            dto.StringArrayResponse.from_binary)
        return response.values

    async def get_all_labels_async(
            self
    ) -> List[str]:
        """
        Gets the labels for every trigger for this device.

        Returns:
            The labels for every trigger for this device. If a trigger has no label, the value will be an empty string.
        """
        request = dto.DeviceEmptyRequest(
            interface_id=self.device.connection.interface_id,
            device=self.device.device_address,
        )
        response = await call_async(
            "triggers/get_all_labels",
            request,
            dto.StringArrayResponse.from_binary)
        return response.values
