# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import zaber_bson
from ..microscopy.wdi_autofocus_provider_status import WdiAutofocusProviderStatus


@dataclass
class WdiGetStatusResponse:

    status: WdiAutofocusProviderStatus = field(default_factory=WdiAutofocusProviderStatus.zero_values)

    @staticmethod
    def zero_values() -> 'WdiGetStatusResponse':
        return WdiGetStatusResponse(
            status=WdiAutofocusProviderStatus.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'WdiGetStatusResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return WdiGetStatusResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WdiGetStatusResponse':
        return WdiGetStatusResponse(
            status=WdiAutofocusProviderStatus.from_dict(data.get('status')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.status is None:
            raise ValueError(f'Property "Status" of "WdiGetStatusResponse" is None.')

        if not isinstance(self.status, WdiAutofocusProviderStatus):
            raise ValueError(f'Property "Status" of "WdiGetStatusResponse" is not an instance of "WdiAutofocusProviderStatus".')

        self.status.validate()
