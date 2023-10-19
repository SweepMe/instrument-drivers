# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class StreamExecutionExceptionData:
    """
    Contains additional data for StreamExecutionException.
    """

    @property
    def error_flag(self) -> str:
        """
        The error flag that caused the exception.
        """

        return self._error_flag

    @error_flag.setter
    def error_flag(self, value: str) -> None:
        self._error_flag = value

    @property
    def reason(self) -> str:
        """
        The reason for the exception.
        """

        return self._reason

    @reason.setter
    def reason(self, value: str) -> None:
        self._reason = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.StreamExecutionExceptionData
    ) -> 'StreamExecutionExceptionData':
        instance = StreamExecutionExceptionData.__new__(
            StreamExecutionExceptionData
        )  # type: StreamExecutionExceptionData
        instance.error_flag = pb_data.error_flag
        instance.reason = pb_data.reason
        return instance
