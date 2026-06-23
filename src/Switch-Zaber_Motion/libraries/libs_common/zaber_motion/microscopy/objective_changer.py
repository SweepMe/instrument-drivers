# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Optional
from ..ascii import Device, Axis
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.measurement import Measurement
from ..units import Units, LengthUnits


class ObjectiveChanger:
    """
    Represents an objective changer of a microscope.
    Unstable. Expect breaking changes in future releases.
    Requires at least Firmware 7.32.
    """

    @property
    def turret(self) -> Device:
        """
        Device address of the turret.
        """
        return self._turret

    @property
    def focus_axis(self) -> Axis:
        """
        The focus axis.
        """
        return self._focus_axis

    def __init__(self, turret: Device, focus_axis: Axis):
        """
        Creates instance of `ObjectiveChanger` based on the given device.
        If the device is identified, this constructor will ensure it is an objective changer.
        """
        self._turret: Device = turret
        self._focus_axis: Axis = focus_axis
        self.__verify_is_changer()

    def change(
            self,
            objective: int,
            focus_offset: Optional[Measurement] = None
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.
        The focus stage moves to the focus datum after the objective change.

        Args:
            objective: Objective number starting from 1.
            focus_offset: Optional offset from the focus datum.
        """
        request = dto.ObjectiveChangerChangeRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            objective=objective,
            focus_offset=focus_offset,
        )
        call("objective_changer/change", request)

    async def change_async(
            self,
            objective: int,
            focus_offset: Optional[Measurement] = None
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.
        The focus stage moves to the focus datum after the objective change.

        Args:
            objective: Objective number starting from 1.
            focus_offset: Optional offset from the focus datum.
        """
        request = dto.ObjectiveChangerChangeRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            objective=objective,
            focus_offset=focus_offset,
        )
        await call_async("objective_changer/change", request)

    def release(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = dto.ObjectiveChangerRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
        )
        call("objective_changer/release", request)

    async def release_async(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = dto.ObjectiveChangerRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
        )
        await call_async("objective_changer/release", request)

    def get_current_objective(
            self
    ) -> int:
        """
        Returns current objective number starting from 1.
        The value of 0 indicates that the position is either unknown or between two objectives.

        Returns:
            Current objective number starting from 1 or 0 if not applicable.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.turret.connection.interface_id,
            device=self.turret.device_address,
            axis=1,
        )
        response = call(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_current_objective_async(
            self
    ) -> int:
        """
        Returns current objective number starting from 1.
        The value of 0 indicates that the position is either unknown or between two objectives.

        Returns:
            Current objective number starting from 1 or 0 if not applicable.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.turret.connection.interface_id,
            device=self.turret.device_address,
            axis=1,
        )
        response = await call_async(
            "device/get_index_position",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_number_of_objectives(
            self
    ) -> int:
        """
        Gets number of objectives that the turret can accommodate.

        Returns:
            Number of positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.turret.connection.interface_id,
            device=self.turret.device_address,
            axis=1,
        )
        response = call(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    async def get_number_of_objectives_async(
            self
    ) -> int:
        """
        Gets number of objectives that the turret can accommodate.

        Returns:
            Number of positions.
        """
        request = dto.AxisEmptyRequest(
            interface_id=self.turret.connection.interface_id,
            device=self.turret.device_address,
            axis=1,
        )
        response = await call_async(
            "device/get_index_count",
            request,
            dto.IntResponse.from_binary)
        return response.value

    def get_focus_datum(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            unit: Units of datum.

        Returns:
            The datum.
        """
        request = dto.ObjectiveChangerSetRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            unit=unit,
        )
        response = call(
            "objective_changer/get_datum",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_focus_datum_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            unit: Units of datum.

        Returns:
            The datum.
        """
        request = dto.ObjectiveChangerSetRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            unit=unit,
        )
        response = await call_async(
            "objective_changer/get_datum",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_focus_datum(
            self,
            datum: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            datum: Value of datum.
            unit: Units of datum.
        """
        request = dto.ObjectiveChangerSetRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            value=datum,
            unit=unit,
        )
        call("objective_changer/set_datum", request)

    async def set_focus_datum_async(
            self,
            datum: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            datum: Value of datum.
            unit: Units of datum.
        """
        request = dto.ObjectiveChangerSetRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
            value=datum,
            unit=unit,
        )
        await call_async("objective_changer/set_datum", request)

    def __verify_is_changer(
            self
    ) -> None:
        """
        Checks if this is a objective changer and throws an error if it is not.
        """
        request = dto.ObjectiveChangerRequest(
            interface_id=self.turret.connection.interface_id,
            turret_address=self.turret.device_address,
            focus_address=self.focus_axis.device.device_address,
            focus_axis=self.focus_axis.axis_number,
        )
        call_sync("objective_changer/verify", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = dto.AxisToStringRequest(
            interface_id=self.turret.connection.interface_id,
            device=self.turret.device_address,
        )
        response = call_sync(
            "device/device_to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value
