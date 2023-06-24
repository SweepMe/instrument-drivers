# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class InvalidPacketExceptionData:
    """
    Contains additional data for the InvalidPacketException.
    """

    @property
    def packet(self) -> str:
        """
        The invalid packet that caused the exception.
        """

        return self._packet

    @packet.setter
    def packet(self, value: str) -> None:
        self._packet = value

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
        pb_data: main_pb2.InvalidPacketExceptionData
    ) -> 'InvalidPacketExceptionData':
        instance = InvalidPacketExceptionData.__new__(
            InvalidPacketExceptionData
        )  # type: InvalidPacketExceptionData
        instance.packet = pb_data.packet
        instance.reason = pb_data.reason
        return instance
