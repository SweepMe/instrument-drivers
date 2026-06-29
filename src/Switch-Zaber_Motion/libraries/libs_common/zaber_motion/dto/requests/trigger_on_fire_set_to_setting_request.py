# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.trigger_action import TriggerAction
from ..ascii.trigger_operation import TriggerOperation


@dataclass
class TriggerOnFireSetToSettingRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    action: TriggerAction = next(first for first in TriggerAction)

    axis: int = 0

    setting: str = ""

    operation: TriggerOperation = next(first for first in TriggerOperation)

    from_axis: int = 0

    from_setting: str = ""

    @staticmethod
    def zero_values() -> 'TriggerOnFireSetToSettingRequest':
        return TriggerOnFireSetToSettingRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            action=next(first for first in TriggerAction),
            axis=0,
            setting="",
            operation=next(first for first in TriggerOperation),
            from_axis=0,
            from_setting="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerOnFireSetToSettingRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerOnFireSetToSettingRequest.from_dict(data)

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
            'fromAxis': int(self.from_axis),
            'fromSetting': str(self.from_setting or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerOnFireSetToSettingRequest':
        return TriggerOnFireSetToSettingRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            action=TriggerAction(data.get('action')),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            setting=data.get('setting'),  # type: ignore
            operation=TriggerOperation(data.get('operation')),  # type: ignore
            from_axis=data.get('fromAxis'),  # type: ignore
            from_setting=data.get('fromSetting'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetToSettingRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerOnFireSetToSettingRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerOnFireSetToSettingRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerOnFireSetToSettingRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetToSettingRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerOnFireSetToSettingRequest" is not integer value.')

        if self.action is None:
            raise ValueError(f'Property "Action" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.action, TriggerAction):
            raise ValueError(f'Property "Action" of "TriggerOnFireSetToSettingRequest" is not an instance of "TriggerAction".')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetToSettingRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "TriggerOnFireSetToSettingRequest" is not integer value.')

        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "TriggerOnFireSetToSettingRequest" is not a string.')

        if self.operation is None:
            raise ValueError(f'Property "Operation" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.operation, TriggerOperation):
            raise ValueError(f'Property "Operation" of "TriggerOnFireSetToSettingRequest" is not an instance of "TriggerOperation".')

        if self.from_axis is None:
            raise ValueError(f'Property "FromAxis" of "TriggerOnFireSetToSettingRequest" is None.')

        if not isinstance(self.from_axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FromAxis" of "TriggerOnFireSetToSettingRequest" is not a number.')

        if int(self.from_axis) != self.from_axis:
            raise ValueError(f'Property "FromAxis" of "TriggerOnFireSetToSettingRequest" is not integer value.')

        if self.from_setting is not None:
            if not isinstance(self.from_setting, str):
                raise ValueError(f'Property "FromSetting" of "TriggerOnFireSetToSettingRequest" is not a string.')
