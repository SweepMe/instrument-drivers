# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from .response_type import ResponseType
from .errors import Errors


@dataclass
class GatewayResponse:

    response: ResponseType = next(first for first in ResponseType)

    error_type: Errors = next(first for first in Errors)

    error_message: str = ""

    @staticmethod
    def zero_values() -> 'GatewayResponse':
        return GatewayResponse(
            response=next(first for first in ResponseType),
            error_type=next(first for first in Errors),
            error_message="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GatewayResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GatewayResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'response': self.response.value,
            'errorType': self.error_type.value,
            'errorMessage': str(self.error_message or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GatewayResponse':
        return GatewayResponse(
            response=ResponseType(data.get('response')),  # type: ignore
            error_type=Errors(data.get('errorType')),  # type: ignore
            error_message=data.get('errorMessage'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.response is None:
            raise ValueError(f'Property "Response" of "GatewayResponse" is None.')

        if not isinstance(self.response, ResponseType):
            raise ValueError(f'Property "Response" of "GatewayResponse" is not an instance of "ResponseType".')

        if self.error_type is None:
            raise ValueError(f'Property "ErrorType" of "GatewayResponse" is None.')

        if not isinstance(self.error_type, Errors):
            raise ValueError(f'Property "ErrorType" of "GatewayResponse" is not an instance of "Errors".')

        if self.error_message is not None:
            if not isinstance(self.error_message, str):
                raise ValueError(f'Property "ErrorMessage" of "GatewayResponse" is not a string.')
