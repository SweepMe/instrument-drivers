# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class LockstepGetAxisNumbersResponse:

    axes: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'LockstepGetAxisNumbersResponse':
        return LockstepGetAxisNumbersResponse(
            axes=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepGetAxisNumbersResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepGetAxisNumbersResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axes': [int(item) for item in self.axes] if self.axes is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepGetAxisNumbersResponse':
        return LockstepGetAxisNumbersResponse(
            axes=data.get('axes'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "LockstepGetAxisNumbersResponse" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepGetAxisNumbersResponse" is None.')

                if not isinstance(axes_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepGetAxisNumbersResponse" is not a number.')

                if int(axes_item) != axes_item:
                    raise ValueError(f'Item {i} in property "Axes" of "LockstepGetAxisNumbersResponse" is not integer value.')
