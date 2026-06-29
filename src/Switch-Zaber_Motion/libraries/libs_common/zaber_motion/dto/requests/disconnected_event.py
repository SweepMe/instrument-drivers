# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .errors import Errors


@dataclass
class DisconnectedEvent:
    """
    Event that is sent when a connection is lost.
    """

    interface_id: int = 0
    """
    The id of the interface that was disconnected.
    """

    session_id: int = 0
    """
    The id of the connection session.
    """

    error_type: Errors = next(first for first in Errors)
    """
    The type of error that caused the disconnection.
    """

    error_message: str = ""
    """
    The message describing the error.
    """

    @staticmethod
    def zero_values() -> 'DisconnectedEvent':
        return DisconnectedEvent(
            interface_id=0,
            session_id=0,
            error_type=next(first for first in Errors),
            error_message="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DisconnectedEvent':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DisconnectedEvent.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'sessionId': int(self.session_id),
            'errorType': self.error_type.value,
            'errorMessage': str(self.error_message or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DisconnectedEvent':
        return DisconnectedEvent(
            interface_id=data.get('interfaceId'),  # type: ignore
            session_id=data.get('sessionId'),  # type: ignore
            error_type=Errors(data.get('errorType')),  # type: ignore
            error_message=data.get('errorMessage'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DisconnectedEvent" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DisconnectedEvent" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DisconnectedEvent" is not integer value.')

        if self.session_id is None:
            raise ValueError(f'Property "SessionId" of "DisconnectedEvent" is None.')

        if not isinstance(self.session_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "SessionId" of "DisconnectedEvent" is not a number.')

        if int(self.session_id) != self.session_id:
            raise ValueError(f'Property "SessionId" of "DisconnectedEvent" is not integer value.')

        if self.error_type is None:
            raise ValueError(f'Property "ErrorType" of "DisconnectedEvent" is None.')

        if not isinstance(self.error_type, Errors):
            raise ValueError(f'Property "ErrorType" of "DisconnectedEvent" is not an instance of "Errors".')

        if self.error_message is not None:
            if not isinstance(self.error_message, str):
                raise ValueError(f'Property "ErrorMessage" of "DisconnectedEvent" is not a string.')
