# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .set_state_axis_response import SetStateAxisResponse


@dataclass
class SetStateDeviceResponse:
    """
    An object containing any non-blocking issues encountered when loading a saved state to a device.
    """

    warnings: List[str]
    """
    The warnings encountered when applying this state to the given device.
    """

    axis_responses: List[SetStateAxisResponse]
    """
    A list of axis responses, potentially with warnings encountered
    when applying this state to the device's axes.
    """

    @staticmethod
    def zero_values() -> 'SetStateDeviceResponse':
        return SetStateDeviceResponse(
            warnings=[],
            axis_responses=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetStateDeviceResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetStateDeviceResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'warnings': [str(item or '') for item in self.warnings] if self.warnings is not None else [],
            'axisResponses': [item.to_dict() for item in self.axis_responses] if self.axis_responses is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetStateDeviceResponse':
        return SetStateDeviceResponse(
            warnings=data.get('warnings'),  # type: ignore
            axis_responses=[SetStateAxisResponse.from_dict(item) for item in data.get('axisResponses')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.warnings is not None:
            if not isinstance(self.warnings, Iterable):
                raise ValueError('Property "Warnings" of "SetStateDeviceResponse" is not iterable.')

            for i, warnings_item in enumerate(self.warnings):
                if warnings_item is not None:
                    if not isinstance(warnings_item, str):
                        raise ValueError(f'Item {i} in property "Warnings" of "SetStateDeviceResponse" is not a string.')

        if self.axis_responses is not None:
            if not isinstance(self.axis_responses, Iterable):
                raise ValueError('Property "AxisResponses" of "SetStateDeviceResponse" is not iterable.')

            for i, axis_responses_item in enumerate(self.axis_responses):
                if axis_responses_item is None:
                    raise ValueError(f'Item {i} in property "AxisResponses" of "SetStateDeviceResponse" is None.')

                if not isinstance(axis_responses_item, SetStateAxisResponse):
                    raise ValueError(f'Item {i} in property "AxisResponses" of "SetStateDeviceResponse" is not an instance of "SetStateAxisResponse".')

                axis_responses_item.validate()
