# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from .moveable_type import MoveableType
from ..movement.default_motion_units import DefaultMotionUnits


@dataclass
class MoveableSetupRequest:

    interface_id: int = 0

    device: int = 0

    moveable_number: int = 0

    moveable_type: MoveableType = next(first for first in MoveableType)

    default_units: Optional[DefaultMotionUnits] = None

    @staticmethod
    def zero_values() -> 'MoveableSetupRequest':
        return MoveableSetupRequest(
            interface_id=0,
            device=0,
            moveable_number=0,
            moveable_type=next(first for first in MoveableType),
            default_units=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableSetupRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableSetupRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'moveableNumber': int(self.moveable_number),
            'moveableType': self.moveable_type.value,
            'defaultUnits': self.default_units.to_dict() if self.default_units is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableSetupRequest':
        return MoveableSetupRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            moveable_number=data.get('moveableNumber'),  # type: ignore
            moveable_type=MoveableType(data.get('moveableType')),  # type: ignore
            default_units=DefaultMotionUnits.from_dict(data.get('defaultUnits')) if data.get('defaultUnits') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "MoveableSetupRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "MoveableSetupRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "MoveableSetupRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "MoveableSetupRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "MoveableSetupRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "MoveableSetupRequest" is not integer value.')

        if self.moveable_number is None:
            raise ValueError(f'Property "MoveableNumber" of "MoveableSetupRequest" is None.')

        if not isinstance(self.moveable_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableNumber" of "MoveableSetupRequest" is not a number.')

        if int(self.moveable_number) != self.moveable_number:
            raise ValueError(f'Property "MoveableNumber" of "MoveableSetupRequest" is not integer value.')

        if self.moveable_type is None:
            raise ValueError(f'Property "MoveableType" of "MoveableSetupRequest" is None.')

        if not isinstance(self.moveable_type, MoveableType):
            raise ValueError(f'Property "MoveableType" of "MoveableSetupRequest" is not an instance of "MoveableType".')

        if self.default_units is not None:
            if not isinstance(self.default_units, DefaultMotionUnits):
                raise ValueError(f'Property "DefaultUnits" of "MoveableSetupRequest" is not an instance of "DefaultMotionUnits".')

            self.default_units.validate()
