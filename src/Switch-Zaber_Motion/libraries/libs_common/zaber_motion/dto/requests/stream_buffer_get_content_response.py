# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson


@dataclass
class StreamBufferGetContentResponse:

    buffer_lines: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamBufferGetContentResponse':
        return StreamBufferGetContentResponse(
            buffer_lines=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamBufferGetContentResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamBufferGetContentResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bufferLines': [str(item or '') for item in self.buffer_lines] if self.buffer_lines is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamBufferGetContentResponse':
        return StreamBufferGetContentResponse(
            buffer_lines=data.get('bufferLines'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.buffer_lines is not None:
            if not isinstance(self.buffer_lines, Iterable):
                raise ValueError('Property "BufferLines" of "StreamBufferGetContentResponse" is not iterable.')

            for i, buffer_lines_item in enumerate(self.buffer_lines):
                if buffer_lines_item is not None:
                    if not isinstance(buffer_lines_item, str):
                        raise ValueError(f'Item {i} in property "BufferLines" of "StreamBufferGetContentResponse" is not a string.')
