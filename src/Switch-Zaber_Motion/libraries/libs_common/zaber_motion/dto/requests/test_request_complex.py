# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from .test_variant import TestVariant, TestVariantWireFormat
from ..ascii.axis_type import AxisType


@dataclass
class TestRequestComplex:

    int_array: List[int] = field(default_factory=list)

    test_variant: TestVariant = next(first for first in AxisType)

    @staticmethod
    def zero_values() -> 'TestRequestComplex':
        return TestRequestComplex(
            int_array=[],
            test_variant=next(first for first in AxisType),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TestRequestComplex':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TestRequestComplex.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'intArray': [int(item) for item in self.int_array] if self.int_array is not None else [],
            'testVariant': TestVariantWireFormat(self.test_variant).to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestRequestComplex':
        return TestRequestComplex(
            int_array=data.get('intArray'),  # type: ignore
            test_variant=TestVariantWireFormat.from_dict(data.get('testVariant')).convert_back(),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.int_array is not None:
            if not isinstance(self.int_array, Iterable):
                raise ValueError('Property "IntArray" of "TestRequestComplex" is not iterable.')

            for i, int_array_item in enumerate(self.int_array):
                if int_array_item is None:
                    raise ValueError(f'Item {i} in property "IntArray" of "TestRequestComplex" is None.')

                if not isinstance(int_array_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "IntArray" of "TestRequestComplex" is not a number.')

                if int(int_array_item) != int_array_item:
                    raise ValueError(f'Item {i} in property "IntArray" of "TestRequestComplex" is not integer value.')

        if self.test_variant is not None:
            TestVariantWireFormat(self.test_variant).validate()
