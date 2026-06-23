# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..measurement import Measurement


@dataclass
class PrepareCommandRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    command_template: str = ""

    parameters: List[Measurement] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'PrepareCommandRequest':
        return PrepareCommandRequest(
            interface_id=0,
            device=0,
            axis=0,
            command_template="",
            parameters=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PrepareCommandRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PrepareCommandRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'commandTemplate': str(self.command_template or ''),
            'parameters': [item.to_dict() for item in self.parameters] if self.parameters is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PrepareCommandRequest':
        return PrepareCommandRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            command_template=data.get('commandTemplate'),  # type: ignore
            parameters=[Measurement.from_dict(item) for item in data.get('parameters')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "PrepareCommandRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "PrepareCommandRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "PrepareCommandRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "PrepareCommandRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "PrepareCommandRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "PrepareCommandRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "PrepareCommandRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "PrepareCommandRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "PrepareCommandRequest" is not integer value.')

        if self.command_template is not None:
            if not isinstance(self.command_template, str):
                raise ValueError(f'Property "CommandTemplate" of "PrepareCommandRequest" is not a string.')

        if self.parameters is not None:
            if not isinstance(self.parameters, Iterable):
                raise ValueError('Property "Parameters" of "PrepareCommandRequest" is not iterable.')

            for i, parameters_item in enumerate(self.parameters):
                if parameters_item is None:
                    raise ValueError(f'Item {i} in property "Parameters" of "PrepareCommandRequest" is None.')

                if not isinstance(parameters_item, Measurement):
                    raise ValueError(f'Item {i} in property "Parameters" of "PrepareCommandRequest" is not an instance of "Measurement".')

                parameters_item.validate()
