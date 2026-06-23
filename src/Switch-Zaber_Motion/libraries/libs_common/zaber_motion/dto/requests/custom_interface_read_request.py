# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class CustomInterfaceReadRequest:

    transport_id: int = 0

    @staticmethod
    def zero_values() -> 'CustomInterfaceReadRequest':
        return CustomInterfaceReadRequest(
            transport_id=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CustomInterfaceReadRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CustomInterfaceReadRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transportId': int(self.transport_id),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CustomInterfaceReadRequest':
        return CustomInterfaceReadRequest(
            transport_id=data.get('transportId'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.transport_id is None:
            raise ValueError(f'Property "TransportId" of "CustomInterfaceReadRequest" is None.')

        if not isinstance(self.transport_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TransportId" of "CustomInterfaceReadRequest" is not a number.')

        if int(self.transport_id) != self.transport_id:
            raise ValueError(f'Property "TransportId" of "CustomInterfaceReadRequest" is not integer value.')
