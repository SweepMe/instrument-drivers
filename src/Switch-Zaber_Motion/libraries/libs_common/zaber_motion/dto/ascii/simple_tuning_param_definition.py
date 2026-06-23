# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class SimpleTuningParamDefinition:
    """
    Information about a parameter used for the simple tuning method.
    """

    name: str
    """
    The name of the parameter.
    """

    min_label: str
    """
    The human readable description of the effect of a lower value on this setting.
    """

    max_label: str
    """
    The human readable description of the effect of a higher value on this setting.
    """

    data_type: str
    """
    How this parameter will be parsed by the tuner.
    """

    default_value: Optional[float] = None
    """
    The default value of this parameter.
    """

    @staticmethod
    def zero_values() -> 'SimpleTuningParamDefinition':
        return SimpleTuningParamDefinition(
            name="",
            min_label="",
            max_label="",
            data_type="",
            default_value=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SimpleTuningParamDefinition':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SimpleTuningParamDefinition.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': str(self.name or ''),
            'minLabel': str(self.min_label or ''),
            'maxLabel': str(self.max_label or ''),
            'dataType': str(self.data_type or ''),
            'defaultValue': float(self.default_value) if self.default_value is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SimpleTuningParamDefinition':
        return SimpleTuningParamDefinition(
            name=data.get('name'),  # type: ignore
            min_label=data.get('minLabel'),  # type: ignore
            max_label=data.get('maxLabel'),  # type: ignore
            data_type=data.get('dataType'),  # type: ignore
            default_value=data.get('defaultValue'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.name is not None:
            if not isinstance(self.name, str):
                raise ValueError(f'Property "Name" of "SimpleTuningParamDefinition" is not a string.')

        if self.min_label is not None:
            if not isinstance(self.min_label, str):
                raise ValueError(f'Property "MinLabel" of "SimpleTuningParamDefinition" is not a string.')

        if self.max_label is not None:
            if not isinstance(self.max_label, str):
                raise ValueError(f'Property "MaxLabel" of "SimpleTuningParamDefinition" is not a string.')

        if self.data_type is not None:
            if not isinstance(self.data_type, str):
                raise ValueError(f'Property "DataType" of "SimpleTuningParamDefinition" is not a string.')

        if self.default_value is not None:
            if not isinstance(self.default_value, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "DefaultValue" of "SimpleTuningParamDefinition" is not a number.')
