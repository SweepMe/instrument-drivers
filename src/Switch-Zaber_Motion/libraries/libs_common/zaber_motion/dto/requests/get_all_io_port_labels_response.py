# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.io_port_label import IoPortLabel


@dataclass
class GetAllIoPortLabelsResponse:

    labels: List[IoPortLabel] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'GetAllIoPortLabelsResponse':
        return GetAllIoPortLabelsResponse(
            labels=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetAllIoPortLabelsResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetAllIoPortLabelsResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'labels': [item.to_dict() for item in self.labels] if self.labels is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetAllIoPortLabelsResponse':
        return GetAllIoPortLabelsResponse(
            labels=[IoPortLabel.from_dict(item) for item in data.get('labels')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.labels is not None:
            if not isinstance(self.labels, Iterable):
                raise ValueError('Property "Labels" of "GetAllIoPortLabelsResponse" is not iterable.')

            for i, labels_item in enumerate(self.labels):
                if labels_item is None:
                    raise ValueError(f'Item {i} in property "Labels" of "GetAllIoPortLabelsResponse" is None.')

                if not isinstance(labels_item, IoPortLabel):
                    raise ValueError(f'Item {i} in property "Labels" of "GetAllIoPortLabelsResponse" is not an instance of "IoPortLabel".')

                labels_item.validate()
