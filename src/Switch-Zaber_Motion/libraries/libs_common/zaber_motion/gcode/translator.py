# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List, Optional
from ..ascii import Stream
from ..call import call, call_async, call_sync
from ..dto import requests as dto
from ..dto.gcode.translate_result import TranslateResult
from ..dto.gcode.translator_config import TranslatorConfig
from ..units import LengthUnits, VelocityUnits


class Translator:
    """
    Represents a live G-Code translator.
    It allows to stream G-Code blocks to a connected device.
    It requires a stream to be setup on the device.
    Requires at least Firmware 7.11.
    """

    @property
    def translator_id(self) -> int:
        """
        The ID of the translator that serves to identify native resources.
        """
        return self._translator_id

    @property
    def coordinate_system(self) -> str:
        """
        Current coordinate system.
        """
        return self.__get_current_coordinate_system()

    def __init__(self, translator_id: int):
        self._translator_id: int = translator_id

    @staticmethod
    def setup(
            stream: Stream,
            config: Optional[TranslatorConfig] = None
    ) -> 'Translator':
        """
        Sets up the translator on top of a provided stream.

        Args:
            stream: The stream to setup the translator on.
                The stream must be already setup in a live or a store mode.
            config: Configuration of the translator.

        Returns:
            New instance of translator.
        """
        request = dto.TranslatorCreateLiveRequest(
            device=stream.device.device_address,
            interface_id=stream.device.connection.interface_id,
            stream_id=stream.stream_id,
            config=config,
        )
        response = call(
            "gcode/create_live",
            request,
            dto.TranslatorCreateResponse.from_binary)
        return Translator(response.translator_id)

    @staticmethod
    async def setup_async(
            stream: Stream,
            config: Optional[TranslatorConfig] = None
    ) -> 'Translator':
        """
        Sets up the translator on top of a provided stream.

        Args:
            stream: The stream to setup the translator on.
                The stream must be already setup in a live or a store mode.
            config: Configuration of the translator.

        Returns:
            New instance of translator.
        """
        request = dto.TranslatorCreateLiveRequest(
            device=stream.device.device_address,
            interface_id=stream.device.connection.interface_id,
            stream_id=stream.stream_id,
            config=config,
        )
        response = await call_async(
            "gcode/create_live",
            request,
            dto.TranslatorCreateResponse.from_binary)
        return Translator(response.translator_id)

    def translate(
            self,
            block: str
    ) -> TranslateResult:
        """
        Translates a single block (line) of G-code.
        The commands are queued in the underlying stream to ensure smooth continues movement.
        Returning of this method indicates that the commands are queued (not necessarily executed).

        Args:
            block: Block (line) of G-code.

        Returns:
            Result of translation containing the commands sent to the device.
        """
        request = dto.TranslatorTranslateRequest(
            translator_id=self.translator_id,
            block=block,
        )
        response = call(
            "gcode/translate_live",
            request,
            TranslateResult.from_binary)
        return response

    async def translate_async(
            self,
            block: str
    ) -> TranslateResult:
        """
        Translates a single block (line) of G-code.
        The commands are queued in the underlying stream to ensure smooth continues movement.
        Returning of this method indicates that the commands are queued (not necessarily executed).

        Args:
            block: Block (line) of G-code.

        Returns:
            Result of translation containing the commands sent to the device.
        """
        request = dto.TranslatorTranslateRequest(
            translator_id=self.translator_id,
            block=block,
        )
        response = await call_async(
            "gcode/translate_live",
            request,
            TranslateResult.from_binary)
        return response

    def flush(
            self,
            wait_until_idle: bool = True
    ) -> List[str]:
        """
        Flushes the remaining stream commands waiting in optimization buffer into the underlying stream.
        The flush is also performed by M2 and M30 codes.

        Args:
            wait_until_idle: Determines whether to wait for the stream to finish all the movements.

        Returns:
            The remaining stream commands.
        """
        request = dto.TranslatorFlushLiveRequest(
            translator_id=self.translator_id,
            wait_until_idle=wait_until_idle,
        )
        response = call(
            "gcode/flush_live",
            request,
            dto.TranslatorFlushResponse.from_binary)
        return response.commands

    async def flush_async(
            self,
            wait_until_idle: bool = True
    ) -> List[str]:
        """
        Flushes the remaining stream commands waiting in optimization buffer into the underlying stream.
        The flush is also performed by M2 and M30 codes.

        Args:
            wait_until_idle: Determines whether to wait for the stream to finish all the movements.

        Returns:
            The remaining stream commands.
        """
        request = dto.TranslatorFlushLiveRequest(
            translator_id=self.translator_id,
            wait_until_idle=wait_until_idle,
        )
        response = await call_async(
            "gcode/flush_live",
            request,
            dto.TranslatorFlushResponse.from_binary)
        return response.commands

    def reset_position(
            self
    ) -> None:
        """
        Resets position of the translator from the underlying stream.
        Call this method after performing a movement outside of translator.
        """
        request = dto.TranslatorEmptyRequest(
            translator_id=self.translator_id,
        )
        call("gcode/reset_position_from_stream", request)

    async def reset_position_async(
            self
    ) -> None:
        """
        Resets position of the translator from the underlying stream.
        Call this method after performing a movement outside of translator.
        """
        request = dto.TranslatorEmptyRequest(
            translator_id=self.translator_id,
        )
        await call_async("gcode/reset_position_from_stream", request)

    def set_traverse_rate(
            self,
            traverse_rate: float,
            unit: VelocityUnits
    ) -> None:
        """
        Sets the speed at which the device moves when traversing (G0).

        Args:
            traverse_rate: The traverse rate.
            unit: Units of the traverse rate.
        """
        request = dto.TranslatorSetTraverseRateRequest(
            translator_id=self.translator_id,
            traverse_rate=traverse_rate,
            unit=unit,
        )
        call_sync("gcode/set_traverse_rate", request)

    def set_axis_position(
            self,
            axis: str,
            position: float,
            unit: LengthUnits
    ) -> None:
        """
        Sets position of translator's axis.
        Use this method to set position after performing movement outside of the translator.
        This method does not cause any movement.

        Args:
            axis: Letter of the axis.
            position: The position.
            unit: Units of position.
        """
        request = dto.TranslatorSetAxisPositionRequest(
            translator_id=self.translator_id,
            axis=axis,
            position=position,
            unit=unit,
        )
        call_sync("gcode/set_axis_position", request)

    def get_axis_position(
            self,
            axis: str,
            unit: LengthUnits
    ) -> float:
        """
        Gets position of translator's axis.
        This method does not query device but returns value from translator's state.

        Args:
            axis: Letter of the axis.
            unit: Units of position.

        Returns:
            Position of translator's axis.
        """
        request = dto.TranslatorGetAxisPositionRequest(
            translator_id=self.translator_id,
            axis=axis,
            unit=unit,
        )
        response = call_sync(
            "gcode/get_axis_position",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_axis_home_position(
            self,
            axis: str,
            position: float,
            unit: LengthUnits
    ) -> None:
        """
        Sets the home position of translator's axis.
        This position is used by G28.

        Args:
            axis: Letter of the axis.
            position: The home position.
            unit: Units of position.
        """
        request = dto.TranslatorSetAxisPositionRequest(
            translator_id=self.translator_id,
            axis=axis,
            position=position,
            unit=unit,
        )
        call_sync("gcode/set_axis_home", request)

    def set_axis_secondary_home_position(
            self,
            axis: str,
            position: float,
            unit: LengthUnits
    ) -> None:
        """
        Sets the secondary home position of translator's axis.
        This position is used by G30.

        Args:
            axis: Letter of the axis.
            position: The home position.
            unit: Units of position.
        """
        request = dto.TranslatorSetAxisPositionRequest(
            translator_id=self.translator_id,
            axis=axis,
            position=position,
            unit=unit,
        )
        call_sync("gcode/set_axis_secondary_home", request)

    def get_axis_coordinate_system_offset(
            self,
            coordinate_system: str,
            axis: str,
            unit: LengthUnits
    ) -> float:
        """
        Gets offset of an axis in a given coordinate system.

        Args:
            coordinate_system: Coordinate system (e.g. G54).
            axis: Letter of the axis.
            unit: Units of position.

        Returns:
            Offset in translator units of the axis.
        """
        request = dto.TranslatorGetAxisOffsetRequest(
            translator_id=self.translator_id,
            coordinate_system=coordinate_system,
            axis=axis,
            unit=unit,
        )
        response = call_sync(
            "gcode/get_axis_offset",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def reset_after_stream_error(
            self
    ) -> None:
        """
        Resets internal state after device rejected generated command.
        Axis positions become uninitialized.
        """
        request = dto.TranslatorEmptyRequest(
            translator_id=self.translator_id,
        )
        call_sync("gcode/reset_after_stream_error", request)

    def set_feed_rate_override(
            self,
            coefficient: float
    ) -> None:
        """
        Allows to scale feed rate of the translated code by a coefficient.

        Args:
            coefficient: Coefficient of the original feed rate.
        """
        request = dto.TranslatorSetFeedRateOverrideRequest(
            translator_id=self.translator_id,
            coefficient=coefficient,
        )
        call_sync("gcode/set_feed_rate_override", request)

    @staticmethod
    def __free(
            translator_id: int
    ) -> None:
        """
        Releases native resources of a translator.

        Args:
            translator_id: The ID of the translator.
        """
        request = dto.TranslatorEmptyRequest(
            translator_id=translator_id,
        )
        call_sync("gcode/free", request)

    def __get_current_coordinate_system(
            self
    ) -> str:
        """
        Gets current coordinate system (e.g. G54).

        Returns:
            Current coordinate system.
        """
        request = dto.TranslatorEmptyRequest(
            translator_id=self.translator_id,
        )
        response = call_sync(
            "gcode/get_current_coordinate_system",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def __del__(self) -> None:
        Translator.__free(self._translator_id)
