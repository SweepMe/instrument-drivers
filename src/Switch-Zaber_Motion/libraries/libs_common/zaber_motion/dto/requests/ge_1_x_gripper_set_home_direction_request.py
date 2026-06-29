# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..product.ge_1_x_gripper_direction import Ge1xGripperDirection


@dataclass
class Ge1xGripperSetHomeDirectionRequest:

    connection_id: int = 0

    direction: Ge1xGripperDirection = next(first for first in Ge1xGripperDirection)

    save_to_flash: bool = False

    @staticmethod
    def zero_values() -> 'Ge1xGripperSetHomeDirectionRequest':
        return Ge1xGripperSetHomeDirectionRequest(
            connection_id=0,
            direction=next(first for first in Ge1xGripperDirection),
            save_to_flash=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperSetHomeDirectionRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperSetHomeDirectionRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'connectionId': int(self.connection_id),
            'direction': self.direction.value,
            'saveToFlash': bool(self.save_to_flash),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperSetHomeDirectionRequest':
        return Ge1xGripperSetHomeDirectionRequest(
            connection_id=data.get('connectionId'),  # type: ignore
            direction=Ge1xGripperDirection(data.get('direction')),  # type: ignore
            save_to_flash=data.get('saveToFlash'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.connection_id is None:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetHomeDirectionRequest" is None.')

        if not isinstance(self.connection_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetHomeDirectionRequest" is not a number.')

        if int(self.connection_id) != self.connection_id:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetHomeDirectionRequest" is not integer value.')

        if self.direction is None:
            raise ValueError(f'Property "Direction" of "Ge1xGripperSetHomeDirectionRequest" is None.')

        if not isinstance(self.direction, Ge1xGripperDirection):
            raise ValueError(f'Property "Direction" of "Ge1xGripperSetHomeDirectionRequest" is not an instance of "Ge1xGripperDirection".')
