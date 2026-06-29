# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from .stream_axis_type import StreamAxisType


@dataclass
class StreamAxisDefinition:
    """
    Defines an axis of the stream.
    """

    axis_number: int
    """
    Number of a physical axis or a lockstep group.
    """

    axis_type: Optional[StreamAxisType] = None
    """
    Defines the type of the axis.
    """

    @staticmethod
    def zero_values() -> 'StreamAxisDefinition':
        return StreamAxisDefinition(
            axis_number=0,
            axis_type=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamAxisDefinition':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamAxisDefinition.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisNumber': int(self.axis_number),
            'axisType': self.axis_type.value if self.axis_type is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamAxisDefinition':
        return StreamAxisDefinition(
            axis_number=data.get('axisNumber'),  # type: ignore
            axis_type=StreamAxisType(data.get('axisType')) if data.get('axisType') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "StreamAxisDefinition" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "StreamAxisDefinition" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "StreamAxisDefinition" is not integer value.')

        if self.axis_type is not None:
            if not isinstance(self.axis_type, StreamAxisType):
                raise ValueError(f'Property "AxisType" of "StreamAxisDefinition" is not an instance of "StreamAxisType".')
