# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable, too-many-return-statements, no-else-raise
from dataclasses import dataclass
from typing import Any, Dict, Union
import decimal
import zaber_bson
from .measurement import Measurement


MeasurementOrValue = Union[float, Measurement]
"""
A numerical value, or a Measurement.
"""


@dataclass
class MeasurementOrValueWireFormat:
    """
    Serialization wrapper for MeasurementOrValue variant. Not part of the public API; do not use.
    """

    variantValueType: str

    doubleValue: float

    measurementValue: Measurement

    def __init__(self, value: MeasurementOrValue) -> None:
        if value is None:
            raise ValueError("Cannot initialize MeasurementOrValue with None value")
        elif isinstance(value, (int, float, decimal.Decimal)):
            self.doubleValue = value
            self.variantValueType = 'double'
        elif isinstance(value, Measurement):
            self.measurementValue = value
            self.variantValueType = 'Measurement'
        else:
            raise TypeError(f"Cannot initialize MeasurementOrValue with value of type {type(value)}")

    def convert_back(self) -> MeasurementOrValue:
        if self.variantValueType == 'double':
            return self.doubleValue
        if self.variantValueType == 'Measurement':
            return self.measurementValue

        raise ValueError(f"Invalid variant type tag value: {self.variantValueType}")

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MeasurementOrValueWireFormat':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MeasurementOrValueWireFormat.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            'variantValueType': self.variantValueType,
        }

        if self.variantValueType == 'double':
            d['doubleValue'] = float(self.doubleValue)
        elif self.variantValueType == 'Measurement':
            d['measurementValue'] = self.measurementValue.to_dict()
        else:
            raise ValueError(f"Invalid variant type tag {self.variantValueType} value")

        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MeasurementOrValueWireFormat':
        tag = data.get('variantValueType')
        if tag == 'double':
            return MeasurementOrValueWireFormat(data.get('doubleValue'))  # type: ignore
        if tag == 'Measurement':
            return MeasurementOrValueWireFormat(Measurement.from_dict(data.get('measurementValue')))  # type: ignore

        raise ValueError(f"Invalid variant type tag {tag} in response data")

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.variantValueType == 'double':
            if self.doubleValue is None:
                raise ValueError(f'Property "double" of "MeasurementOrValue" is None.')

            if not isinstance(self.doubleValue, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "double" of "MeasurementOrValue" is not a number.')

        elif self.variantValueType == 'Measurement':
            if self.measurementValue is None:
                raise ValueError(f'Property "Measurement" of "MeasurementOrValue" is None.')

            if not isinstance(self.measurementValue, Measurement):
                raise ValueError(f'Property "Measurement" of "MeasurementOrValue" is not an instance of "Measurement".')

            self.measurementValue.validate()
