# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ..ascii.stream_mode import StreamMode
from ..ascii.pvt_mode import PvtMode


@dataclass
class StreamModeResponse:

    stream_mode: StreamMode = next(first for first in StreamMode)

    pvt_mode: PvtMode = next(first for first in PvtMode)

    @staticmethod
    def zero_values() -> 'StreamModeResponse':
        return StreamModeResponse(
            stream_mode=next(first for first in StreamMode),
            pvt_mode=next(first for first in PvtMode),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamModeResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamModeResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'streamMode': self.stream_mode.value,
            'pvtMode': self.pvt_mode.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamModeResponse':
        return StreamModeResponse(
            stream_mode=StreamMode(data.get('streamMode')),  # type: ignore
            pvt_mode=PvtMode(data.get('pvtMode')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.stream_mode is None:
            raise ValueError(f'Property "StreamMode" of "StreamModeResponse" is None.')

        if not isinstance(self.stream_mode, StreamMode):
            raise ValueError(f'Property "StreamMode" of "StreamModeResponse" is not an instance of "StreamMode".')

        if self.pvt_mode is None:
            raise ValueError(f'Property "PvtMode" of "StreamModeResponse" is None.')

        if not isinstance(self.pvt_mode, PvtMode):
            raise ValueError(f'Property "PvtMode" of "StreamModeResponse" is not an instance of "PvtMode".')
