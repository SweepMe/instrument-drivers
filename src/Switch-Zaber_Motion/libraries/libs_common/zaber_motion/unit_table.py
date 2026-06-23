# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List
from .call import call_sync
from .dto import requests as dto
from .dto.unit_conversion_descriptor import UnitConversionDescriptor
from .units import UnitsAndLiterals


class UnitTable:
    """
    Helper for working with units of measure.
    """

    @staticmethod
    def get_symbol(
            unit: UnitsAndLiterals
    ) -> str:
        """
        Gets the standard symbol associated with a given unit.

        Args:
            unit: Unit of measure.

        Returns:
            Symbols corresponding to the given unit. Throws NoValueForKey if no symbol is defined.
        """
        request = dto.UnitGetSymbolRequest(
            unit=unit,
        )
        response = call_sync(
            "units/get_symbol",
            request,
            dto.UnitGetSymbolResponse.from_binary)
        return response.symbol

    @staticmethod
    def get_unit(
            symbol: str
    ) -> UnitsAndLiterals:
        """
        Gets the unit enum value associated with a standard symbol.
        Note not all units can be retrieved this way.

        Args:
            symbol: Symbol to look up.

        Returns:
            The unit enum value with the given symbols. Throws NoValueForKey if the symbol is not supported for lookup.
        """
        request = dto.UnitGetEnumRequest(
            symbol=symbol,
        )
        response = call_sync(
            "units/get_enum",
            request,
            dto.UnitGetEnumResponse.from_binary)
        return response.unit

    @staticmethod
    def convert_units(
            value: float,
            from_unit: UnitsAndLiterals,
            to_unit: UnitsAndLiterals
    ) -> float:
        """
        Converts a value from one unit to a different unit of the same dimension.
        Note that this function does not support native unit conversions.

        Args:
            value: The value to be converted.
            from_unit: The unit which the value is being converted from.
            to_unit: The unit which the value is being converted to.

        Returns:
            The converted value. Throws ConversionFailedException if unit is incompatible.
        """
        request = dto.UnitConvertUnitRequest(
            value=value,
            from_unit=from_unit,
            to_unit=to_unit,
        )
        response = call_sync(
            "units/convert_unit",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    @staticmethod
    def convert_to_native_units(
            conversion: UnitConversionDescriptor,
            value: float,
            from_unit: UnitsAndLiterals,
            round: bool = False
    ) -> float:
        """
        Converts a value from one unit to native units given unit conversion descriptor.

        Args:
            conversion: The unit conversion data retrieved from device or axis.
            value: The value to be converted.
            from_unit: The unit which the value is being converted from.
            round: If true, round the result to the descriptor's native decimal places.

        Returns:
            The converted value. Throws ConversionFailedException if unit is incompatible.
        """
        request = dto.UnitConvertNativeRequest(
            conversion=conversion,
            value=value,
            unit=from_unit,
            round=round,
        )
        response = call_sync(
            "units/convert_to_native_unit",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    @staticmethod
    def convert_from_native_units(
            conversion: UnitConversionDescriptor,
            value: float,
            to_unit: UnitsAndLiterals
    ) -> float:
        """
        Converts a value from native units to the specified unit given unit conversion descriptor.

        Args:
            conversion: The unit conversion data retrieved from device or axis.
            value: The value to be converted.
            to_unit: The unit which the value is being converted to.

        Returns:
            The converted value. Throws ConversionFailedException if unit is incompatible.
        """
        request = dto.UnitConvertNativeRequest(
            conversion=conversion,
            value=value,
            unit=to_unit,
        )
        response = call_sync(
            "units/convert_from_native_unit",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    @staticmethod
    def convert_to_native_units_batch(
            conversion: UnitConversionDescriptor,
            values: List[float],
            from_unit: UnitsAndLiterals,
            round: bool = False
    ) -> List[float]:
        """
        Converts values from one unit to native units given unit conversion descriptor.

        Args:
            conversion: The unit conversion data retrieved from device or axis.
            values: The value to be converted.
            from_unit: The unit which the value is being converted from.
            round: If true, round the results to the descriptor's native decimal places.

        Returns:
            The converted values. Throws ConversionFailedException if unit is incompatible.
        """
        request = dto.UnitConvertNativeRequest(
            conversion=conversion,
            values=values,
            unit=from_unit,
            round=round,
        )
        response = call_sync(
            "units/convert_to_native_unit_batch",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    @staticmethod
    def convert_from_native_units_batch(
            conversion: UnitConversionDescriptor,
            values: List[float],
            to_unit: UnitsAndLiterals
    ) -> List[float]:
        """
        Converts values from native units to the specified unit given unit conversion descriptor.

        Args:
            conversion: The unit conversion data retrieved from device or axis.
            values: The value to be converted.
            to_unit: The unit which the value is being converted to.

        Returns:
            The converted values. Throws ConversionFailedException if unit is incompatible.
        """
        request = dto.UnitConvertNativeRequest(
            conversion=conversion,
            values=values,
            unit=to_unit,
        )
        response = call_sync(
            "units/convert_from_native_unit_batch",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values
