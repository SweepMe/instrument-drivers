# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import decimal
import zaber_bson
from ..binary.unknown_response_event import UnknownResponseEvent


@dataclass
class UnknownBinaryResponseEventWrapper:

    interface_id: int = 0

    session_id: int = 0
    """
    The id of the connection session.
    """

    unknown_response: UnknownResponseEvent = field(default_factory=UnknownResponseEvent.zero_values)

    @staticmethod
    def zero_values() -> 'UnknownBinaryResponseEventWrapper':
        return UnknownBinaryResponseEventWrapper(
            interface_id=0,
            session_id=0,
            unknown_response=UnknownResponseEvent.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnknownBinaryResponseEventWrapper':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnknownBinaryResponseEventWrapper.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'sessionId': int(self.session_id),
            'unknownResponse': self.unknown_response.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnknownBinaryResponseEventWrapper':
        return UnknownBinaryResponseEventWrapper(
            interface_id=data.get('interfaceId'),  # type: ignore
            session_id=data.get('sessionId'),  # type: ignore
            unknown_response=UnknownResponseEvent.from_dict(data.get('unknownResponse')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "UnknownBinaryResponseEventWrapper" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "UnknownBinaryResponseEventWrapper" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "UnknownBinaryResponseEventWrapper" is not integer value.')

        if self.session_id is None:
            raise ValueError(f'Property "SessionId" of "UnknownBinaryResponseEventWrapper" is None.')

        if not isinstance(self.session_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "SessionId" of "UnknownBinaryResponseEventWrapper" is not a number.')

        if int(self.session_id) != self.session_id:
            raise ValueError(f'Property "SessionId" of "UnknownBinaryResponseEventWrapper" is not integer value.')

        if self.unknown_response is None:
            raise ValueError(f'Property "UnknownResponse" of "UnknownBinaryResponseEventWrapper" is None.')

        if not isinstance(self.unknown_response, UnknownResponseEvent):
            raise ValueError(f'Property "UnknownResponse" of "UnknownBinaryResponseEventWrapper" is not an instance of "UnknownResponseEvent".')

        self.unknown_response.validate()
