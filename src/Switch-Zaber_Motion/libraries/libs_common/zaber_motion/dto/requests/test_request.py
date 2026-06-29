# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class TestRequest:

    return_error: bool = False

    data_ping: str = ""

    return_error_with_data: bool = False

    @staticmethod
    def zero_values() -> 'TestRequest':
        return TestRequest(
            return_error=False,
            data_ping="",
            return_error_with_data=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TestRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TestRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'returnError': bool(self.return_error),
            'dataPing': str(self.data_ping or ''),
            'returnErrorWithData': bool(self.return_error_with_data),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestRequest':
        return TestRequest(
            return_error=data.get('returnError'),  # type: ignore
            data_ping=data.get('dataPing'),  # type: ignore
            return_error_with_data=data.get('returnErrorWithData'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_ping is not None:
            if not isinstance(self.data_ping, str):
                raise ValueError(f'Property "DataPing" of "TestRequest" is not a string.')
