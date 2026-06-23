# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class SetInternalModeRequest:

    mode: bool = False

    @staticmethod
    def zero_values() -> 'SetInternalModeRequest':
        return SetInternalModeRequest(
            mode=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetInternalModeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetInternalModeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mode': bool(self.mode),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetInternalModeRequest':
        return SetInternalModeRequest(
            mode=data.get('mode'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        pass
