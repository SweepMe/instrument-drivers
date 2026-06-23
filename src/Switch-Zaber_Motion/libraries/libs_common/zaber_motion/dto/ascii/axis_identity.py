# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .axis_type import AxisType


@dataclass
class AxisIdentity:
    """
    Representation of data gathered during axis identification.
    """

    peripheral_id: int
    """
    Unique ID of the peripheral hardware.
    """

    peripheral_name: str
    """
    Name of the peripheral.
    """

    peripheral_serial_number: int
    """
    Serial number of the peripheral, or 0 when not applicable.
    """

    is_peripheral: bool
    """
    Indicates whether the axis is a peripheral or part of an integrated device.
    """

    axis_type: AxisType
    """
    Determines the type of an axis and units it accepts.
    """

    is_modified: bool
    """
    The peripheral has hardware modifications.
    """

    resolution: int
    """
    The number of microsteps per full step for motion axes. Always equal to 0 for non-motion axes.
    """

    @staticmethod
    def zero_values() -> 'AxisIdentity':
        return AxisIdentity(
            peripheral_id=0,
            peripheral_name="",
            peripheral_serial_number=0,
            is_peripheral=False,
            axis_type=next(first for first in AxisType),
            is_modified=False,
            resolution=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisIdentity':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisIdentity.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'peripheralId': int(self.peripheral_id),
            'peripheralName': str(self.peripheral_name or ''),
            'peripheralSerialNumber': int(self.peripheral_serial_number),
            'isPeripheral': bool(self.is_peripheral),
            'axisType': self.axis_type.value,
            'isModified': bool(self.is_modified),
            'resolution': int(self.resolution),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisIdentity':
        return AxisIdentity(
            peripheral_id=data.get('peripheralId'),  # type: ignore
            peripheral_name=data.get('peripheralName'),  # type: ignore
            peripheral_serial_number=data.get('peripheralSerialNumber'),  # type: ignore
            is_peripheral=data.get('isPeripheral'),  # type: ignore
            axis_type=AxisType(data.get('axisType')),  # type: ignore
            is_modified=data.get('isModified'),  # type: ignore
            resolution=data.get('resolution'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.peripheral_id is None:
            raise ValueError(f'Property "PeripheralId" of "AxisIdentity" is None.')

        if not isinstance(self.peripheral_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PeripheralId" of "AxisIdentity" is not a number.')

        if int(self.peripheral_id) != self.peripheral_id:
            raise ValueError(f'Property "PeripheralId" of "AxisIdentity" is not integer value.')

        if self.peripheral_name is not None:
            if not isinstance(self.peripheral_name, str):
                raise ValueError(f'Property "PeripheralName" of "AxisIdentity" is not a string.')

        if self.peripheral_serial_number is None:
            raise ValueError(f'Property "PeripheralSerialNumber" of "AxisIdentity" is None.')

        if not isinstance(self.peripheral_serial_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PeripheralSerialNumber" of "AxisIdentity" is not a number.')

        if int(self.peripheral_serial_number) != self.peripheral_serial_number:
            raise ValueError(f'Property "PeripheralSerialNumber" of "AxisIdentity" is not integer value.')

        if self.axis_type is None:
            raise ValueError(f'Property "AxisType" of "AxisIdentity" is None.')

        if not isinstance(self.axis_type, AxisType):
            raise ValueError(f'Property "AxisType" of "AxisIdentity" is not an instance of "AxisType".')

        if self.resolution is None:
            raise ValueError(f'Property "Resolution" of "AxisIdentity" is None.')

        if not isinstance(self.resolution, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Resolution" of "AxisIdentity" is not a number.')

        if int(self.resolution) != self.resolution:
            raise ValueError(f'Property "Resolution" of "AxisIdentity" is not integer value.')
