# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class ReplyOnlyEvent:
    """
    Spontaneous message received from the device.
    """

    @property
    def device_address(self) -> int:
        """
        Number of the device that sent or should receive the message.
        """

        return self._device_address

    @device_address.setter
    def device_address(self, value: int) -> None:
        self._device_address = value

    @property
    def command(self) -> int:
        """
        The warning flag contains the highest priority warning currently active for the device or axis.
        """

        return self._command

    @command.setter
    def command(self, value: int) -> None:
        self._command = value

    @property
    def data(self) -> int:
        """
        Data payload of the message, if applicable, or zero otherwise.
        """

        return self._data

    @data.setter
    def data(self, value: int) -> None:
        self._data = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.BinaryReplyOnlyEvent
    ) -> 'ReplyOnlyEvent':
        instance = ReplyOnlyEvent.__new__(
            ReplyOnlyEvent
        )  # type: ReplyOnlyEvent
        instance.device_address = pb_data.device_address
        instance.command = pb_data.command
        instance.data = pb_data.data
        return instance
