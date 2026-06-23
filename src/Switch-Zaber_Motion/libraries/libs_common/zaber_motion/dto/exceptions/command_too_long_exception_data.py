# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class CommandTooLongExceptionData:
    """
    Information describing why the command could not fit.
    """

    fit: str
    """
    The part of the command that could be successfully fit in the space provided by the protocol.
    """

    remainder: str
    """
    The part of the command that could not fit within the space provided.
    """

    packet_size: int
    """
    The length of the ascii string that can be written to a single line.
    """

    packets_max: int
    """
    The number of lines a command can be split over using continuations.
    """

    @staticmethod
    def zero_values() -> 'CommandTooLongExceptionData':
        return CommandTooLongExceptionData(
            fit="",
            remainder="",
            packet_size=0,
            packets_max=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CommandTooLongExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CommandTooLongExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'fit': str(self.fit or ''),
            'remainder': str(self.remainder or ''),
            'packetSize': int(self.packet_size),
            'packetsMax': int(self.packets_max),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CommandTooLongExceptionData':
        return CommandTooLongExceptionData(
            fit=data.get('fit'),  # type: ignore
            remainder=data.get('remainder'),  # type: ignore
            packet_size=data.get('packetSize'),  # type: ignore
            packets_max=data.get('packetsMax'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.fit is not None:
            if not isinstance(self.fit, str):
                raise ValueError(f'Property "Fit" of "CommandTooLongExceptionData" is not a string.')

        if self.remainder is not None:
            if not isinstance(self.remainder, str):
                raise ValueError(f'Property "Remainder" of "CommandTooLongExceptionData" is not a string.')

        if self.packet_size is None:
            raise ValueError(f'Property "PacketSize" of "CommandTooLongExceptionData" is None.')

        if not isinstance(self.packet_size, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PacketSize" of "CommandTooLongExceptionData" is not a number.')

        if int(self.packet_size) != self.packet_size:
            raise ValueError(f'Property "PacketSize" of "CommandTooLongExceptionData" is not integer value.')

        if self.packets_max is None:
            raise ValueError(f'Property "PacketsMax" of "CommandTooLongExceptionData" is None.')

        if not isinstance(self.packets_max, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PacketsMax" of "CommandTooLongExceptionData" is not a number.')

        if int(self.packets_max) != self.packets_max:
            raise ValueError(f'Property "PacketsMax" of "CommandTooLongExceptionData" is not integer value.')
