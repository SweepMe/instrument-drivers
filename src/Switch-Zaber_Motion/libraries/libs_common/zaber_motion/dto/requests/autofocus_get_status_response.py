# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import zaber_bson
from ..microscopy.autofocus_status import AutofocusStatus


@dataclass
class AutofocusGetStatusResponse:

    status: AutofocusStatus = field(default_factory=AutofocusStatus.zero_values)

    @staticmethod
    def zero_values() -> 'AutofocusGetStatusResponse':
        return AutofocusGetStatusResponse(
            status=AutofocusStatus.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AutofocusGetStatusResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AutofocusGetStatusResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AutofocusGetStatusResponse':
        return AutofocusGetStatusResponse(
            status=AutofocusStatus.from_dict(data.get('status')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.status is None:
            raise ValueError(f'Property "Status" of "AutofocusGetStatusResponse" is None.')

        if not isinstance(self.status, AutofocusStatus):
            raise ValueError(f'Property "Status" of "AutofocusGetStatusResponse" is not an instance of "AutofocusStatus".')

        self.status.validate()
