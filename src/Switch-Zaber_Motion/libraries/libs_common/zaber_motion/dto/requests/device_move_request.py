# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from .axis_move_type import AxisMoveType
from ..cyclic_direction import CyclicDirection
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DeviceMoveRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    wait_until_idle: bool = False

    type: AxisMoveType = next(first for first in AxisMoveType)

    arg: float = 0

    arg_int: int = 0

    unit: UnitsAndLiterals = Units.NATIVE

    velocity: float = 0

    velocity_unit: UnitsAndLiterals = Units.NATIVE

    acceleration: float = 0

    acceleration_unit: UnitsAndLiterals = Units.NATIVE

    cyclic_direction: Optional[CyclicDirection] = None

    extra_cycles: Optional[int] = None

    @staticmethod
    def zero_values() -> 'DeviceMoveRequest':
        return DeviceMoveRequest(
            interface_id=0,
            device=0,
            axis=0,
            wait_until_idle=False,
            type=next(first for first in AxisMoveType),
            arg=0,
            arg_int=0,
            unit=Units.NATIVE,
            velocity=0,
            velocity_unit=Units.NATIVE,
            acceleration=0,
            acceleration_unit=Units.NATIVE,
            cyclic_direction=None,
            extra_cycles=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceMoveRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceMoveRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'waitUntilIdle': bool(self.wait_until_idle),
            'type': self.type.value,
            'arg': float(self.arg),
            'argInt': int(self.arg_int),
            'unit': units_from_literals(self.unit).value,
            'velocity': float(self.velocity),
            'velocityUnit': units_from_literals(self.velocity_unit).value,
            'acceleration': float(self.acceleration),
            'accelerationUnit': units_from_literals(self.acceleration_unit).value,
            'cyclicDirection': self.cyclic_direction.value if self.cyclic_direction is not None else None,
            'extraCycles': int(self.extra_cycles) if self.extra_cycles is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceMoveRequest':
        return DeviceMoveRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            wait_until_idle=data.get('waitUntilIdle'),  # type: ignore
            type=AxisMoveType(data.get('type')),  # type: ignore
            arg=data.get('arg'),  # type: ignore
            arg_int=data.get('argInt'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            velocity=data.get('velocity'),  # type: ignore
            velocity_unit=Units(data.get('velocityUnit')),  # type: ignore
            acceleration=data.get('acceleration'),  # type: ignore
            acceleration_unit=Units(data.get('accelerationUnit')),  # type: ignore
            cyclic_direction=CyclicDirection(data.get('cyclicDirection')) if data.get('cyclicDirection') is not None else None,  # type: ignore
            extra_cycles=data.get('extraCycles'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceMoveRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceMoveRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceMoveRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceMoveRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceMoveRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceMoveRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceMoveRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceMoveRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceMoveRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "DeviceMoveRequest" is None.')

        if not isinstance(self.type, AxisMoveType):
            raise ValueError(f'Property "Type" of "DeviceMoveRequest" is not an instance of "AxisMoveType".')

        if self.arg is None:
            raise ValueError(f'Property "Arg" of "DeviceMoveRequest" is None.')

        if not isinstance(self.arg, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Arg" of "DeviceMoveRequest" is not a number.')

        if self.arg_int is None:
            raise ValueError(f'Property "ArgInt" of "DeviceMoveRequest" is None.')

        if not isinstance(self.arg_int, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ArgInt" of "DeviceMoveRequest" is not a number.')

        if int(self.arg_int) != self.arg_int:
            raise ValueError(f'Property "ArgInt" of "DeviceMoveRequest" is not integer value.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "DeviceMoveRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "DeviceMoveRequest" is not Units.')

        if self.velocity is None:
            raise ValueError(f'Property "Velocity" of "DeviceMoveRequest" is None.')

        if not isinstance(self.velocity, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Velocity" of "DeviceMoveRequest" is not a number.')

        if self.velocity_unit is None:
            raise ValueError(f'Property "VelocityUnit" of "DeviceMoveRequest" is None.')

        if not isinstance(self.velocity_unit, (Units, str)):
            raise ValueError(f'Property "VelocityUnit" of "DeviceMoveRequest" is not Units.')

        if self.acceleration is None:
            raise ValueError(f'Property "Acceleration" of "DeviceMoveRequest" is None.')

        if not isinstance(self.acceleration, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Acceleration" of "DeviceMoveRequest" is not a number.')

        if self.acceleration_unit is None:
            raise ValueError(f'Property "AccelerationUnit" of "DeviceMoveRequest" is None.')

        if not isinstance(self.acceleration_unit, (Units, str)):
            raise ValueError(f'Property "AccelerationUnit" of "DeviceMoveRequest" is not Units.')

        if self.cyclic_direction is not None:
            if not isinstance(self.cyclic_direction, CyclicDirection):
                raise ValueError(f'Property "CyclicDirection" of "DeviceMoveRequest" is not an instance of "CyclicDirection".')

        if self.extra_cycles is not None:
            if not isinstance(self.extra_cycles, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "ExtraCycles" of "DeviceMoveRequest" is not a number.')

            if int(self.extra_cycles) != self.extra_cycles:
                raise ValueError(f'Property "ExtraCycles" of "DeviceMoveRequest" is not integer value.')
