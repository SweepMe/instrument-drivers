# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from .message_type import MessageType


class UnknownResponseEvent:
    """
    Reply that could not be matched to a request.
    """

    @property
    def device_address(self) -> int:
        """
        Number of the device that sent the message.
        """

        return self._device_address

    @device_address.setter
    def device_address(self, value: int) -> None:
        self._device_address = value

    @property
    def axis_number(self) -> int:
        """
        Number of the axis which the response applies to. Zero denotes device scope.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def reply_flag(self) -> str:
        """
        The reply flag indicates if the request was accepted (OK) or rejected (RJ).
        """

        return self._reply_flag

    @reply_flag.setter
    def reply_flag(self, value: str) -> None:
        self._reply_flag = value

    @property
    def status(self) -> str:
        """
        The device status contains BUSY when the axis is moving and IDLE otherwise.
        """

        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def warning_flag(self) -> str:
        """
        The warning flag contains the highest priority warning currently active for the device or axis.
        """

        return self._warning_flag

    @warning_flag.setter
    def warning_flag(self, value: str) -> None:
        self._warning_flag = value

    @property
    def data(self) -> str:
        """
        Response data which varies depending on the request.
        """

        return self._data

    @data.setter
    def data(self, value: str) -> None:
        self._data = value

    @property
    def message_type(self) -> MessageType:
        """
        Type of the reply received.
        """

        return self._message_type

    @message_type.setter
    def message_type(self, value: MessageType) -> None:
        self._message_type = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.UnknownResponseEvent
    ) -> 'UnknownResponseEvent':
        instance = UnknownResponseEvent.__new__(
            UnknownResponseEvent
        )  # type: UnknownResponseEvent
        instance.device_address = pb_data.device_address
        instance.axis_number = pb_data.axis_number
        instance.reply_flag = pb_data.reply_flag
        instance.status = pb_data.status
        instance.warning_flag = pb_data.warning_flag
        instance.data = pb_data.data
        instance.message_type = MessageType(pb_data.message_type)
        return instance
