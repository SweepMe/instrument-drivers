# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import zaber_bson
from ..log_output_mode import LogOutputMode


@dataclass
class SetLogOutputRequest:

    mode: LogOutputMode = next(first for first in LogOutputMode)

    file_path: Optional[str] = None

    @staticmethod
    def zero_values() -> 'SetLogOutputRequest':
        return SetLogOutputRequest(
            mode=next(first for first in LogOutputMode),
            file_path=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetLogOutputRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetLogOutputRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mode': self.mode.value,
            'filePath': str(self.file_path) if self.file_path is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetLogOutputRequest':
        return SetLogOutputRequest(
            mode=LogOutputMode(data.get('mode')),  # type: ignore
            file_path=data.get('filePath'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.mode is None:
            raise ValueError(f'Property "Mode" of "SetLogOutputRequest" is None.')

        if not isinstance(self.mode, LogOutputMode):
            raise ValueError(f'Property "Mode" of "SetLogOutputRequest" is not an instance of "LogOutputMode".')

        if self.file_path is not None:
            if not isinstance(self.file_path, str):
                raise ValueError(f'Property "FilePath" of "SetLogOutputRequest" is not a string.')
