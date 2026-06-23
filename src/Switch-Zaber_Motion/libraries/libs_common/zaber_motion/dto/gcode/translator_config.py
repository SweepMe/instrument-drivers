# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from .axis_mapping import AxisMapping
from .axis_transformation import AxisTransformation


@dataclass
class TranslatorConfig:
    """
    Configuration of a translator.
    """

    axis_mappings: Optional[List[AxisMapping]] = None
    """
    Optional custom mapping of translator axes to stream axes.
    """

    axis_transformations: Optional[List[AxisTransformation]] = None
    """
    Optional transformation of axes.
    """

    @staticmethod
    def zero_values() -> 'TranslatorConfig':
        return TranslatorConfig(
            axis_mappings=None,
            axis_transformations=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorConfig':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorConfig.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisMappings': [item.to_dict() for item in self.axis_mappings] if self.axis_mappings is not None else [],
            'axisTransformations': [item.to_dict() for item in self.axis_transformations] if self.axis_transformations is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorConfig':
        return TranslatorConfig(
            axis_mappings=[AxisMapping.from_dict(item) for item in data.get('axisMappings')] if data.get('axisMappings') is not None else None,  # type: ignore
            axis_transformations=[AxisTransformation.from_dict(item) for item in data.get('axisTransformations')] if data.get('axisTransformations') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_mappings is not None:
            if not isinstance(self.axis_mappings, Iterable):
                raise ValueError('Property "AxisMappings" of "TranslatorConfig" is not iterable.')

            for i, axis_mappings_item in enumerate(self.axis_mappings):
                if axis_mappings_item is None:
                    raise ValueError(f'Item {i} in property "AxisMappings" of "TranslatorConfig" is None.')

                if not isinstance(axis_mappings_item, AxisMapping):
                    raise ValueError(f'Item {i} in property "AxisMappings" of "TranslatorConfig" is not an instance of "AxisMapping".')

                axis_mappings_item.validate()

        if self.axis_transformations is not None:
            if not isinstance(self.axis_transformations, Iterable):
                raise ValueError('Property "AxisTransformations" of "TranslatorConfig" is not iterable.')

            for i, axis_transformations_item in enumerate(self.axis_transformations):
                if axis_transformations_item is None:
                    raise ValueError(f'Item {i} in property "AxisTransformations" of "TranslatorConfig" is None.')

                if not isinstance(axis_transformations_item, AxisTransformation):
                    raise ValueError(f'Item {i} in property "AxisTransformations" of "TranslatorConfig" is not an instance of "AxisTransformation".')

                axis_transformations_item.validate()
