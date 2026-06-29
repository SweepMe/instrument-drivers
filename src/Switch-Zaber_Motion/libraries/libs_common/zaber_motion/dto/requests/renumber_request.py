# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class RenumberRequest:

    interface_id: int = 0

    device: int = 0

    address: int = 0

    @staticmethod
    def zero_values() -> 'RenumberRequest':
        return RenumberRequest(
            interface_id=0,
            device=0,
            address=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'RenumberRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return RenumberRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'address': int(self.address),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RenumberRequest':
        return RenumberRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            address=data.get('address'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "RenumberRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "RenumberRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "RenumberRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "RenumberRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "RenumberRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "RenumberRequest" is not integer value.')

        if self.address is None:
            raise ValueError(f'Property "Address" of "RenumberRequest" is None.')

        if not isinstance(self.address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Address" of "RenumberRequest" is not a number.')

        if int(self.address) != self.address:
            raise ValueError(f'Property "Address" of "RenumberRequest" is not integer value.')
