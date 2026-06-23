# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class TriggerState:
    """
    The complete state of a trigger.
    """

    condition: str
    """
    The firing condition for a trigger.
    """

    actions: List[str]
    """
    The actions for a trigger.
    """

    enabled: bool
    """
    The enabled state for a trigger.
    """

    fires_total: int
    """
    The number of total fires for this trigger.
    A value of -1 indicates unlimited fires.
    """

    fires_remaining: int
    """
    The number of remaining fires for this trigger.
    A value of -1 indicates unlimited fires remaining.
    """

    @staticmethod
    def zero_values() -> 'TriggerState':
        return TriggerState(
            condition="",
            actions=[],
            enabled=False,
            fires_total=0,
            fires_remaining=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerState':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerState.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'condition': str(self.condition or ''),
            'actions': [str(item or '') for item in self.actions] if self.actions is not None else [],
            'enabled': bool(self.enabled),
            'firesTotal': int(self.fires_total),
            'firesRemaining': int(self.fires_remaining),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerState':
        return TriggerState(
            condition=data.get('condition'),  # type: ignore
            actions=data.get('actions'),  # type: ignore
            enabled=data.get('enabled'),  # type: ignore
            fires_total=data.get('firesTotal'),  # type: ignore
            fires_remaining=data.get('firesRemaining'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.condition is not None:
            if not isinstance(self.condition, str):
                raise ValueError(f'Property "Condition" of "TriggerState" is not a string.')

        if self.actions is not None:
            if not isinstance(self.actions, Iterable):
                raise ValueError('Property "Actions" of "TriggerState" is not iterable.')

            for i, actions_item in enumerate(self.actions):
                if actions_item is not None:
                    if not isinstance(actions_item, str):
                        raise ValueError(f'Item {i} in property "Actions" of "TriggerState" is not a string.')

        if self.fires_total is None:
            raise ValueError(f'Property "FiresTotal" of "TriggerState" is None.')

        if not isinstance(self.fires_total, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FiresTotal" of "TriggerState" is not a number.')

        if int(self.fires_total) != self.fires_total:
            raise ValueError(f'Property "FiresTotal" of "TriggerState" is not integer value.')

        if self.fires_remaining is None:
            raise ValueError(f'Property "FiresRemaining" of "TriggerState" is None.')

        if not isinstance(self.fires_remaining, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FiresRemaining" of "TriggerState" is not a number.')

        if int(self.fires_remaining) != self.fires_remaining:
            raise ValueError(f'Property "FiresRemaining" of "TriggerState" is not integer value.')
