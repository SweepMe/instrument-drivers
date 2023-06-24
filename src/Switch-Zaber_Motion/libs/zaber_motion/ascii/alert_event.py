# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class AlertEvent:
    """
    Alert message received from the device.
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

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.AlertEvent
    ) -> 'AlertEvent':
        instance = AlertEvent.__new__(
            AlertEvent
        )  # type: AlertEvent
        instance.device_address = pb_data.device_address
        instance.axis_number = pb_data.axis_number
        instance.status = pb_data.status
        instance.warning_flag = pb_data.warning_flag
        instance.data = pb_data.data
        return instance
