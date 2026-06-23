# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class InvalidResponseExceptionData:
    """
    Contains additional data for InvalidResponseException.
    """

    response: str
    """
    The response data.
    """

    @staticmethod
    def zero_values() -> 'InvalidResponseExceptionData':
        return InvalidResponseExceptionData(
            response="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'InvalidResponseExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return InvalidResponseExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'response': str(self.response or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'InvalidResponseExceptionData':
        return InvalidResponseExceptionData(
            response=data.get('response'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.response is not None:
            if not isinstance(self.response, str):
                raise ValueError(f'Property "Response" of "InvalidResponseExceptionData" is not a string.')
