# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.trigger_action import TriggerAction
from ..ascii.trigger_operation import TriggerOperation
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TriggerOnFireSetRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    action: TriggerAction = next(first for first in TriggerAction)

    axis: int = 0

    setting: str = ""

    operation: TriggerOperation = next(first for first in TriggerOperation)

    value: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TriggerOnFireSetRequest':
        return TriggerOnFireSetRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            action=next(first for first in TriggerAction),
            axis=0,
            setting="",
            operation=next(first for first in TriggerOperation),
            value=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerOnFireSetRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerOnFireSetRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'triggerNumber': int(self.trigger_number),
            'action': self.action.value,
            'axis': int(self.axis),
            'setting': str(self.setting or ''),
            'operation': self.operation.value,
            'value': float(self.value),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerOnFireSetRequest':
        return TriggerOnFireSetRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            action=TriggerAction(data.get('action')),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            setting=data.get('setting'),  # type: ignore
            operation=TriggerOperation(data.get('operation')),  # type: ignore
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerOnFireSetRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerOnFireSetRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetRequest" is not integer value.')

        if self.action is None:
            raise ValueError(f'Property "Action" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.action, TriggerAction):
            raise ValueError(f'Property "Action" of "TriggerOnFireSetRequest" is not an instance of "TriggerAction".')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetRequest" is not integer value.')

        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "TriggerOnFireSetRequest" is not a string.')

        if self.operation is None:
            raise ValueError(f'Property "Operation" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.operation, TriggerOperation):
            raise ValueError(f'Property "Operation" of "TriggerOnFireSetRequest" is not an instance of "TriggerOperation".')

        if self.value is None:
            raise ValueError(f'Property "Value" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "TriggerOnFireSetRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TriggerOnFireSetRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TriggerOnFireSetRequest" is not Units.')
