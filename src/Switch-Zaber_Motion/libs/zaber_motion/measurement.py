# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional
from .protobufs import main_pb2
from .units import Units


class Measurement:
    """
    Represents a numerical value with optional units specified.
    """

    def __init__(
            self: 'Measurement',
            value: float,
            unit: Optional[Units] = None
    ) -> None:
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        """
        Value of the measurement.
        """

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def unit(self) -> Optional[Units]:
        """
        Optional units of the measurement.
        """

        return self._unit

    @unit.setter
    def unit(self, value: Optional[Units]) -> None:
        self._unit = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def to_protobuf(source: 'Measurement') -> main_pb2.Measurement:
        if not isinstance(source, Measurement):
            raise TypeError("Provided value is not Measurement.")

        pb_data = main_pb2.Measurement()
        pb_data.value = source.value
        pb_data.unit = (source.unit or Units.NATIVE).value
        return pb_data
