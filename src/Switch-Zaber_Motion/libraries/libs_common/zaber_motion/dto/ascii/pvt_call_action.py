# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class PvtCallAction:
    """
    Represents a buffer call in a PVT sequence or buffer.
    """

    buffer_number: int
    """
    The number of the buffer to call. A buffer with this number must exist on the device when the call is made.
    """

    @staticmethod
    def zero_values() -> 'PvtCallAction':
        return PvtCallAction(
            buffer_number=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtCallAction':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtCallAction.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bufferNumber': int(self.buffer_number),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtCallAction':
        return PvtCallAction(
            buffer_number=data.get('bufferNumber'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.buffer_number is None:
            raise ValueError(f'Property "BufferNumber" of "PvtCallAction" is None.')

        if not isinstance(self.buffer_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "BufferNumber" of "PvtCallAction" is not a number.')

        if int(self.buffer_number) != self.buffer_number:
            raise ValueError(f'Property "BufferNumber" of "PvtCallAction" is not integer value.')
