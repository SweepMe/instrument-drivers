# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..axis_address import AxisAddress
from ..channel_address import ChannelAddress


@dataclass
class MicroscopeConfig:
    """
    Configuration representing a microscope setup.
    Device address of value 0 means that the part is not present.
    """

    focus_axis: Optional[AxisAddress] = None
    """
    Focus axis of the microscope.
    """

    x_axis: Optional[AxisAddress] = None
    """
    X axis of the microscope.
    """

    y_axis: Optional[AxisAddress] = None
    """
    Y axis of the microscope.
    """

    illuminator: Optional[int] = None
    """
    Illuminator device address.
    """

    filter_changer: Optional[int] = None
    """
    Filter changer device address.
    """

    objective_changer: Optional[int] = None
    """
    Objective changer device address.
    """

    autofocus: Optional[int] = None
    """
    Autofocus identifier.
    """

    camera_trigger: Optional[ChannelAddress] = None
    """
    Camera trigger digital output address.
    """

    @staticmethod
    def zero_values() -> 'MicroscopeConfig':
        return MicroscopeConfig(
            focus_axis=None,
            x_axis=None,
            y_axis=None,
            illuminator=None,
            filter_changer=None,
            objective_changer=None,
            autofocus=None,
            camera_trigger=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MicroscopeConfig':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MicroscopeConfig.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'focusAxis': self.focus_axis.to_dict() if self.focus_axis is not None else None,
            'xAxis': self.x_axis.to_dict() if self.x_axis is not None else None,
            'yAxis': self.y_axis.to_dict() if self.y_axis is not None else None,
            'illuminator': int(self.illuminator) if self.illuminator is not None else None,
            'filterChanger': int(self.filter_changer) if self.filter_changer is not None else None,
            'objectiveChanger': int(self.objective_changer) if self.objective_changer is not None else None,
            'autofocus': int(self.autofocus) if self.autofocus is not None else None,
            'cameraTrigger': self.camera_trigger.to_dict() if self.camera_trigger is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MicroscopeConfig':
        return MicroscopeConfig(
            focus_axis=AxisAddress.from_dict(data.get('focusAxis')) if data.get('focusAxis') is not None else None,  # type: ignore
            x_axis=AxisAddress.from_dict(data.get('xAxis')) if data.get('xAxis') is not None else None,  # type: ignore
            y_axis=AxisAddress.from_dict(data.get('yAxis')) if data.get('yAxis') is not None else None,  # type: ignore
            illuminator=data.get('illuminator'),  # type: ignore
            filter_changer=data.get('filterChanger'),  # type: ignore
            objective_changer=data.get('objectiveChanger'),  # type: ignore
            autofocus=data.get('autofocus'),  # type: ignore
            camera_trigger=ChannelAddress.from_dict(data.get('cameraTrigger')) if data.get('cameraTrigger') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.focus_axis is not None:
            if not isinstance(self.focus_axis, AxisAddress):
                raise ValueError(f'Property "FocusAxis" of "MicroscopeConfig" is not an instance of "AxisAddress".')

            self.focus_axis.validate()

        if self.x_axis is not None:
            if not isinstance(self.x_axis, AxisAddress):
                raise ValueError(f'Property "XAxis" of "MicroscopeConfig" is not an instance of "AxisAddress".')

            self.x_axis.validate()

        if self.y_axis is not None:
            if not isinstance(self.y_axis, AxisAddress):
                raise ValueError(f'Property "YAxis" of "MicroscopeConfig" is not an instance of "AxisAddress".')

            self.y_axis.validate()

        if self.illuminator is not None:
            if not isinstance(self.illuminator, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Illuminator" of "MicroscopeConfig" is not a number.')

            if int(self.illuminator) != self.illuminator:
                raise ValueError(f'Property "Illuminator" of "MicroscopeConfig" is not integer value.')

        if self.filter_changer is not None:
            if not isinstance(self.filter_changer, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "FilterChanger" of "MicroscopeConfig" is not a number.')

            if int(self.filter_changer) != self.filter_changer:
                raise ValueError(f'Property "FilterChanger" of "MicroscopeConfig" is not integer value.')

        if self.objective_changer is not None:
            if not isinstance(self.objective_changer, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "ObjectiveChanger" of "MicroscopeConfig" is not a number.')

            if int(self.objective_changer) != self.objective_changer:
                raise ValueError(f'Property "ObjectiveChanger" of "MicroscopeConfig" is not integer value.')

        if self.autofocus is not None:
            if not isinstance(self.autofocus, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Autofocus" of "MicroscopeConfig" is not a number.')

            if int(self.autofocus) != self.autofocus:
                raise ValueError(f'Property "Autofocus" of "MicroscopeConfig" is not integer value.')

        if self.camera_trigger is not None:
            if not isinstance(self.camera_trigger, ChannelAddress):
                raise ValueError(f'Property "CameraTrigger" of "MicroscopeConfig" is not an instance of "ChannelAddress".')

            self.camera_trigger.validate()
