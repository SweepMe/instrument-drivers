# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .axis_definition import AxisDefinition
from ..measurement import Measurement


@dataclass
class DeviceDefinition:
    """
    Holds information about device and its axes for purpose of a translator.
    """

    device_id: int
    """
    Device ID of the controller.
    Can be obtained from device settings.
    """

    axes: List[AxisDefinition]
    """
    Applicable axes of the device.
    """

    max_speed: Measurement
    """
    The smallest of each axis' maxspeed setting value.
    This value becomes the traverse rate of the translator.
    """

    @staticmethod
    def zero_values() -> 'DeviceDefinition':
        return DeviceDefinition(
            device_id=0,
            axes=[],
            max_speed=Measurement.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDefinition':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDefinition.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceId': int(self.device_id),
            'axes': [item.to_dict() for item in self.axes] if self.axes is not None else [],
            'maxSpeed': self.max_speed.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDefinition':
        return DeviceDefinition(
            device_id=data.get('deviceId'),  # type: ignore
            axes=[AxisDefinition.from_dict(item) for item in data.get('axes')],  # type: ignore
            max_speed=Measurement.from_dict(data.get('maxSpeed')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_id is None:
            raise ValueError(f'Property "DeviceId" of "DeviceDefinition" is None.')

        if not isinstance(self.device_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceId" of "DeviceDefinition" is not a number.')

        if int(self.device_id) != self.device_id:
            raise ValueError(f'Property "DeviceId" of "DeviceDefinition" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "DeviceDefinition" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "DeviceDefinition" is None.')

                if not isinstance(axes_item, AxisDefinition):
                    raise ValueError(f'Item {i} in property "Axes" of "DeviceDefinition" is not an instance of "AxisDefinition".')

                axes_item.validate()

        if self.max_speed is None:
            raise ValueError(f'Property "MaxSpeed" of "DeviceDefinition" is None.')

        if not isinstance(self.max_speed, Measurement):
            raise ValueError(f'Property "MaxSpeed" of "DeviceDefinition" is not an instance of "Measurement".')

        self.max_speed.validate()
