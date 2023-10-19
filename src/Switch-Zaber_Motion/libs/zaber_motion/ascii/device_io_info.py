# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class DeviceIOInfo:
    """
    Class representing information on the I/O channels of the device.
    """

    @property
    def number_analog_outputs(self) -> int:
        """
        Number of analog output channels.
        """

        return self._number_analog_outputs

    @number_analog_outputs.setter
    def number_analog_outputs(self, value: int) -> None:
        self._number_analog_outputs = value

    @property
    def number_analog_inputs(self) -> int:
        """
        Number of analog input channels.
        """

        return self._number_analog_inputs

    @number_analog_inputs.setter
    def number_analog_inputs(self, value: int) -> None:
        self._number_analog_inputs = value

    @property
    def number_digital_outputs(self) -> int:
        """
        Number of digital output channels.
        """

        return self._number_digital_outputs

    @number_digital_outputs.setter
    def number_digital_outputs(self, value: int) -> None:
        self._number_digital_outputs = value

    @property
    def number_digital_inputs(self) -> int:
        """
        Number of digital input channels.
        """

        return self._number_digital_inputs

    @number_digital_inputs.setter
    def number_digital_inputs(self, value: int) -> None:
        self._number_digital_inputs = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.DeviceIOInfo
    ) -> 'DeviceIOInfo':
        instance = DeviceIOInfo.__new__(
            DeviceIOInfo
        )  # type: DeviceIOInfo
        instance.number_analog_outputs = pb_data.number_analog_outputs
        instance.number_analog_inputs = pb_data.number_analog_inputs
        instance.number_digital_outputs = pb_data.number_digital_outputs
        instance.number_digital_inputs = pb_data.number_digital_inputs
        return instance
