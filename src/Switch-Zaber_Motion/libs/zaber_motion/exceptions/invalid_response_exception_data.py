# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class InvalidResponseExceptionData:
    """
    Contains additional data for InvalidResponseException.
    """

    @property
    def response(self) -> str:
        """
        The response data.
        """

        return self._response

    @response.setter
    def response(self, value: str) -> None:
        self._response = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.InvalidResponseExceptionData
    ) -> 'InvalidResponseExceptionData':
        instance = InvalidResponseExceptionData.__new__(
            InvalidResponseExceptionData
        )  # type: InvalidResponseExceptionData
        instance.response = pb_data.response
        return instance
