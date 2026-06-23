# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class InvalidPacketExceptionData:
    """
    Contains additional data for the InvalidPacketException.
    """

    packet: str
    """
    The invalid packet that caused the exception.
    """

    reason: str
    """
    The reason for the exception.
    """

    @staticmethod
    def zero_values() -> 'InvalidPacketExceptionData':
        return InvalidPacketExceptionData(
            packet="",
            reason="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'InvalidPacketExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return InvalidPacketExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'packet': str(self.packet or ''),
            'reason': str(self.reason or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'InvalidPacketExceptionData':
        return InvalidPacketExceptionData(
            packet=data.get('packet'),  # type: ignore
            reason=data.get('reason'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.packet is not None:
            if not isinstance(self.packet, str):
                raise ValueError(f'Property "Packet" of "InvalidPacketExceptionData" is not a string.')

        if self.reason is not None:
            if not isinstance(self.reason, str):
                raise ValueError(f'Property "Reason" of "InvalidPacketExceptionData" is not a string.')
