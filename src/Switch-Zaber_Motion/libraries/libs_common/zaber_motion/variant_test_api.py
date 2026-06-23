# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List, Optional
from .call import call, call_async
from .dto import requests as dto
from .dto.requests import TestVariant


class VariantTestApi:
    """
    Test case for certain library features. Not public API; do not use.
    """

    @staticmethod
    def mutate_variant(
            the_variant: TestVariant
    ) -> Optional[TestVariant]:
        """
        Tests serialization of variants.

        Args:
            the_variant: Test value to modify and return.

        Returns:
            Mutated input value.
        """
        request = dto.TestDtoWithVariants(
            the_variant=the_variant,
        )
        response = call(
            "test/mutate_variant",
            request,
            dto.TestDtoWithVariants.from_binary)
        return response.the_variant

    @staticmethod
    async def mutate_variant_async(
            the_variant: TestVariant
    ) -> Optional[TestVariant]:
        """
        Tests serialization of variants.

        Args:
            the_variant: Test value to modify and return.

        Returns:
            Mutated input value.
        """
        request = dto.TestDtoWithVariants(
            the_variant=the_variant,
        )
        response = await call_async(
            "test/mutate_variant",
            request,
            dto.TestDtoWithVariants.from_binary)
        return response.the_variant

    @staticmethod
    def mutate_variant_array(
            variant_array: List[TestVariant]
    ) -> List[TestVariant]:
        """
        Tests serialization of arrays of variants.

        Args:
            variant_array: Test values to modify and return.

        Returns:
            Mutated input values.
        """
        request = dto.TestDtoWithVariants(
            variant_array=variant_array,
        )
        response = call(
            "test/mutate_variant",
            request,
            dto.TestDtoWithVariants.from_binary)
        return response.variant_array

    @staticmethod
    async def mutate_variant_array_async(
            variant_array: List[TestVariant]
    ) -> List[TestVariant]:
        """
        Tests serialization of arrays of variants.

        Args:
            variant_array: Test values to modify and return.

        Returns:
            Mutated input values.
        """
        request = dto.TestDtoWithVariants(
            variant_array=variant_array,
        )
        response = await call_async(
            "test/mutate_variant",
            request,
            dto.TestDtoWithVariants.from_binary)
        return response.variant_array
