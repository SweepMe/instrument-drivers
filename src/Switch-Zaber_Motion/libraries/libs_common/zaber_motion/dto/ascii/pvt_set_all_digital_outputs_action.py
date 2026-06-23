# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from .digital_output_action import DigitalOutputAction
from ..measurement import Measurement


@dataclass
class PvtSetAllDigitalOutputsAction:
    """
    Change the state of multiple pins of a digital output port in a PVT sequence or buffer.
    """

    values: List[DigitalOutputAction]
    """
    The states to set the digital output pins to. Must have one entry per pin in the port.
    """

    delay: Optional[Measurement] = None
    """
    If nonzero, specifies the time until the delayed output change occurs.
    """

    future_values: Optional[List[DigitalOutputAction]] = None
    """
    The states to set the output pins to after the delay time expires. Ignored if the delay is zero or unspecified.
    Must have one entry per pin in the port.
    """

    @staticmethod
    def zero_values() -> 'PvtSetAllDigitalOutputsAction':
        return PvtSetAllDigitalOutputsAction(
            values=[],
            delay=None,
            future_values=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtSetAllDigitalOutputsAction':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtSetAllDigitalOutputsAction.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'values': [item.value for item in self.values] if self.values is not None else [],
            'delay': self.delay.to_dict() if self.delay is not None else None,
            'futureValues': [item.value for item in self.future_values] if self.future_values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtSetAllDigitalOutputsAction':
        return PvtSetAllDigitalOutputsAction(
            values=[DigitalOutputAction(item) for item in data.get('values')],  # type: ignore
            delay=Measurement.from_dict(data.get('delay')) if data.get('delay') is not None else None,  # type: ignore
            future_values=[DigitalOutputAction(item) for item in data.get('futureValues')] if data.get('futureValues') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "PvtSetAllDigitalOutputsAction" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "PvtSetAllDigitalOutputsAction" is None.')

                if not isinstance(values_item, DigitalOutputAction):
                    raise ValueError(f'Item {i} in property "Values" of "PvtSetAllDigitalOutputsAction" is not an instance of "DigitalOutputAction".')

        if self.delay is not None:
            if not isinstance(self.delay, Measurement):
                raise ValueError(f'Property "Delay" of "PvtSetAllDigitalOutputsAction" is not an instance of "Measurement".')

            self.delay.validate()

        if self.future_values is not None:
            if not isinstance(self.future_values, Iterable):
                raise ValueError('Property "FutureValues" of "PvtSetAllDigitalOutputsAction" is not iterable.')

            for i, future_values_item in enumerate(self.future_values):
                if future_values_item is None:
                    raise ValueError(f'Item {i} in property "FutureValues" of "PvtSetAllDigitalOutputsAction" is None.')

                if not isinstance(future_values_item, DigitalOutputAction):
                    raise ValueError(f'Item {i} in property "FutureValues" of "PvtSetAllDigitalOutputsAction" is not an instance of "DigitalOutputAction".')
