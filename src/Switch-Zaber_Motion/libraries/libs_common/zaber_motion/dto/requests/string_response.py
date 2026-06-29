# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class StringResponse:

    value: str = ""

    @staticmethod
    def zero_values() -> 'StringResponse':
        return StringResponse(
            value="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StringResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StringResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': str(self.value or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StringResponse':
        return StringResponse(
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.value is not None:
            if not isinstance(self.value, str):
                raise ValueError(f'Property "Value" of "StringResponse" is not a string.')
