# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .message_type import MessageType


@dataclass
class UnknownResponseEvent:
    """
    Reply that could not be matched to a request.
    """

    device_address: int
    """
    Number of the device that sent the message.
    """

    axis_number: int
    """
    Number of the axis which the response applies to. Zero denotes device scope.
    """

    reply_flag: str
    """
    The reply flag indicates if the request was accepted (OK) or rejected (RJ).
    Does not apply to info messages.
    """

    status: str
    """
    The device status contains BUSY when the axis is moving and IDLE otherwise.
    Does not apply to info messages.
    """

    warning_flag: str
    """
    The warning flag contains the highest priority warning currently active for the device or axis.
    Does not apply to info messages.
    """

    data: str
    """
    Response data which varies depending on the request.
    """

    message_type: MessageType
    """
    Type of the response received (only Reply or Info).
    """

    @staticmethod
    def zero_values() -> 'UnknownResponseEvent':
        return UnknownResponseEvent(
            device_address=0,
            axis_number=0,
            reply_flag="",
            status="",
            warning_flag="",
            data="",
            message_type=next(first for first in MessageType),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnknownResponseEvent':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnknownResponseEvent.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceAddress': int(self.device_address),
            'axisNumber': int(self.axis_number),
            'replyFlag': str(self.reply_flag or ''),
            'status': str(self.status or ''),
            'warningFlag': str(self.warning_flag or ''),
            'data': str(self.data or ''),
            'messageType': self.message_type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnknownResponseEvent':
        return UnknownResponseEvent(
            device_address=data.get('deviceAddress'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
            reply_flag=data.get('replyFlag'),  # type: ignore
            status=data.get('status'),  # type: ignore
            warning_flag=data.get('warningFlag'),  # type: ignore
            data=data.get('data'),  # type: ignore
            message_type=MessageType(data.get('messageType')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_address is None:
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is None.')

        if not isinstance(self.device_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is not a number.')

        if int(self.device_address) != self.device_address:
            raise ValueError(f'Property "DeviceAddress" of "UnknownResponseEvent" is not integer value.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "UnknownResponseEvent" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "UnknownResponseEvent" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "UnknownResponseEvent" is not integer value.')

        if self.reply_flag is not None:
            if not isinstance(self.reply_flag, str):
                raise ValueError(f'Property "ReplyFlag" of "UnknownResponseEvent" is not a string.')

        if self.status is not None:
            if not isinstance(self.status, str):
                raise ValueError(f'Property "Status" of "UnknownResponseEvent" is not a string.')

        if self.warning_flag is not None:
            if not isinstance(self.warning_flag, str):
                raise ValueError(f'Property "WarningFlag" of "UnknownResponseEvent" is not a string.')

        if self.data is not None:
            if not isinstance(self.data, str):
                raise ValueError(f'Property "Data" of "UnknownResponseEvent" is not a string.')

        if self.message_type is None:
            raise ValueError(f'Property "MessageType" of "UnknownResponseEvent" is None.')

        if not isinstance(self.message_type, MessageType):
            raise ValueError(f'Property "MessageType" of "UnknownResponseEvent" is not an instance of "MessageType".')
