# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class BoolResponse:

    value: bool = False

    @staticmethod
    def zero_values() -> 'BoolResponse':
        return BoolResponse(
            value=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BoolResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BoolResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': bool(self.value),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BoolResponse':
        return BoolResponse(
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        pass
