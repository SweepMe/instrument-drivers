# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class CommandFailedExceptionData:
    """
    Contains additional data for CommandFailedException.
    """

    @property
    def response_data(self) -> str:
        """
        The response data.
        """

        return self._response_data

    @response_data.setter
    def response_data(self, value: str) -> None:
        self._response_data = value

    @property
    def reply_flag(self) -> str:
        """
        The flags on the reply sent by the device.
        """

        return self._reply_flag

    @reply_flag.setter
    def reply_flag(self, value: str) -> None:
        self._reply_flag = value

    @property
    def status(self) -> str:
        """
        The current device status.
        """

        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def warning_flag(self) -> str:
        """
        The current warning flag on the device.
        """

        return self._warning_flag

    @warning_flag.setter
    def warning_flag(self, value: str) -> None:
        self._warning_flag = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.CommandFailedExceptionData
    ) -> 'CommandFailedExceptionData':
        instance = CommandFailedExceptionData.__new__(
            CommandFailedExceptionData
        )  # type: CommandFailedExceptionData
        instance.response_data = pb_data.response_data
        instance.reply_flag = pb_data.reply_flag
        instance.status = pb_data.status
        instance.warning_flag = pb_data.warning_flag
        return instance
