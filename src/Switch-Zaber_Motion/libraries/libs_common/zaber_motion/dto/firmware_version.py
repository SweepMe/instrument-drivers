# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class FirmwareVersion:
    """
    Class representing version of firmware in the controller.
    """

    major: int
    """
    Major version number.
    """

    minor: int
    """
    Minor version number.
    """

    build: int
    """
    Build version number.
    """

    @staticmethod
    def zero_values() -> 'FirmwareVersion':
        return FirmwareVersion(
            major=0,
            minor=0,
            build=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'FirmwareVersion':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return FirmwareVersion.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'major': int(self.major),
            'minor': int(self.minor),
            'build': int(self.build),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FirmwareVersion':
        return FirmwareVersion(
            major=data.get('major'),  # type: ignore
            minor=data.get('minor'),  # type: ignore
            build=data.get('build'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.major is None:
            raise ValueError(f'Property "Major" of "FirmwareVersion" is None.')

        if not isinstance(self.major, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Major" of "FirmwareVersion" is not a number.')

        if int(self.major) != self.major:
            raise ValueError(f'Property "Major" of "FirmwareVersion" is not integer value.')

        if self.minor is None:
            raise ValueError(f'Property "Minor" of "FirmwareVersion" is None.')

        if not isinstance(self.minor, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Minor" of "FirmwareVersion" is not a number.')

        if int(self.minor) != self.minor:
            raise ValueError(f'Property "Minor" of "FirmwareVersion" is not integer value.')

        if self.build is None:
            raise ValueError(f'Property "Build" of "FirmwareVersion" is None.')

        if not isinstance(self.build, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Build" of "FirmwareVersion" is not a number.')

        if int(self.build) != self.build:
            raise ValueError(f'Property "Build" of "FirmwareVersion" is not integer value.')
