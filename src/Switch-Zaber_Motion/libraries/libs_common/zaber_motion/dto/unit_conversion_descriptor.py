# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class UnitConversionDescriptor:
    """
    Information about unit conversion.
    """

    dimension: str
    """
    Name of the dimension being converted.
    """

    conversion_function: str
    """
    Internal name of conversion function used.
    """

    scale: float
    """
    Scale factor used in conversion, if applicable.
    """

    decimal_places: int
    """
    Number of decimal places the device uses for the native representation of this setting or command argument.
    """

    resolution: Optional[int] = None
    """
    Microstep resolution used in conversion, if applicable.
    """

    @staticmethod
    def zero_values() -> 'UnitConversionDescriptor':
        return UnitConversionDescriptor(
            dimension="",
            conversion_function="",
            scale=0,
            resolution=None,
            decimal_places=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnitConversionDescriptor':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnitConversionDescriptor.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dimension': str(self.dimension or ''),
            'conversionFunction': str(self.conversion_function or ''),
            'scale': float(self.scale),
            'resolution': int(self.resolution) if self.resolution is not None else None,
            'decimalPlaces': int(self.decimal_places),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnitConversionDescriptor':
        return UnitConversionDescriptor(
            dimension=data.get('dimension'),  # type: ignore
            conversion_function=data.get('conversionFunction'),  # type: ignore
            scale=data.get('scale'),  # type: ignore
            resolution=data.get('resolution'),  # type: ignore
            decimal_places=data.get('decimalPlaces'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.dimension is not None:
            if not isinstance(self.dimension, str):
                raise ValueError(f'Property "Dimension" of "UnitConversionDescriptor" is not a string.')

        if self.conversion_function is not None:
            if not isinstance(self.conversion_function, str):
                raise ValueError(f'Property "ConversionFunction" of "UnitConversionDescriptor" is not a string.')

        if self.scale is None:
            raise ValueError(f'Property "Scale" of "UnitConversionDescriptor" is None.')

        if not isinstance(self.scale, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Scale" of "UnitConversionDescriptor" is not a number.')

        if self.resolution is not None:
            if not isinstance(self.resolution, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Resolution" of "UnitConversionDescriptor" is not a number.')

            if int(self.resolution) != self.resolution:
                raise ValueError(f'Property "Resolution" of "UnitConversionDescriptor" is not integer value.')

        if self.decimal_places is None:
            raise ValueError(f'Property "DecimalPlaces" of "UnitConversionDescriptor" is None.')

        if not isinstance(self.decimal_places, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DecimalPlaces" of "UnitConversionDescriptor" is not a number.')

        if int(self.decimal_places) != self.decimal_places:
            raise ValueError(f'Property "DecimalPlaces" of "UnitConversionDescriptor" is not integer value.')
