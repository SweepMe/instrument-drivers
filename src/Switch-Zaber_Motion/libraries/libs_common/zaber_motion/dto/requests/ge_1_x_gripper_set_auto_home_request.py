# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class Ge1xGripperSetAutoHomeRequest:

    connection_id: int = 0

    enabled: bool = False

    save_to_flash: bool = False

    @staticmethod
    def zero_values() -> 'Ge1xGripperSetAutoHomeRequest':
        return Ge1xGripperSetAutoHomeRequest(
            connection_id=0,
            enabled=False,
            save_to_flash=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperSetAutoHomeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperSetAutoHomeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'connectionId': int(self.connection_id),
            'enabled': bool(self.enabled),
            'saveToFlash': bool(self.save_to_flash),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperSetAutoHomeRequest':
        return Ge1xGripperSetAutoHomeRequest(
            connection_id=data.get('connectionId'),  # type: ignore
            enabled=data.get('enabled'),  # type: ignore
            save_to_flash=data.get('saveToFlash'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.connection_id is None:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetAutoHomeRequest" is None.')

        if not isinstance(self.connection_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetAutoHomeRequest" is not a number.')

        if int(self.connection_id) != self.connection_id:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetAutoHomeRequest" is not integer value.')
