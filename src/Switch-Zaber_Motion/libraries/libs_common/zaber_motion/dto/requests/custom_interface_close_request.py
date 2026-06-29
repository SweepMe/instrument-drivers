# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class CustomInterfaceCloseRequest:

    transport_id: int = 0

    error_message: str = ""

    @staticmethod
    def zero_values() -> 'CustomInterfaceCloseRequest':
        return CustomInterfaceCloseRequest(
            transport_id=0,
            error_message="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CustomInterfaceCloseRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CustomInterfaceCloseRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transportId': int(self.transport_id),
            'errorMessage': str(self.error_message or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CustomInterfaceCloseRequest':
        return CustomInterfaceCloseRequest(
            transport_id=data.get('transportId'),  # type: ignore
            error_message=data.get('errorMessage'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.transport_id is None:
            raise ValueError(f'Property "TransportId" of "CustomInterfaceCloseRequest" is None.')

        if not isinstance(self.transport_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TransportId" of "CustomInterfaceCloseRequest" is not a number.')

        if int(self.transport_id) != self.transport_id:
            raise ValueError(f'Property "TransportId" of "CustomInterfaceCloseRequest" is not integer value.')

        if self.error_message is not None:
            if not isinstance(self.error_message, str):
                raise ValueError(f'Property "ErrorMessage" of "CustomInterfaceCloseRequest" is not a string.')
