# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ..product.ge_1_x_gripper_error import Ge1xGripperError


@dataclass
class Ge1xGripperGetErrorResponse:

    value: Ge1xGripperError = next(first for first in Ge1xGripperError)

    @staticmethod
    def zero_values() -> 'Ge1xGripperGetErrorResponse':
        return Ge1xGripperGetErrorResponse(
            value=next(first for first in Ge1xGripperError),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperGetErrorResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperGetErrorResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperGetErrorResponse':
        return Ge1xGripperGetErrorResponse(
            value=Ge1xGripperError(data.get('value')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is None:
            raise ValueError(f'Property "Value" of "Ge1xGripperGetErrorResponse" is None.')

        if not isinstance(self.value, Ge1xGripperError):
            raise ValueError(f'Property "Value" of "Ge1xGripperGetErrorResponse" is not an instance of "Ge1xGripperError".')
