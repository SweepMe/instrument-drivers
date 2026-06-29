# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable, too-many-return-statements, no-else-raise
from dataclasses import dataclass
from typing import Any, Dict, Union
import decimal
import zaber_bson


TypedSetting = Union[float, int, bool, str]
"""
The value of a setting, which can be of various types.
"""


@dataclass
class TypedSettingWireFormat:
    """
    Serialization wrapper for TypedSetting variant. Not part of the public API; do not use.
    """

    variantValueType: str

    doubleValue: float

    int64Value: int

    boolValue: bool

    stringValue: str

    def __init__(self, value: TypedSetting) -> None:
        if value is None:
            raise ValueError("Cannot initialize TypedSetting with None value")
        elif isinstance(value, int):
            self.int64Value = value
            self.variantValueType = 'int64'
        elif isinstance(value, (float, decimal.Decimal)):
            self.doubleValue = value
            self.variantValueType = 'double'
        elif isinstance(value, bool):
            self.boolValue = value
            self.variantValueType = 'bool'
        elif isinstance(value, str):
            self.stringValue = value
            self.variantValueType = 'string'
        else:
            raise TypeError(f"Cannot initialize TypedSetting with value of type {type(value)}")

    def convert_back(self) -> TypedSetting:
        if self.variantValueType == 'double':
            return self.doubleValue
        if self.variantValueType == 'int64':
            return self.int64Value
        if self.variantValueType == 'bool':
            return self.boolValue
        if self.variantValueType == 'string':
            return self.stringValue

        raise ValueError(f"Invalid variant type tag value: {self.variantValueType}")

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TypedSettingWireFormat':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TypedSettingWireFormat.from_dict(data)

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
        elif self.variantValueType == 'int64':
            d['int64Value'] = int(self.int64Value)
        elif self.variantValueType == 'bool':
            d['boolValue'] = bool(self.boolValue)
        elif self.variantValueType == 'string':
            d['stringValue'] = str(self.stringValue or '')
        else:
            raise ValueError(f"Invalid variant type tag {self.variantValueType} value")

        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TypedSettingWireFormat':
        tag = data.get('variantValueType')
        if tag == 'double':
            return TypedSettingWireFormat(data.get('doubleValue'))  # type: ignore
        if tag == 'int64':
            return TypedSettingWireFormat(data.get('int64Value'))  # type: ignore
        if tag == 'bool':
            return TypedSettingWireFormat(data.get('boolValue'))  # type: ignore
        if tag == 'string':
            return TypedSettingWireFormat(data.get('stringValue'))  # type: ignore

        raise ValueError(f"Invalid variant type tag {tag} in response data")

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.variantValueType == 'double':
            if self.doubleValue is None:
                raise ValueError(f'Property "double" of "TypedSetting" is None.')

            if not isinstance(self.doubleValue, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "double" of "TypedSetting" is not a number.')

        elif self.variantValueType == 'int64':
            if self.int64Value is None:
                raise ValueError(f'Property "int64" of "TypedSetting" is None.')

            if not isinstance(self.int64Value, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "int64" of "TypedSetting" is not a number.')

            if int(self.int64Value) != self.int64Value:
                raise ValueError(f'Property "int64" of "TypedSetting" is not integer value.')

        elif self.variantValueType == 'bool':
            pass
        elif self.variantValueType == 'string':
            if self.stringValue is not None:
                if not isinstance(self.stringValue, str):
                    raise ValueError(f'Property "string" of "TypedSetting" is not a string.')
