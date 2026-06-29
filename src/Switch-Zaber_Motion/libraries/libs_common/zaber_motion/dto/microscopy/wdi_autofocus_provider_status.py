# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class WdiAutofocusProviderStatus:
    """
    Status of the WDI autofocus.
    """

    in_range: bool
    """
    Indicates whether the autofocus is in range.
    """

    laser_on: bool
    """
    Indicates whether the laser is turned on.
    """

    @staticmethod
    def zero_values() -> 'WdiAutofocusProviderStatus':
        return WdiAutofocusProviderStatus(
            in_range=False,
            laser_on=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'WdiAutofocusProviderStatus':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return WdiAutofocusProviderStatus.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'inRange': bool(self.in_range),
            'laserOn': bool(self.laser_on),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WdiAutofocusProviderStatus':
        return WdiAutofocusProviderStatus(
            in_range=data.get('inRange'),  # type: ignore
            laser_on=data.get('laserOn'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        pass
