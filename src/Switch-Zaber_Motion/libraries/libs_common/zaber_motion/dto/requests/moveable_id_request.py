# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class MoveableIdRequest:

    moveable_id: int = 0

    @staticmethod
    def zero_values() -> 'MoveableIdRequest':
        return MoveableIdRequest(
            moveable_id=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableIdRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableIdRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'moveableId': int(self.moveable_id),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableIdRequest':
        return MoveableIdRequest(
            moveable_id=data.get('moveableId'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.moveable_id is None:
            raise ValueError(f'Property "MoveableId" of "MoveableIdRequest" is None.')

        if not isinstance(self.moveable_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableId" of "MoveableIdRequest" is not a number.')

        if int(self.moveable_id) != self.moveable_id:
            raise ValueError(f'Property "MoveableId" of "MoveableIdRequest" is not integer value.')
