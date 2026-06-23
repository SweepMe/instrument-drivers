# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.alert_event import AlertEvent


@dataclass
class AlertEventWrapper:

    interface_id: int = 0

    session_id: int = 0
    """
    The id of the connection session.
    """

    alert: AlertEvent = field(default_factory=AlertEvent.zero_values)

    @staticmethod
    def zero_values() -> 'AlertEventWrapper':
        return AlertEventWrapper(
            interface_id=0,
            session_id=0,
            alert=AlertEvent.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AlertEventWrapper':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AlertEventWrapper.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'sessionId': int(self.session_id),
            'alert': self.alert.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AlertEventWrapper':
        return AlertEventWrapper(
            interface_id=data.get('interfaceId'),  # type: ignore
            session_id=data.get('sessionId'),  # type: ignore
            alert=AlertEvent.from_dict(data.get('alert')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "AlertEventWrapper" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "AlertEventWrapper" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "AlertEventWrapper" is not integer value.')

        if self.session_id is None:
            raise ValueError(f'Property "SessionId" of "AlertEventWrapper" is None.')

        if not isinstance(self.session_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "SessionId" of "AlertEventWrapper" is not a number.')

        if int(self.session_id) != self.session_id:
            raise ValueError(f'Property "SessionId" of "AlertEventWrapper" is not integer value.')

        if self.alert is None:
            raise ValueError(f'Property "Alert" of "AlertEventWrapper" is None.')

        if not isinstance(self.alert, AlertEvent):
            raise ValueError(f'Property "Alert" of "AlertEventWrapper" is not an instance of "AlertEvent".')

        self.alert.validate()
