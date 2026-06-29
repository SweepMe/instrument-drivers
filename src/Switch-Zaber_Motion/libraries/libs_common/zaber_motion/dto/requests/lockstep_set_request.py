# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class LockstepSetRequest:

    interface_id: int = 0

    device: int = 0

    lockstep_group_id: int = 0

    value: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    axis_index: int = 0

    @staticmethod
    def zero_values() -> 'LockstepSetRequest':
        return LockstepSetRequest(
            interface_id=0,
            device=0,
            lockstep_group_id=0,
            value=0,
            unit=Units.NATIVE,
            axis_index=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepSetRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepSetRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'lockstepGroupId': int(self.lockstep_group_id),
            'value': float(self.value),
            'unit': units_from_literals(self.unit).value,
            'axisIndex': int(self.axis_index),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepSetRequest':
        return LockstepSetRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            lockstep_group_id=data.get('lockstepGroupId'),  # type: ignore
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            axis_index=data.get('axisIndex'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LockstepSetRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LockstepSetRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LockstepSetRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LockstepSetRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LockstepSetRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LockstepSetRequest" is not integer value.')

        if self.lockstep_group_id is None:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepSetRequest" is None.')

        if not isinstance(self.lockstep_group_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LockstepGroupId" of "LockstepSetRequest" is not a number.')

        if int(self.lockstep_group_id) != self.lockstep_group_id:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepSetRequest" is not integer value.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "LockstepSetRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "LockstepSetRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "LockstepSetRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "LockstepSetRequest" is not Units.')

        if self.axis_index is None:
            raise ValueError(f'Property "AxisIndex" of "LockstepSetRequest" is None.')

        if not isinstance(self.axis_index, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisIndex" of "LockstepSetRequest" is not a number.')

        if int(self.axis_index) != self.axis_index:
            raise ValueError(f'Property "AxisIndex" of "LockstepSetRequest" is not integer value.')
