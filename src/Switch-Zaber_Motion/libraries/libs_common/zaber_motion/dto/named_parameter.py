# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class NamedParameter:
    """
    Named parameter with optional value.
    """

    name: str
    """
    Name of the parameter.
    """

    value: Optional[float] = None
    """
    Optional value of the parameter.
    """

    @staticmethod
    def zero_values() -> 'NamedParameter':
        return NamedParameter(
            name="",
            value=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'NamedParameter':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return NamedParameter.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': str(self.name or ''),
            'value': float(self.value) if self.value is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'NamedParameter':
        return NamedParameter(
            name=data.get('name'),  # type: ignore
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.name is not None:
            if not isinstance(self.name, str):
                raise ValueError(f'Property "Name" of "NamedParameter" is not a string.')

        if self.value is not None:
            if not isinstance(self.value, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Value" of "NamedParameter" is not a number.')
