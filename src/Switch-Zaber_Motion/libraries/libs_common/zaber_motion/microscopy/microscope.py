# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Optional
from ..ascii import Connection, Device, Axis, AxisGroup
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.microscopy.microscope_config import MicroscopeConfig
from ..dto.microscopy.third_party_components import ThirdPartyComponents
from .autofocus import Autofocus
from .camera_trigger import CameraTrigger
from .filter_changer import FilterChanger
from .illuminator import Illuminator
from .objective_changer import ObjectiveChanger


class Microscope:
    """
    Represent a microscope.
    Parts of the microscope may or may not be instantiated depending on the configuration.
    Requires at least Firmware 7.34.
    """

    @property
    def connection(self) -> Connection:
        """
        Connection of the microscope.
        """
        return self._connection

    _illuminator: Optional[Illuminator]

    @property
    def illuminator(self) -> Optional[Illuminator]:
        """
        The illuminator.
        """
        return self._illuminator

    _focus_axis: Optional[Axis]

    @property
    def focus_axis(self) -> Optional[Axis]:
        """
        The focus axis.
        """
        return self._focus_axis

    _x_axis: Optional[Axis]

    @property
    def x_axis(self) -> Optional[Axis]:
        """
        The X axis.
        """
        return self._x_axis

    _y_axis: Optional[Axis]

    @property
    def y_axis(self) -> Optional[Axis]:
        """
        The Y axis.
        """
        return self._y_axis

    _plate: Optional[AxisGroup]

    @property
    def plate(self) -> Optional[AxisGroup]:
        """
        Axis group consisting of X and Y axes representing the plate of the microscope.
        """
        return self._plate

    _objective_changer: Optional[ObjectiveChanger]

    @property
    def objective_changer(self) -> Optional[ObjectiveChanger]:
        """
        The objective changer.
        """
        return self._objective_changer

    _filter_changer: Optional[FilterChanger]

    @property
    def filter_changer(self) -> Optional[FilterChanger]:
        """
        The filter changer.
        """
        return self._filter_changer

    _autofocus: Optional[Autofocus]

    @property
    def autofocus(self) -> Optional[Autofocus]:
        """
        The autofocus feature.
        """
        return self._autofocus

    _camera_trigger: Optional[CameraTrigger]

    @property
    def camera_trigger(self) -> Optional[CameraTrigger]:
        """
        The camera trigger.
        """
        return self._camera_trigger

    def __init__(self, connection: Connection, config: MicroscopeConfig):
        """
        Creates instance of `Microscope` from the given config.
        Parts are instantiated depending on device addresses in the config.
        """
        self._connection: Connection = connection
        self._config: MicroscopeConfig = MicroscopeConfig.from_binary(MicroscopeConfig.to_binary(config))
        self._initialize_components()

    @staticmethod
    def find(
            connection: Connection,
            third_party_components: Optional[ThirdPartyComponents] = None
    ) -> 'Microscope':
        """
        Finds a microscope on a connection.

        Args:
            connection: Connection on which to detect the microscope.
            third_party_components: Third party components of the microscope that cannot be found on the connection.

        Returns:
            New instance of microscope.
        """
        request = dto.MicroscopeFindRequest(
            interface_id=connection.interface_id,
            third_party=third_party_components,
        )
        response = call(
            "microscope/detect",
            request,
            dto.MicroscopeConfigResponse.from_binary)
        return Microscope(connection, response.config)

    @staticmethod
    async def find_async(
            connection: Connection,
            third_party_components: Optional[ThirdPartyComponents] = None
    ) -> 'Microscope':
        """
        Finds a microscope on a connection.

        Args:
            connection: Connection on which to detect the microscope.
            third_party_components: Third party components of the microscope that cannot be found on the connection.

        Returns:
            New instance of microscope.
        """
        request = dto.MicroscopeFindRequest(
            interface_id=connection.interface_id,
            third_party=third_party_components,
        )
        response = await call_async(
            "microscope/detect",
            request,
            dto.MicroscopeConfigResponse.from_binary)
        return Microscope(connection, response.config)

    def initialize(
            self,
            force: bool = False
    ) -> None:
        """
        Initializes the microscope.
        Homes all axes, filter changer, and objective changer if they require it.

        Args:
            force: Forces all devices to home even when not required.
        """
        request = dto.MicroscopeInitRequest(
            interface_id=self.connection.interface_id,
            config=self._config,
            force=force,
        )
        call("microscope/initialize", request)

    async def initialize_async(
            self,
            force: bool = False
    ) -> None:
        """
        Initializes the microscope.
        Homes all axes, filter changer, and objective changer if they require it.

        Args:
            force: Forces all devices to home even when not required.
        """
        request = dto.MicroscopeInitRequest(
            interface_id=self.connection.interface_id,
            config=self._config,
            force=force,
        )
        await call_async("microscope/initialize", request)

    def is_initialized(
            self
    ) -> bool:
        """
        Checks whether the microscope is initialized.

        Returns:
            True, when the microscope is initialized. False, otherwise.
        """
        request = dto.MicroscopeEmptyRequest(
            interface_id=self.connection.interface_id,
            config=self._config,
        )
        response = call(
            "microscope/is_initialized",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def is_initialized_async(
            self
    ) -> bool:
        """
        Checks whether the microscope is initialized.

        Returns:
            True, when the microscope is initialized. False, otherwise.
        """
        request = dto.MicroscopeEmptyRequest(
            interface_id=self.connection.interface_id,
            config=self._config,
        )
        response = await call_async(
            "microscope/is_initialized",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the microscope.

        Returns:
            A string that represents the microscope.
        """
        request = dto.MicroscopeEmptyRequest(
            interface_id=self.connection.interface_id,
            config=self._config,
        )
        response = call_sync(
            "microscope/to_string",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def _initialize_components(self) -> None:
        """
        Initializes the components of the microscope based on the configuration.
        """
        if self._config.illuminator:
            self._illuminator = Illuminator(Device(self._connection, self._config.illuminator))
        else:
            self._illuminator = None

        if self._config.focus_axis and self._config.focus_axis.device:
            self._focus_axis = Axis(
                Device(self._connection, self._config.focus_axis.device), self._config.focus_axis.axis)
        else:
            self._focus_axis = None

        if self._config.x_axis and self._config.x_axis.device:
            self._x_axis = Axis(Device(self._connection, self._config.x_axis.device), self._config.x_axis.axis)
        else:
            self._x_axis = None

        if self._config.y_axis and self._config.y_axis.device:
            self._y_axis = Axis(Device(self._connection, self._config.y_axis.device), self._config.y_axis.axis)
        else:
            self._y_axis = None

        if self._x_axis is not None and self._y_axis is not None:
            self._plate = AxisGroup([self._x_axis, self._y_axis])
        else:
            self._plate = None

        if self._config.objective_changer and self._focus_axis:
            self._objective_changer = ObjectiveChanger(
                Device(self._connection, self._config.objective_changer), self._focus_axis)
        else:
            self._objective_changer = None

        if self._config.filter_changer:
            self._filter_changer = FilterChanger(Device(self._connection, self._config.filter_changer))
        else:
            self._filter_changer = None

        if self._config.autofocus and self._focus_axis:
            turret = self._objective_changer.turret if self._objective_changer else None
            self._autofocus = Autofocus(self._config.autofocus, self._focus_axis, turret)
        else:
            self._autofocus = None

        if self._config.camera_trigger and self._config.camera_trigger.device:
            trigger_device = Device(self._connection, self._config.camera_trigger.device)
            self._camera_trigger = CameraTrigger(trigger_device, self._config.camera_trigger.channel)
        else:
            self._camera_trigger = None
