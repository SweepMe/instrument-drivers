# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class LockstepEnableRequest:

    interface_id: int = 0

    device: int = 0

    lockstep_group_id: int = 0

    axes: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'LockstepEnableRequest':
        return LockstepEnableRequest(
            interface_id=0,
            device=0,
            lockstep_group_id=0,
            axes=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepEnableRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepEnableRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'lockstepGroupId': int(self.lockstep_group_id),
            'axes': [int(item) for item in self.axes] if self.axes is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepEnableRequest':
        return LockstepEnableRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            lockstep_group_id=data.get('lockstepGroupId'),  # type: ignore
            axes=data.get('axes'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LockstepEnableRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LockstepEnableRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LockstepEnableRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LockstepEnableRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LockstepEnableRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LockstepEnableRequest" is not integer value.')

        if self.lockstep_group_id is None:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepEnableRequest" is None.')

        if not isinstance(self.lockstep_group_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LockstepGroupId" of "LockstepEnableRequest" is not a number.')

        if int(self.lockstep_group_id) != self.lockstep_group_id:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepEnableRequest" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "LockstepEnableRequest" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepEnableRequest" is None.')

                if not isinstance(axes_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepEnableRequest" is not a number.')

                if int(axes_item) != axes_item:
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepEnableRequest" is not integer value.')
