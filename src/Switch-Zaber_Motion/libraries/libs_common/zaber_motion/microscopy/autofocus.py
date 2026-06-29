# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Optional, List
from ..ascii import Device, Axis
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.microscopy.autofocus_status import AutofocusStatus
from ..dto.named_parameter import NamedParameter
from ..units import LengthUnits, Units


class Autofocus:
    """
    A generic autofocus device.
    """

    @property
    def provider_id(self) -> int:
        """
        The identification of external device providing the capability.
        """
        return self._provider_id

    @property
    def focus_axis(self) -> Axis:
        """
        The focus axis.
        """
        return self._focus_axis

    @property
    def objective_turret(self) -> Optional[Device]:
        """
        The objective turret device if the microscope has one.
        """
        return self._objective_turret

    def __init__(self, provider_id: int, focus_axis: Axis, objective_turret: Optional[Device]):
        """
        Creates instance of `Autofocus` based on the given provider id.
        """
        self._provider_id: int = provider_id
        self._focus_axis: Axis = focus_axis
        self._objective_turret: Optional[Device] = objective_turret

    def set_focus_zero(
            self
    ) -> None:
        """
        Sets the current focus to be target for the autofocus control loop.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        call("autofocus/set_zero", request)

    async def set_focus_zero_async(
            self
    ) -> None:
        """
        Sets the current focus to be target for the autofocus control loop.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        await call_async("autofocus/set_zero", request)

    def get_status(
            self
    ) -> AutofocusStatus:
        """
        Returns the status of the autofocus.

        Returns:
            The status of the autofocus.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        response = call(
            "autofocus/get_status",
            request,
            dto.AutofocusGetStatusResponse.from_binary)
        return response.status

    async def get_status_async(
            self
    ) -> AutofocusStatus:
        """
        Returns the status of the autofocus.

        Returns:
            The status of the autofocus.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        response = await call_async(
            "autofocus/get_status",
            request,
            dto.AutofocusGetStatusResponse.from_binary)
        return response.status

    def focus_once(
            self,
            scan: bool = False,
            timeout: int = -1
    ) -> None:
        """
        Moves the device until it's in focus.

        Args:
            scan: If true, the autofocus will approach from the limit moving until it's in range.
            timeout: Sets autofocus timeout duration in milliseconds.
        """
        request = dto.AutofocusFocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            once=True,
            scan=scan,
            timeout=timeout,
        )
        call("autofocus/focus_once", request)

    async def focus_once_async(
            self,
            scan: bool = False,
            timeout: int = -1
    ) -> None:
        """
        Moves the device until it's in focus.

        Args:
            scan: If true, the autofocus will approach from the limit moving until it's in range.
            timeout: Sets autofocus timeout duration in milliseconds.
        """
        request = dto.AutofocusFocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            once=True,
            scan=scan,
            timeout=timeout,
        )
        await call_async("autofocus/focus_once", request)

    def start_focus_loop(
            self
    ) -> None:
        """
        Moves the focus axis continuously maintaining focus.
        Starts the autofocus control loop.
        Note that the control loop may stop if the autofocus comes out of range or a movement error occurs.
        Use WaitUntilIdle of the focus axis to wait for the loop to stop and handle potential errors.
        """
        request = dto.AutofocusFocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        call("autofocus/start_focus_loop", request)

    async def start_focus_loop_async(
            self
    ) -> None:
        """
        Moves the focus axis continuously maintaining focus.
        Starts the autofocus control loop.
        Note that the control loop may stop if the autofocus comes out of range or a movement error occurs.
        Use WaitUntilIdle of the focus axis to wait for the loop to stop and handle potential errors.
        """
        request = dto.AutofocusFocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        await call_async("autofocus/start_focus_loop", request)

    def stop_focus_loop(
            self
    ) -> None:
        """
        Stops autofocus control loop.
        If the focus axis already stopped moving because of an error, an exception will be thrown.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        call("autofocus/stop_focus_loop", request)

    async def stop_focus_loop_async(
            self
    ) -> None:
        """
        Stops autofocus control loop.
        If the focus axis already stopped moving because of an error, an exception will be thrown.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        await call_async("autofocus/stop_focus_loop", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the focus axis is busy.
        Can be used to determine if the focus loop is running.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
        )
        response = call(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the focus axis is busy.
        Can be used to determine if the focus loop is running.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
        )
        response = await call_async(
            "device/is_busy",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def get_limit_min(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the lower motion limit for the autofocus control loop.
        Gets motion.tracking.limit.min setting of the focus axis.

        Args:
            unit: The units of the limit.

        Returns:
            Limit value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.min",
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_limit_min_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the lower motion limit for the autofocus control loop.
        Gets motion.tracking.limit.min setting of the focus axis.

        Args:
            unit: The units of the limit.

        Returns:
            Limit value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.min",
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_limit_max(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the upper motion limit for the autofocus control loop.
        Gets motion.tracking.limit.max setting of the focus axis.

        Args:
            unit: The units of the limit.

        Returns:
            Limit value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.max",
            unit=unit,
        )
        response = call(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_limit_max_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the upper motion limit for the autofocus control loop.
        Gets motion.tracking.limit.max setting of the focus axis.

        Args:
            unit: The units of the limit.

        Returns:
            Limit value.
        """
        request = dto.DeviceGetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.max",
            unit=unit,
        )
        response = await call_async(
            "device/get_setting",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_limit_min(
            self,
            limit: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the lower motion limit for the autofocus control loop.
        Use the limits to prevent the focus axis from crashing into the sample.
        Changes motion.tracking.limit.min setting of the focus axis.

        Args:
            limit: The lower limit of the focus axis.
            unit: The units of the limit.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.min",
            value=limit,
            unit=unit,
        )
        call("device/set_setting", request)

    async def set_limit_min_async(
            self,
            limit: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the lower motion limit for the autofocus control loop.
        Use the limits to prevent the focus axis from crashing into the sample.
        Changes motion.tracking.limit.min setting of the focus axis.

        Args:
            limit: The lower limit of the focus axis.
            unit: The units of the limit.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.min",
            value=limit,
            unit=unit,
        )
        await call_async("device/set_setting", request)

    def set_limit_max(
            self,
            limit: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the upper motion limit for the autofocus control loop.
        Use the limits to prevent the focus axis from crashing into the sample.
        Changes motion.tracking.limit.max setting of the focus axis.

        Args:
            limit: The upper limit of the focus axis.
            unit: The units of the limit.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.max",
            value=limit,
            unit=unit,
        )
        call("device/set_setting", request)

    async def set_limit_max_async(
            self,
            limit: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the upper motion limit for the autofocus control loop.
        Use the limits to prevent the focus axis from crashing into the sample.
        Changes motion.tracking.limit.max setting of the focus axis.

        Args:
            limit: The upper limit of the focus axis.
            unit: The units of the limit.
        """
        request = dto.DeviceSetSettingRequest(
            interface_id=self.focus_axis.device.connection.interface_id,
            device=self.focus_axis.device.device_address,
            axis=self.focus_axis.axis_number,
            setting="motion.tracking.limit.max",
            value=limit,
            unit=unit,
        )
        await call_async("device/set_setting", request)

    def synchronize_parameters(
            self
    ) -> None:
        """
        Typically, the control loop parameters and objective are kept synchronized by the library.
        If the parameters or current objective changes outside of the library, call this method to synchronize them.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        call("autofocus/sync_params", request)

    async def synchronize_parameters_async(
            self
    ) -> None:
        """
        Typically, the control loop parameters and objective are kept synchronized by the library.
        If the parameters or current objective changes outside of the library, call this method to synchronize them.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        await call_async("autofocus/sync_params", request)

    def set_objective_parameters(
            self,
            objective: int,
            parameters: List[NamedParameter]
    ) -> None:
        """
        Sets the parameters for the autofocus objective.
        Note that the method temporarily switches current objective to set the parameters.

        Args:
            objective: The objective (numbered from 1) to set the parameters for.
                If your microscope has only one objective, use value of 1.
            parameters: The parameters for the autofocus objective.
        """
        request = dto.AutofocusSetObjectiveParamsRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            objective=objective,
            parameters=parameters,
        )
        call("autofocus/set_objective_params", request)

    async def set_objective_parameters_async(
            self,
            objective: int,
            parameters: List[NamedParameter]
    ) -> None:
        """
        Sets the parameters for the autofocus objective.
        Note that the method temporarily switches current objective to set the parameters.

        Args:
            objective: The objective (numbered from 1) to set the parameters for.
                If your microscope has only one objective, use value of 1.
            parameters: The parameters for the autofocus objective.
        """
        request = dto.AutofocusSetObjectiveParamsRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            objective=objective,
            parameters=parameters,
        )
        await call_async("autofocus/set_objective_params", request)

    def get_objective_parameters(
            self,
            objective: int
    ) -> List[NamedParameter]:
        """
        Returns the parameters for the autofocus objective.

        Args:
            objective: The objective (numbered from 1) to get the parameters for.
                If your microscope has only one objective, use value of 1.
                Note that the method temporarily switches current objective to get the parameters.

        Returns:
            The parameters for the autofocus objective.
        """
        request = dto.AutofocusGetObjectiveParamsRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            objective=objective,
        )
        response = call(
            "autofocus/get_objective_params",
            request,
            dto.AutofocusGetObjectiveParamsResponse.from_binary)
        return response.parameters

    async def get_objective_parameters_async(
            self,
            objective: int
    ) -> List[NamedParameter]:
        """
        Returns the parameters for the autofocus objective.

        Args:
            objective: The objective (numbered from 1) to get the parameters for.
                If your microscope has only one objective, use value of 1.
                Note that the method temporarily switches current objective to get the parameters.

        Returns:
            The parameters for the autofocus objective.
        """
        request = dto.AutofocusGetObjectiveParamsRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
            objective=objective,
        )
        response = await call_async(
            "autofocus/get_objective_params",
            request,
            dto.AutofocusGetObjectiveParamsResponse.from_binary)
        return response.parameters

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the autofocus.

        Returns:
            A string that represents the autofocus.
        """
        request = dto.EmptyAutofocusRequest(
            provider_id=self.provider_id,
            interface_id=self.focus_axis.device.connection.interface_id,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            turret_address=self.objective_turret.device_address if self.objective_turret else 0,
        )
        response = call_sync(
            "autofocus/to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
