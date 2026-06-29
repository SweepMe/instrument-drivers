# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class ThirdPartyComponents:
    """
    Third party components of the microscope.
    """

    autofocus: Optional[int] = None
    """
    Autofocus provider identifier.
    """

    @staticmethod
    def zero_values() -> 'ThirdPartyComponents':
        return ThirdPartyComponents(
            autofocus=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ThirdPartyComponents':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ThirdPartyComponents.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'autofocus': int(self.autofocus) if self.autofocus is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ThirdPartyComponents':
        return ThirdPartyComponents(
            autofocus=data.get('autofocus'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.autofocus is not None:
            if not isinstance(self.autofocus, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Autofocus" of "ThirdPartyComponents" is not a number.')

            if int(self.autofocus) != self.autofocus:
                raise ValueError(f'Property "Autofocus" of "ThirdPartyComponents" is not integer value.')
