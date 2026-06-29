# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List, Optional
from ..call import call, call_async
from ..dto import requests as dto
from ..dto.ascii.paramset_info import ParamsetInfo
from ..dto.ascii.pid_tuning import PidTuning
from ..dto.ascii.servo_tuning_param import ServoTuningParam
from ..dto.ascii.servo_tuning_paramset import ServoTuningParamset
from ..dto.ascii.simple_tuning import SimpleTuning
from ..dto.ascii.simple_tuning_param_definition import SimpleTuningParamDefinition
from ..units import UnitsAndLiterals, Units
from .axis import Axis


class ServoTuner:
    """
    Exposes the capabilities to inspect and edit an axis' servo tuning.
    Requires at least Firmware 6.25 or 7.00.
    """

    @property
    def axis(self) -> Axis:
        """
        The axis that will be tuned.
        """
        return self._axis

    def __init__(self, axis: Axis):
        """
        Creates instance of ServoTuner for the given axis.
        """
        self._axis: Axis = axis

    def get_startup_paramset(
            self
    ) -> ServoTuningParamset:
        """
        Get the paramset that this device uses by default when it starts up.

        Returns:
            The paramset used when the device restarts.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
        )
        response = call(
            "servotuning/get_startup_set",
            request,
            dto.ServoTuningParamsetResponse.from_binary)
        return response.paramset

    async def get_startup_paramset_async(
            self
    ) -> ServoTuningParamset:
        """
        Get the paramset that this device uses by default when it starts up.

        Returns:
            The paramset used when the device restarts.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
        )
        response = await call_async(
            "servotuning/get_startup_set",
            request,
            dto.ServoTuningParamsetResponse.from_binary)
        return response.paramset

    def set_startup_paramset(
            self,
            paramset: ServoTuningParamset
    ) -> None:
        """
        Set the paramset that this device uses by default when it starts up.

        Args:
            paramset: The paramset to use at startup.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        call("servotuning/set_startup_set", request)

    async def set_startup_paramset_async(
            self,
            paramset: ServoTuningParamset
    ) -> None:
        """
        Set the paramset that this device uses by default when it starts up.

        Args:
            paramset: The paramset to use at startup.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        await call_async("servotuning/set_startup_set", request)

    def load_paramset(
            self,
            to_paramset: ServoTuningParamset,
            from_paramset: ServoTuningParamset
    ) -> None:
        """
        Load the values from one paramset into another.

        Args:
            to_paramset: The paramset to load into.
            from_paramset: The paramset to load from.
        """
        request = dto.LoadParamset(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            to_paramset=to_paramset,
            from_paramset=from_paramset,
        )
        call("servotuning/load_paramset", request)

    async def load_paramset_async(
            self,
            to_paramset: ServoTuningParamset,
            from_paramset: ServoTuningParamset
    ) -> None:
        """
        Load the values from one paramset into another.

        Args:
            to_paramset: The paramset to load into.
            from_paramset: The paramset to load from.
        """
        request = dto.LoadParamset(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            to_paramset=to_paramset,
            from_paramset=from_paramset,
        )
        await call_async("servotuning/load_paramset", request)

    def get_tuning(
            self,
            paramset: ServoTuningParamset
    ) -> ParamsetInfo:
        """
        Get the full set of tuning parameters used by the firmware driving this axis.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The raw representation of the current tuning.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = call(
            "servotuning/get_raw",
            request,
            ParamsetInfo.from_binary)
        return response

    async def get_tuning_async(
            self,
            paramset: ServoTuningParamset
    ) -> ParamsetInfo:
        """
        Get the full set of tuning parameters used by the firmware driving this axis.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The raw representation of the current tuning.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = await call_async(
            "servotuning/get_raw",
            request,
            ParamsetInfo.from_binary)
        return response

    def set_tuning(
            self,
            paramset: ServoTuningParamset,
            tuning_params: List[ServoTuningParam],
            set_unspecified_to_default: bool = False
    ) -> None:
        """
        Set individual tuning parameters.
        Only use this method if you have a strong understanding of Zaber specific tuning parameters.

        Args:
            paramset: The paramset to set tuning of.
            tuning_params: The params to set.
            set_unspecified_to_default: If true, any tuning parameters not included in TuningParams
                are reset to their default values.
        """
        request = dto.SetServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            tuning_params=tuning_params,
            set_unspecified_to_default=set_unspecified_to_default,
        )
        call("servotuning/set_raw", request)

    async def set_tuning_async(
            self,
            paramset: ServoTuningParamset,
            tuning_params: List[ServoTuningParam],
            set_unspecified_to_default: bool = False
    ) -> None:
        """
        Set individual tuning parameters.
        Only use this method if you have a strong understanding of Zaber specific tuning parameters.

        Args:
            paramset: The paramset to set tuning of.
            tuning_params: The params to set.
            set_unspecified_to_default: If true, any tuning parameters not included in TuningParams
                are reset to their default values.
        """
        request = dto.SetServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            tuning_params=tuning_params,
            set_unspecified_to_default=set_unspecified_to_default,
        )
        await call_async("servotuning/set_raw", request)

    def set_pid_tuning(
            self,
            paramset: ServoTuningParamset,
            p: float,
            i: float,
            d: float,
            fc: float
    ) -> PidTuning:
        """
        Sets the tuning of a paramset using the PID method.

        Args:
            paramset: The paramset to get tuning for.
            p: The proportional gain. Must be in units of N/m for linear devices, and N⋅m/° for rotary devices.
            i: The integral gain. Must be in units of N/(m⋅s) for linear devices, and N⋅m/(°⋅s) for rotary devices.
            d: The derivative gain. Must be in units of N⋅s/m for linear devices, and N⋅m⋅s/° for rotary devices.
            fc: The cutoff frequency. Must be in units of Hz.

        Returns:
            The PID representation of the current tuning after your changes have been applied.
        """
        request = dto.SetServoTuningPIDRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            p=p,
            i=i,
            d=d,
            fc=fc,
        )
        response = call(
            "servotuning/set_pid",
            request,
            PidTuning.from_binary)
        return response

    async def set_pid_tuning_async(
            self,
            paramset: ServoTuningParamset,
            p: float,
            i: float,
            d: float,
            fc: float
    ) -> PidTuning:
        """
        Sets the tuning of a paramset using the PID method.

        Args:
            paramset: The paramset to get tuning for.
            p: The proportional gain. Must be in units of N/m for linear devices, and N⋅m/° for rotary devices.
            i: The integral gain. Must be in units of N/(m⋅s) for linear devices, and N⋅m/(°⋅s) for rotary devices.
            d: The derivative gain. Must be in units of N⋅s/m for linear devices, and N⋅m⋅s/° for rotary devices.
            fc: The cutoff frequency. Must be in units of Hz.

        Returns:
            The PID representation of the current tuning after your changes have been applied.
        """
        request = dto.SetServoTuningPIDRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            p=p,
            i=i,
            d=d,
            fc=fc,
        )
        response = await call_async(
            "servotuning/set_pid",
            request,
            PidTuning.from_binary)
        return response

    def get_pid_tuning(
            self,
            paramset: ServoTuningParamset
    ) -> PidTuning:
        """
        Gets the PID representation of this paramset's servo tuning.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The PID representation of the current tuning.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = call(
            "servotuning/get_pid",
            request,
            PidTuning.from_binary)
        return response

    async def get_pid_tuning_async(
            self,
            paramset: ServoTuningParamset
    ) -> PidTuning:
        """
        Gets the PID representation of this paramset's servo tuning.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The PID representation of the current tuning.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = await call_async(
            "servotuning/get_pid",
            request,
            PidTuning.from_binary)
        return response

    def get_simple_tuning_param_definitions(
            self
    ) -> List[SimpleTuningParamDefinition]:
        """
        Gets the parameters that are required to tune this device.

        Returns:
            The tuning parameters.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
        )
        response = call(
            "servotuning/get_simple_params_definition",
            request,
            dto.GetSimpleTuningParamDefinitionResponse.from_binary)
        return response.params

    async def get_simple_tuning_param_definitions_async(
            self
    ) -> List[SimpleTuningParamDefinition]:
        """
        Gets the parameters that are required to tune this device.

        Returns:
            The tuning parameters.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
        )
        response = await call_async(
            "servotuning/get_simple_params_definition",
            request,
            dto.GetSimpleTuningParamDefinitionResponse.from_binary)
        return response.params

    def set_simple_tuning(
            self,
            paramset: ServoTuningParamset,
            tuning_params: List[ServoTuningParam],
            load_inertia: float,
            load_inertia_units: UnitsAndLiterals = Units.NATIVE,
            carriage_inertia: Optional[float] = None,
            carriage_inertia_units: UnitsAndLiterals = Units.NATIVE,
            motor_inertia: Optional[float] = None,
            motor_inertia_units: UnitsAndLiterals = Units.NATIVE,
            enable_feed_forward: bool = True
    ) -> None:
        """
        Set the tuning of this device using the simple input method.

        Args:
            paramset: The paramset to set tuning for.
            tuning_params: The params used to tune this device.
                To get what parameters are expected, call GetSimpleTuningParamList.
                All values must be between 0 and 1.
            load_inertia: The mass loaded on the stage, excluding the mass of the carriage itself.
                Unless specified by the LoadInertiaUnits parameter, this is in units of kg for linear devices,
                and kg⋅m² for rotary devices.
            load_inertia_units: The units the load mass was supplied in.
            carriage_inertia: The mass of the carriage itself. If not supplied, the product's default mass will be used.
                Unless specified by the CarriageInertiaUnits parameter, this is in units of kg for linear devices,
                and kg⋅m² for rotary devices.
            carriage_inertia_units: The units the carriage mass was supplied in.
            motor_inertia: The inertia of the motor. Unless specified by the MotorInertiaUnits parameter,
                this is in units of kg⋅m².
            motor_inertia_units: The units the motor inertia was supplied in.
            enable_feed_forward: Whether to enable the inertial feed-forward term.
        """
        request = dto.SetSimpleTuning(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            tuning_params=tuning_params,
            load_inertia=load_inertia,
            load_inertia_units=load_inertia_units,
            carriage_inertia=carriage_inertia,
            carriage_inertia_units=carriage_inertia_units,
            motor_inertia=motor_inertia,
            motor_inertia_units=motor_inertia_units,
            enable_feed_forward=enable_feed_forward,
        )
        call("servotuning/set_simple_tuning", request)

    async def set_simple_tuning_async(
            self,
            paramset: ServoTuningParamset,
            tuning_params: List[ServoTuningParam],
            load_inertia: float,
            load_inertia_units: UnitsAndLiterals = Units.NATIVE,
            carriage_inertia: Optional[float] = None,
            carriage_inertia_units: UnitsAndLiterals = Units.NATIVE,
            motor_inertia: Optional[float] = None,
            motor_inertia_units: UnitsAndLiterals = Units.NATIVE,
            enable_feed_forward: bool = True
    ) -> None:
        """
        Set the tuning of this device using the simple input method.

        Args:
            paramset: The paramset to set tuning for.
            tuning_params: The params used to tune this device.
                To get what parameters are expected, call GetSimpleTuningParamList.
                All values must be between 0 and 1.
            load_inertia: The mass loaded on the stage, excluding the mass of the carriage itself.
                Unless specified by the LoadInertiaUnits parameter, this is in units of kg for linear devices,
                and kg⋅m² for rotary devices.
            load_inertia_units: The units the load mass was supplied in.
            carriage_inertia: The mass of the carriage itself. If not supplied, the product's default mass will be used.
                Unless specified by the CarriageInertiaUnits parameter, this is in units of kg for linear devices,
                and kg⋅m² for rotary devices.
            carriage_inertia_units: The units the carriage mass was supplied in.
            motor_inertia: The inertia of the motor. Unless specified by the MotorInertiaUnits parameter,
                this is in units of kg⋅m².
            motor_inertia_units: The units the motor inertia was supplied in.
            enable_feed_forward: Whether to enable the inertial feed-forward term.
        """
        request = dto.SetSimpleTuning(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
            tuning_params=tuning_params,
            load_inertia=load_inertia,
            load_inertia_units=load_inertia_units,
            carriage_inertia=carriage_inertia,
            carriage_inertia_units=carriage_inertia_units,
            motor_inertia=motor_inertia,
            motor_inertia_units=motor_inertia_units,
            enable_feed_forward=enable_feed_forward,
        )
        await call_async("servotuning/set_simple_tuning", request)

    def get_simple_tuning(
            self,
            paramset: ServoTuningParamset
    ) -> SimpleTuning:
        """
        Get the simple tuning parameters for this device.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The simple tuning parameters.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = call(
            "servotuning/get_simple_tuning",
            request,
            SimpleTuning.from_binary)
        return response

    async def get_simple_tuning_async(
            self,
            paramset: ServoTuningParamset
    ) -> SimpleTuning:
        """
        Get the simple tuning parameters for this device.

        Args:
            paramset: The paramset to get tuning for.

        Returns:
            The simple tuning parameters.
        """
        request = dto.ServoTuningRequest(
            interface_id=self.axis.device.connection.interface_id,
            device=self.axis.device.device_address,
            axis=self.axis.axis_number,
            paramset=paramset,
        )
        response = await call_async(
            "servotuning/get_simple_tuning",
            request,
            SimpleTuning.from_binary)
        return response
