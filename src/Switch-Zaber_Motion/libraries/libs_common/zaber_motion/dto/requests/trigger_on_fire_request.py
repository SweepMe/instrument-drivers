# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.trigger_action import TriggerAction


@dataclass
class TriggerOnFireRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    action: TriggerAction = next(first for first in TriggerAction)

    axis: int = 0

    command: str = ""

    @staticmethod
    def zero_values() -> 'TriggerOnFireRequest':
        return TriggerOnFireRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            action=next(first for first in TriggerAction),
            axis=0,
            command="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerOnFireRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerOnFireRequest.from_dict(data)

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
            'command': str(self.command or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerOnFireRequest':
        return TriggerOnFireRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            action=TriggerAction(data.get('action')),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            command=data.get('command'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerOnFireRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerOnFireRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerOnFireRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireRequest" is not integer value.')

        if self.action is None:
            raise ValueError(f'Property "Action" of "TriggerOnFireRequest" is None.')

        if not isinstance(self.action, TriggerAction):
            raise ValueError(f'Property "Action" of "TriggerOnFireRequest" is not an instance of "TriggerAction".')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "TriggerOnFireRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "TriggerOnFireRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "TriggerOnFireRequest" is not integer value.')

        if self.command is not None:
            if not isinstance(self.command, str):
                raise ValueError(f'Property "Command" of "TriggerOnFireRequest" is not a string.')
