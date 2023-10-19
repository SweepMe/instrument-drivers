# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional
from ..protobufs import main_pb2
from .stream_axis_type import StreamAxisType


class StreamAxisDefinition:
    """
    Defines an axis of the stream.
    """

    def __init__(
            self: 'StreamAxisDefinition',
            axis_number: int,
            axis_type: Optional[StreamAxisType] = None
    ) -> None:
        self._axis_number = axis_number
        self._axis_type = axis_type

    @property
    def axis_number(self) -> int:
        """
        Number of a physical axis or a lockstep group.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def axis_type(self) -> Optional[StreamAxisType]:
        """
        Defines the type of the axis.
        """

        return self._axis_type

    @axis_type.setter
    def axis_type(self, value: Optional[StreamAxisType]) -> None:
        self._axis_type = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.StreamAxisDefinition
    ) -> 'StreamAxisDefinition':
        instance = StreamAxisDefinition.__new__(
            StreamAxisDefinition
        )  # type: StreamAxisDefinition
        instance.axis_number = pb_data.axis_number
        instance.axis_type = StreamAxisType(pb_data.axis_type)
        return instance

    @staticmethod
    def to_protobuf(source: 'StreamAxisDefinition') -> main_pb2.StreamAxisDefinition:
        if not isinstance(source, StreamAxisDefinition):
            raise TypeError("Provided value is not StreamAxisDefinition.")

        pb_data = main_pb2.StreamAxisDefinition()
        pb_data.axis_number = source.axis_number
        pb_data.axis_type = source.axis_type.value if source.axis_type is not None else 0
        return pb_data
