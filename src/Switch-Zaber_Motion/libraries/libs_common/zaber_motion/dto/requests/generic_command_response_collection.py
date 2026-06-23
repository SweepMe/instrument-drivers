# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.response import Response


@dataclass
class GenericCommandResponseCollection:

    responses: List[Response] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'GenericCommandResponseCollection':
        return GenericCommandResponseCollection(
            responses=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GenericCommandResponseCollection':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GenericCommandResponseCollection.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'responses': [item.to_dict() for item in self.responses] if self.responses is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GenericCommandResponseCollection':
        return GenericCommandResponseCollection(
            responses=[Response.from_dict(item) for item in data.get('responses')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.responses is not None:
            if not isinstance(self.responses, Iterable):
                raise ValueError('Property "Responses" of "GenericCommandResponseCollection" is not iterable.')

            for i, responses_item in enumerate(self.responses):
                if responses_item is None:
                    raise ValueError(f'Item {i} in property "Responses" of "GenericCommandResponseCollection" is None.')

                if not isinstance(responses_item, Response):
                    raise ValueError(f'Item {i} in property "Responses" of "GenericCommandResponseCollection" is not an instance of "Response".')

                responses_item.validate()
