# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import zaber_bson


@dataclass
class ToggleDeviceDbStoreRequest:

    toggle_on: bool = False

    store_location: Optional[str] = None

    @staticmethod
    def zero_values() -> 'ToggleDeviceDbStoreRequest':
        return ToggleDeviceDbStoreRequest(
            toggle_on=False,
            store_location=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ToggleDeviceDbStoreRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ToggleDeviceDbStoreRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'toggleOn': bool(self.toggle_on),
            'storeLocation': str(self.store_location) if self.store_location is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ToggleDeviceDbStoreRequest':
        return ToggleDeviceDbStoreRequest(
            toggle_on=data.get('toggleOn'),  # type: ignore
            store_location=data.get('storeLocation'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.store_location is not None:
            if not isinstance(self.store_location, str):
                raise ValueError(f'Property "StoreLocation" of "ToggleDeviceDbStoreRequest" is not a string.')
