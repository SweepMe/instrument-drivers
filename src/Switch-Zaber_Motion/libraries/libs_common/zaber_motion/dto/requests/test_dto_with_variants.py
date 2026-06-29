# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from .test_variant import TestVariant, TestVariantWireFormat


@dataclass
class TestDtoWithVariants:
    """
    A test DTO that includes variant types.
    This is used to verify the correct handling of variant types as members of other DTO types.
    """

    variant_array: List[TestVariant] = field(default_factory=list)
    """
    Array of variants.
    """

    the_variant: Optional[TestVariant] = None
    """
    Single variant instance.
    """

    @staticmethod
    def zero_values() -> 'TestDtoWithVariants':
        return TestDtoWithVariants(
            the_variant=None,
            variant_array=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TestDtoWithVariants':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TestDtoWithVariants.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'theVariant': TestVariantWireFormat(self.the_variant).to_dict() if self.the_variant is not None else None,
            'variantArray': [TestVariantWireFormat(item).to_dict() for item in self.variant_array] if self.variant_array is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestDtoWithVariants':
        return TestDtoWithVariants(
            the_variant=TestVariantWireFormat.from_dict(data.get('theVariant')).convert_back() if data.get('theVariant') is not None else None,  # type: ignore
            variant_array=[TestVariantWireFormat.from_dict(item).convert_back() for item in data.get('variantArray')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.the_variant is not None:
            TestVariantWireFormat(self.the_variant).validate()

        if self.variant_array is not None:
            if not isinstance(self.variant_array, Iterable):
                raise ValueError('Property "VariantArray" of "TestDtoWithVariants" is not iterable.')

            for i, variant_array_item in enumerate(self.variant_array):
                if variant_array_item is not None:
                    TestVariantWireFormat(variant_array_item).validate()
