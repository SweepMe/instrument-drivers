# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..measurement import Measurement


@dataclass
class PvtSetAnalogOutputAction:
    """
    Change the state of an analog output pin in a PVT sequence or buffer.
    """

    channel: int
    """
    The number of the analog output pin to change.
    """

    value: Measurement
    """
    The voltage to set the analog output pin to.
    """

    delay: Optional[Measurement] = None
    """
    If nonzero, specifies the time until the delayed output change occurs.
    """

    future_value: Optional[Measurement] = None
    """
    The voltage to set the output pin to after the delay time expires. Ignored if the delay is zero or unspecified.
    """

    @staticmethod
    def zero_values() -> 'PvtSetAnalogOutputAction':
        return PvtSetAnalogOutputAction(
            channel=0,
            value=Measurement.zero_values(),
            delay=None,
            future_value=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtSetAnalogOutputAction':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtSetAnalogOutputAction.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'channel': int(self.channel),
            'value': self.value.to_dict(),
            'delay': self.delay.to_dict() if self.delay is not None else None,
            'futureValue': self.future_value.to_dict() if self.future_value is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtSetAnalogOutputAction':
        return PvtSetAnalogOutputAction(
            channel=data.get('channel'),  # type: ignore
            value=Measurement.from_dict(data.get('value')),  # type: ignore
            delay=Measurement.from_dict(data.get('delay')) if data.get('delay') is not None else None,  # type: ignore
            future_value=Measurement.from_dict(data.get('futureValue')) if data.get('futureValue') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.channel is None:
            raise ValueError(f'Property "Channel" of "PvtSetAnalogOutputAction" is None.')

        if not isinstance(self.channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Channel" of "PvtSetAnalogOutputAction" is not a number.')

        if int(self.channel) != self.channel:
            raise ValueError(f'Property "Channel" of "PvtSetAnalogOutputAction" is not integer value.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "PvtSetAnalogOutputAction" is None.')

        if not isinstance(self.value, Measurement):
            raise ValueError(f'Property "Value" of "PvtSetAnalogOutputAction" is not an instance of "Measurement".')

        self.value.validate()

        if self.delay is not None:
            if not isinstance(self.delay, Measurement):
                raise ValueError(f'Property "Delay" of "PvtSetAnalogOutputAction" is not an instance of "Measurement".')

            self.delay.validate()

        if self.future_value is not None:
            if not isinstance(self.future_value, Measurement):
                raise ValueError(f'Property "FutureValue" of "PvtSetAnalogOutputAction" is not an instance of "Measurement".')

            self.future_value.validate()
