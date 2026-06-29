# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable, too-many-return-statements, no-else-raise
from dataclasses import dataclass, field
from typing import Any, Dict, Union, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.axis_type import AxisType
from ..ascii.io_port_label import IoPortLabel


TestVariant = Union[AxisType, IoPortLabel, int, Optional[float], List[str]]
"""
Test case for variant support. Not part of the public API. Do not use.
"""


@dataclass
class TestVariantWireFormat:
    """
    Serialization wrapper for TestVariant variant. Not part of the public API; do not use.
    """

    variantValueType: str = ""

    axisTypeValue: AxisType = next(first for first in AxisType)

    ioPortLabelValue: IoPortLabel = field(default_factory=IoPortLabel.zero_values)

    int32Value: int = 0

    stringArrayValue: List[str] = field(default_factory=list)

    optionalDoubleValue: Optional[float] = None

    def __init__(self, value: TestVariant) -> None:
        if value is None:
            self.optionalDoubleValue = value
            self.variantValueType = 'optionalDouble'
        elif isinstance(value, Iterable):
            self.stringArrayValue = value
            self.variantValueType = 'stringArray'
        elif isinstance(value, int):
            self.int32Value = value
            self.variantValueType = 'int32'
        elif isinstance(value, (float, decimal.Decimal)):
            self.optionalDoubleValue = value
            self.variantValueType = 'optionalDouble'
        elif isinstance(value, AxisType):
            self.axisTypeValue = value
            self.variantValueType = 'AxisType'
        elif isinstance(value, IoPortLabel):
            self.ioPortLabelValue = value
            self.variantValueType = 'IoPortLabel'
        else:
            raise TypeError(f"Cannot initialize TestVariant with value of type {type(value)}")

    def convert_back(self) -> TestVariant:
        if self.variantValueType == 'AxisType':
            return self.axisTypeValue
        if self.variantValueType == 'IoPortLabel':
            return self.ioPortLabelValue
        if self.variantValueType == 'int32':
            return self.int32Value
        if self.variantValueType == 'optionalDouble':
            return self.optionalDoubleValue
        if self.variantValueType == 'stringArray':
            return self.stringArrayValue

        raise ValueError(f"Invalid variant type tag value: {self.variantValueType}")

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TestVariantWireFormat':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TestVariantWireFormat.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            'variantValueType': self.variantValueType,
        }

        if self.variantValueType == 'AxisType':
            d['axisTypeValue'] = self.axisTypeValue.value
        elif self.variantValueType == 'IoPortLabel':
            d['ioPortLabelValue'] = self.ioPortLabelValue.to_dict()
        elif self.variantValueType == 'int32':
            d['int32Value'] = int(self.int32Value)
        elif self.variantValueType == 'optionalDouble':
            d['optionalDoubleValue'] = float(self.optionalDoubleValue) if self.optionalDoubleValue is not None else None
        elif self.variantValueType == 'stringArray':
            d['stringArrayValue'] = [str(item or '') for item in self.stringArrayValue] if self.stringArrayValue is not None else []
        else:
            raise ValueError(f"Invalid variant type tag {self.variantValueType} value")

        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestVariantWireFormat':
        tag = data.get('variantValueType')
        if tag == 'AxisType':
            return TestVariantWireFormat(AxisType(data.get('axisTypeValue')))  # type: ignore
        if tag == 'IoPortLabel':
            return TestVariantWireFormat(IoPortLabel.from_dict(data.get('ioPortLabelValue')))  # type: ignore
        if tag == 'int32':
            return TestVariantWireFormat(data.get('int32Value'))  # type: ignore
        if tag == 'optionalDouble':
            return TestVariantWireFormat(data.get('optionalDoubleValue'))  # type: ignore
        if tag == 'stringArray':
            return TestVariantWireFormat(data.get('stringArrayValue'))  # type: ignore

        raise ValueError(f"Invalid variant type tag {tag} in response data")

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.variantValueType == 'AxisType':
            if self.axisTypeValue is None:
                raise ValueError(f'Property "AxisType" of "TestVariant" is None.')

            if not isinstance(self.axisTypeValue, AxisType):
                raise ValueError(f'Property "AxisType" of "TestVariant" is not an instance of "AxisType".')

        elif self.variantValueType == 'IoPortLabel':
            if self.ioPortLabelValue is None:
                raise ValueError(f'Property "IoPortLabel" of "TestVariant" is None.')

            if not isinstance(self.ioPortLabelValue, IoPortLabel):
                raise ValueError(f'Property "IoPortLabel" of "TestVariant" is not an instance of "IoPortLabel".')

            self.ioPortLabelValue.validate()

        elif self.variantValueType == 'int32':
            if self.int32Value is None:
                raise ValueError(f'Property "int32" of "TestVariant" is None.')

            if not isinstance(self.int32Value, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "int32" of "TestVariant" is not a number.')

            if int(self.int32Value) != self.int32Value:
                raise ValueError(f'Property "int32" of "TestVariant" is not integer value.')

        elif self.variantValueType == 'optionalDouble':
            if self.optionalDoubleValue is not None:
                if not isinstance(self.optionalDoubleValue, (int, float, decimal.Decimal)):
                    raise ValueError(f'Property "optionalDouble" of "TestVariant" is not a number.')

        elif self.variantValueType == 'stringArray':
            if self.stringArrayValue is not None:
                if not isinstance(self.stringArrayValue, Iterable):
                    raise ValueError('Property "stringArray" of "TestVariant" is not iterable.')

                for i, stringArrayValue_item in enumerate(self.stringArrayValue):
                    if stringArrayValue_item is not None:
                        if not isinstance(stringArrayValue_item, str):
                            raise ValueError(f'Item {i} in property "stringArray" of "TestVariant" is not a string.')
