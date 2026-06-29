# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class PidTuning:
    """
    The tuning of this axis represented by PID parameters.
    """

    type: str
    """
    The tuning algorithm used to tune this axis.
    """

    version: int
    """
    The version of the tuning algorithm used to tune this axis.
    """

    p: float
    """
    The positional tuning argument.
    """

    i: float
    """
    The integral tuning argument.
    """

    d: float
    """
    The derivative tuning argument.
    """

    fc: float
    """
    The frequency cutoff for the tuning.
    """

    @staticmethod
    def zero_values() -> 'PidTuning':
        return PidTuning(
            type="",
            version=0,
            p=0,
            i=0,
            d=0,
            fc=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PidTuning':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PidTuning.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': str(self.type or ''),
            'version': int(self.version),
            'p': float(self.p),
            'i': float(self.i),
            'd': float(self.d),
            'fc': float(self.fc),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PidTuning':
        return PidTuning(
            type=data.get('type'),  # type: ignore
            version=data.get('version'),  # type: ignore
            p=data.get('p'),  # type: ignore
            i=data.get('i'),  # type: ignore
            d=data.get('d'),  # type: ignore
            fc=data.get('fc'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.type is not None:
            if not isinstance(self.type, str):
                raise ValueError(f'Property "Type" of "PidTuning" is not a string.')

        if self.version is None:
            raise ValueError(f'Property "Version" of "PidTuning" is None.')

        if not isinstance(self.version, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Version" of "PidTuning" is not a number.')

        if int(self.version) != self.version:
            raise ValueError(f'Property "Version" of "PidTuning" is not integer value.')

        if self.p is None:
            raise ValueError(f'Property "P" of "PidTuning" is None.')

        if not isinstance(self.p, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "P" of "PidTuning" is not a number.')

        if self.i is None:
            raise ValueError(f'Property "I" of "PidTuning" is None.')

        if not isinstance(self.i, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "I" of "PidTuning" is not a number.')

        if self.d is None:
            raise ValueError(f'Property "D" of "PidTuning" is None.')

        if not isinstance(self.d, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "D" of "PidTuning" is not a number.')

        if self.fc is None:
            raise ValueError(f'Property "Fc" of "PidTuning" is None.')

        if not isinstance(self.fc, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Fc" of "PidTuning" is not a number.')
