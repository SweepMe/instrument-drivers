# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..measurement_or_value import MeasurementOrValue, MeasurementOrValueWireFormat


@dataclass
class MoveableSetSettingRequest:

    moveable_id: int = 0

    value: MeasurementOrValue = 0

    @staticmethod
    def zero_values() -> 'MoveableSetSettingRequest':
        return MoveableSetSettingRequest(
            moveable_id=0,
            value=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableSetSettingRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableSetSettingRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'moveableId': int(self.moveable_id),
            'value': MeasurementOrValueWireFormat(self.value).to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableSetSettingRequest':
        return MoveableSetSettingRequest(
            moveable_id=data.get('moveableId'),  # type: ignore
            value=MeasurementOrValueWireFormat.from_dict(data.get('value')).convert_back(),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.moveable_id is None:
            raise ValueError(f'Property "MoveableId" of "MoveableSetSettingRequest" is None.')

        if not isinstance(self.moveable_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableId" of "MoveableSetSettingRequest" is not a number.')

        if int(self.moveable_id) != self.moveable_id:
            raise ValueError(f'Property "MoveableId" of "MoveableSetSettingRequest" is not integer value.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "MoveableSetSettingRequest" is None.')

        MeasurementOrValueWireFormat(self.value).validate()
