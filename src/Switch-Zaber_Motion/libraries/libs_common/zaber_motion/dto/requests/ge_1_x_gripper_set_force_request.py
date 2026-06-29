# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class Ge1xGripperSetForceRequest:

    connection_id: int = 0

    force: int = 0

    @staticmethod
    def zero_values() -> 'Ge1xGripperSetForceRequest':
        return Ge1xGripperSetForceRequest(
            connection_id=0,
            force=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperSetForceRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperSetForceRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'connectionId': int(self.connection_id),
            'force': int(self.force),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperSetForceRequest':
        return Ge1xGripperSetForceRequest(
            connection_id=data.get('connectionId'),  # type: ignore
            force=data.get('force'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.connection_id is None:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetForceRequest" is None.')

        if not isinstance(self.connection_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetForceRequest" is not a number.')

        if int(self.connection_id) != self.connection_id:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetForceRequest" is not integer value.')

        if self.force is None:
            raise ValueError(f'Property "Force" of "Ge1xGripperSetForceRequest" is None.')

        if not isinstance(self.force, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Force" of "Ge1xGripperSetForceRequest" is not a number.')

        if int(self.force) != self.force:
            raise ValueError(f'Property "Force" of "Ge1xGripperSetForceRequest" is not integer value.')
