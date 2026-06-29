# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ..product.ge_1_x_gripper_state import Ge1xGripperState


@dataclass
class Ge1xGripperGetStateResponse:

    value: Ge1xGripperState = next(first for first in Ge1xGripperState)

    @staticmethod
    def zero_values() -> 'Ge1xGripperGetStateResponse':
        return Ge1xGripperGetStateResponse(
            value=next(first for first in Ge1xGripperState),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperGetStateResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperGetStateResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperGetStateResponse':
        return Ge1xGripperGetStateResponse(
            value=Ge1xGripperState(data.get('value')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "Ge1xGripperGetStateResponse" is None.')

        if not isinstance(self.value, Ge1xGripperState):
            raise ValueError(f'Property "Value" of "Ge1xGripperGetStateResponse" is not an instance of "Ge1xGripperState".')
