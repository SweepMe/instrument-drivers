# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class Ge1xGripperEmptyRequest:

    connection_id: int = 0

    @staticmethod
    def zero_values() -> 'Ge1xGripperEmptyRequest':
        return Ge1xGripperEmptyRequest(
            connection_id=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperEmptyRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperEmptyRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'connectionId': int(self.connection_id),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperEmptyRequest':
        return Ge1xGripperEmptyRequest(
            connection_id=data.get('connectionId'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.connection_id is None:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperEmptyRequest" is None.')

        if not isinstance(self.connection_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperEmptyRequest" is not a number.')

        if int(self.connection_id) != self.connection_id:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperEmptyRequest" is not integer value.')
