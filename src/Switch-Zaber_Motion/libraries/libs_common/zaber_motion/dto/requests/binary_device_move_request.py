# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .axis_move_type import AxisMoveType
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class BinaryDeviceMoveRequest:

    interface_id: int = 0

    device: int = 0

    timeout: float = 0

    type: AxisMoveType = next(first for first in AxisMoveType)

    arg: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'BinaryDeviceMoveRequest':
        return BinaryDeviceMoveRequest(
            interface_id=0,
            device=0,
            timeout=0,
            type=next(first for first in AxisMoveType),
            arg=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BinaryDeviceMoveRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BinaryDeviceMoveRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'timeout': float(self.timeout),
            'type': self.type.value,
            'arg': float(self.arg),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BinaryDeviceMoveRequest':
        return BinaryDeviceMoveRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
            type=AxisMoveType(data.get('type')),  # type: ignore
            arg=data.get('arg'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "BinaryDeviceMoveRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "BinaryDeviceMoveRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "BinaryDeviceMoveRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "BinaryDeviceMoveRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "BinaryDeviceMoveRequest" is not a number.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.type, AxisMoveType):
            raise ValueError(f'Property "Type" of "BinaryDeviceMoveRequest" is not an instance of "AxisMoveType".')

        if self.arg is None:
            raise ValueError(f'Property "Arg" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.arg, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Arg" of "BinaryDeviceMoveRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "BinaryDeviceMoveRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "BinaryDeviceMoveRequest" is not Units.')
