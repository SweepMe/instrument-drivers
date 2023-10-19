# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from .axis_type import AxisType


class AxisIdentity:
    """
    Representation of data gathered during axis identification.
    """

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """

        return self._peripheral_id

    @peripheral_id.setter
    def peripheral_id(self, value: int) -> None:
        self._peripheral_id = value

    @property
    def peripheral_name(self) -> str:
        """
        Name of the peripheral.
        """

        return self._peripheral_name

    @peripheral_name.setter
    def peripheral_name(self, value: str) -> None:
        self._peripheral_name = value

    @property
    def is_peripheral(self) -> bool:
        """
        Indicates whether the axis is a peripheral or part of an integrated device.
        """

        return self._is_peripheral

    @is_peripheral.setter
    def is_peripheral(self, value: bool) -> None:
        self._is_peripheral = value

    @property
    def axis_type(self) -> AxisType:
        """
        Determines the type of an axis and units it accepts.
        """

        return self._axis_type

    @axis_type.setter
    def axis_type(self, value: AxisType) -> None:
        self._axis_type = value

    @property
    def is_modified(self) -> bool:
        """
        The peripheral has hardware modifications.
        """

        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        self._is_modified = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.AxisIdentity
    ) -> 'AxisIdentity':
        instance = AxisIdentity.__new__(
            AxisIdentity
        )  # type: AxisIdentity
        instance.peripheral_id = pb_data.peripheral_id
        instance.peripheral_name = pb_data.peripheral_name
        instance.is_peripheral = pb_data.is_peripheral
        instance.axis_type = AxisType(pb_data.axis_type)
        instance.is_modified = pb_data.is_modified
        return instance
