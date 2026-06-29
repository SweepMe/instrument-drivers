# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class UnitGetEnumRequest:

    symbol: str = ""

    @staticmethod
    def zero_values() -> 'UnitGetEnumRequest':
        return UnitGetEnumRequest(
            symbol="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnitGetEnumRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnitGetEnumRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': str(self.symbol or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnitGetEnumRequest':
        return UnitGetEnumRequest(
            symbol=data.get('symbol'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.symbol is not None:
            if not isinstance(self.symbol, str):
                raise ValueError(f'Property "Symbol" of "UnitGetEnumRequest" is not a string.')
