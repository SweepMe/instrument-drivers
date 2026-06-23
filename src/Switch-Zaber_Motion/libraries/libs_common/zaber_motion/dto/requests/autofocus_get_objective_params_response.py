# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..named_parameter import NamedParameter


@dataclass
class AutofocusGetObjectiveParamsResponse:

    parameters: List[NamedParameter] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'AutofocusGetObjectiveParamsResponse':
        return AutofocusGetObjectiveParamsResponse(
            parameters=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AutofocusGetObjectiveParamsResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AutofocusGetObjectiveParamsResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'parameters': [item.to_dict() for item in self.parameters] if self.parameters is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AutofocusGetObjectiveParamsResponse':
        return AutofocusGetObjectiveParamsResponse(
            parameters=[NamedParameter.from_dict(item) for item in data.get('parameters')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.parameters is not None:
            if not isinstance(self.parameters, Iterable):
                raise ValueError('Property "Parameters" of "AutofocusGetObjectiveParamsResponse" is not iterable.')

            for i, parameters_item in enumerate(self.parameters):
                if parameters_item is None:
                    raise ValueError(f'Item {i} in property "Parameters" of "AutofocusGetObjectiveParamsResponse" is None.')

                if not isinstance(parameters_item, NamedParameter):
                    raise ValueError(f'Item {i} in property "Parameters" of "AutofocusGetObjectiveParamsResponse" is not an instance of "NamedParameter".')

                parameters_item.validate()
