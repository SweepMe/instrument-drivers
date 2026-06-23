# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..ascii.stream_axis_definition import StreamAxisDefinition
from ..ascii.pvt_axis_definition import PvtAxisDefinition


@dataclass
class StreamGetAxesResponse:

    axes: List[StreamAxisDefinition] = field(default_factory=list)

    pvt_axes: List[PvtAxisDefinition] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamGetAxesResponse':
        return StreamGetAxesResponse(
            axes=[],
            pvt_axes=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamGetAxesResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamGetAxesResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axes': [item.to_dict() for item in self.axes] if self.axes is not None else [],
            'pvtAxes': [item.to_dict() for item in self.pvt_axes] if self.pvt_axes is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamGetAxesResponse':
        return StreamGetAxesResponse(
            axes=[StreamAxisDefinition.from_dict(item) for item in data.get('axes')],  # type: ignore
            pvt_axes=[PvtAxisDefinition.from_dict(item) for item in data.get('pvtAxes')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "StreamGetAxesResponse" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "StreamGetAxesResponse" is None.')

                if not isinstance(axes_item, StreamAxisDefinition):
                    raise ValueError(f'Item {i} in property "Axes" of "StreamGetAxesResponse" is not an instance of "StreamAxisDefinition".')

                axes_item.validate()

        if self.pvt_axes is not None:
            if not isinstance(self.pvt_axes, Iterable):
                raise ValueError('Property "PvtAxes" of "StreamGetAxesResponse" is not iterable.')

            for i, pvt_axes_item in enumerate(self.pvt_axes):
                if pvt_axes_item is None:
                    raise ValueError(f'Item {i} in property "PvtAxes" of "StreamGetAxesResponse" is None.')

                if not isinstance(pvt_axes_item, PvtAxisDefinition):
                    raise ValueError(f'Item {i} in property "PvtAxes" of "StreamGetAxesResponse" is not an instance of "PvtAxisDefinition".')

                pvt_axes_item.validate()
