# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class CheckVersionRequest:

    version: str = ""

    host: str = ""

    @staticmethod
    def zero_values() -> 'CheckVersionRequest':
        return CheckVersionRequest(
            version="",
            host="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CheckVersionRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CheckVersionRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': str(self.version or ''),
            'host': str(self.host or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CheckVersionRequest':
        return CheckVersionRequest(
            version=data.get('version'),  # type: ignore
            host=data.get('host'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.version is not None:
            if not isinstance(self.version, str):
                raise ValueError(f'Property "Version" of "CheckVersionRequest" is not a string.')

        if self.host is not None:
            if not isinstance(self.host, str):
                raise ValueError(f'Property "Host" of "CheckVersionRequest" is not a string.')
