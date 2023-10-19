# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from .protobufs import main_pb2


class FirmwareVersion:
    """
    Class representing version of firmware in the controller.
    """

    @property
    def major(self) -> int:
        """
        Major version number.
        """

        return self._major

    @major.setter
    def major(self, value: int) -> None:
        self._major = value

    @property
    def minor(self) -> int:
        """
        Minor version number.
        """

        return self._minor

    @minor.setter
    def minor(self, value: int) -> None:
        self._minor = value

    @property
    def build(self) -> int:
        """
        Build version number.
        """

        return self._build

    @build.setter
    def build(self, value: int) -> None:
        self._build = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.FirmwareVersion
    ) -> 'FirmwareVersion':
        instance = FirmwareVersion.__new__(
            FirmwareVersion
        )  # type: FirmwareVersion
        instance.major = pb_data.major
        instance.minor = pb_data.minor
        instance.build = pb_data.build
        return instance
