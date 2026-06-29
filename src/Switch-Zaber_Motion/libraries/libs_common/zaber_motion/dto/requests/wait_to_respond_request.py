# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class WaitToRespondRequest:

    interface_id: int = 0

    device: int = 0

    timeout: float = 0

    @staticmethod
    def zero_values() -> 'WaitToRespondRequest':
        return WaitToRespondRequest(
            interface_id=0,
            device=0,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'WaitToRespondRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return WaitToRespondRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'timeout': float(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WaitToRespondRequest':
        return WaitToRespondRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "WaitToRespondRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "WaitToRespondRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "WaitToRespondRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "WaitToRespondRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "WaitToRespondRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "WaitToRespondRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "WaitToRespondRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "WaitToRespondRequest" is not a number.')
