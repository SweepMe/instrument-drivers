# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class AutofocusStatus:
    """
    Status of the autofocus.
    """

    in_focus: bool
    """
    Indicates whether the autofocus is in focus.
    """

    in_range: bool
    """
    Indicates whether the autofocus is in range.
    """

    @staticmethod
    def zero_values() -> 'AutofocusStatus':
        return AutofocusStatus(
            in_focus=False,
            in_range=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AutofocusStatus':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AutofocusStatus.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'inFocus': bool(self.in_focus),
            'inRange': bool(self.in_range),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AutofocusStatus':
        return AutofocusStatus(
            in_focus=data.get('inFocus'),  # type: ignore
            in_range=data.get('inRange'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        pass
