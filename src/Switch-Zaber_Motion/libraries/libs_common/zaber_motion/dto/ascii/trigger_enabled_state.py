# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class TriggerEnabledState:
    """
    The enabled state of a single trigger.
    Returns whether the given trigger is enabled and the number of times it will fire.
    This is a subset of the complete state, and is faster to query.
    """

    enabled: bool
    """
    The enabled state for a trigger.
    """

    fires_remaining: int
    """
    The number of remaining fires for this trigger.
    A value of -1 indicates unlimited fires remaining.
    """

    @staticmethod
    def zero_values() -> 'TriggerEnabledState':
        return TriggerEnabledState(
            enabled=False,
            fires_remaining=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerEnabledState':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerEnabledState.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'enabled': bool(self.enabled),
            'firesRemaining': int(self.fires_remaining),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerEnabledState':
        return TriggerEnabledState(
            enabled=data.get('enabled'),  # type: ignore
            fires_remaining=data.get('firesRemaining'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.fires_remaining is None:
            raise ValueError(f'Property "FiresRemaining" of "TriggerEnabledState" is None.')

        if not isinstance(self.fires_remaining, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FiresRemaining" of "TriggerEnabledState" is not a number.')

        if int(self.fires_remaining) != self.fires_remaining:
            raise ValueError(f'Property "FiresRemaining" of "TriggerEnabledState" is not integer value.')
