# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class LockstepAxes:
    """
    The axis numbers of a lockstep group.
    """

    @property
    def axis_1(self) -> int:
        """
        The axis number used to set the first axis.
        """

        return self._axis_1

    @axis_1.setter
    def axis_1(self, value: int) -> None:
        self._axis_1 = value

    @property
    def axis_2(self) -> int:
        """
        The axis number used to set the second axis.
        """

        return self._axis_2

    @axis_2.setter
    def axis_2(self, value: int) -> None:
        self._axis_2 = value

    @property
    def axis_3(self) -> int:
        """
        The axis number used to set the third axis.
        """

        return self._axis_3

    @axis_3.setter
    def axis_3(self, value: int) -> None:
        self._axis_3 = value

    @property
    def axis_4(self) -> int:
        """
        The axis number used to set the fourth axis.
        """

        return self._axis_4

    @axis_4.setter
    def axis_4(self, value: int) -> None:
        self._axis_4 = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.LockstepAxes
    ) -> 'LockstepAxes':
        instance = LockstepAxes.__new__(
            LockstepAxes
        )  # type: LockstepAxes
        instance.axis_1 = pb_data.axis_1
        instance.axis_2 = pb_data.axis_2
        instance.axis_3 = pb_data.axis_3
        instance.axis_4 = pb_data.axis_4
        return instance
