# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class OpenInterfaceResponse:

    interface_id: int = 0

    @staticmethod
    def zero_values() -> 'OpenInterfaceResponse':
        return OpenInterfaceResponse(
            interface_id=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OpenInterfaceResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OpenInterfaceResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OpenInterfaceResponse':
        return OpenInterfaceResponse(
            interface_id=data.get('interfaceId'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "OpenInterfaceResponse" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "OpenInterfaceResponse" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "OpenInterfaceResponse" is not integer value.')
