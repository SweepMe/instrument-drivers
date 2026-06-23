# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class LockstepWaitUntilIdleRequest:

    interface_id: int = 0

    device: int = 0

    lockstep_group_id: int = 0

    throw_error_on_fault: bool = False

    @staticmethod
    def zero_values() -> 'LockstepWaitUntilIdleRequest':
        return LockstepWaitUntilIdleRequest(
            interface_id=0,
            device=0,
            lockstep_group_id=0,
            throw_error_on_fault=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepWaitUntilIdleRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepWaitUntilIdleRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'lockstepGroupId': int(self.lockstep_group_id),
            'throwErrorOnFault': bool(self.throw_error_on_fault),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepWaitUntilIdleRequest':
        return LockstepWaitUntilIdleRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            lockstep_group_id=data.get('lockstepGroupId'),  # type: ignore
            throw_error_on_fault=data.get('throwErrorOnFault'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LockstepWaitUntilIdleRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LockstepWaitUntilIdleRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LockstepWaitUntilIdleRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LockstepWaitUntilIdleRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LockstepWaitUntilIdleRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LockstepWaitUntilIdleRequest" is not integer value.')

        if self.lockstep_group_id is None:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepWaitUntilIdleRequest" is None.')

        if not isinstance(self.lockstep_group_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LockstepGroupId" of "LockstepWaitUntilIdleRequest" is not a number.')

        if int(self.lockstep_group_id) != self.lockstep_group_id:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepWaitUntilIdleRequest" is not integer value.')
