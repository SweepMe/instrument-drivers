# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class BinaryCommandFailedExceptionData:
    """
    Contains additional data for BinaryCommandFailedException.
    """

    @property
    def response_data(self) -> int:
        """
        The response data.
        """

        return self._response_data

    @response_data.setter
    def response_data(self, value: int) -> None:
        self._response_data = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.BinaryCommandFailedExceptionData
    ) -> 'BinaryCommandFailedExceptionData':
        instance = BinaryCommandFailedExceptionData.__new__(
            BinaryCommandFailedExceptionData
        )  # type: BinaryCommandFailedExceptionData
        instance.response_data = pb_data.response_data
        return instance
