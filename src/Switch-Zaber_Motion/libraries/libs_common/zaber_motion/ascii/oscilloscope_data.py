# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List
from ..call import call_sync
from ..dto import requests as dto
from ..dto.ascii.io_port_type import IoPortType
from ..dto.ascii.oscilloscope_capture_properties import OscilloscopeCaptureProperties
from ..dto.ascii.oscilloscope_data_source import OscilloscopeDataSource
from ..units import UnitsAndLiterals, Units, TimeUnits, FrequencyUnits


class OscilloscopeData:
    """
    Contains a block of contiguous recorded data for one channel of the device's oscilloscope.
    """

    @property
    def data_id(self) -> int:
        """
        Unique ID for this block of recorded data.
        """
        return self._data_id

    @property
    def data_source(self) -> OscilloscopeDataSource:
        """
        Indicates whether the data came from a setting or an I/O pin.
        """
        return self.__retrieve_properties().data_source

    @property
    def setting(self) -> str:
        """
        The name of the recorded setting.
        """
        return self.__retrieve_properties().setting

    @property
    def axis_number(self) -> int:
        """
        The number of the axis the data was recorded from, or 0 for the controller.
        """
        return self.__retrieve_properties().axis_number

    @property
    def io_type(self) -> IoPortType:
        """
        Which kind of I/O port data was recorded from.
        """
        return self.__retrieve_properties().io_type

    @property
    def io_channel(self) -> int:
        """
        Which I/O pin within the port was recorded.
        """
        return self.__retrieve_properties().io_channel

    def __init__(self, data_id: int):
        self._data_id: int = data_id

    def get_timebase(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the sample interval that this data was recorded with.

        Args:
            unit: Unit of measure to represent the timebase in.

        Returns:
            The timebase setting at the time the data was recorded.
        """
        request = dto.OscilloscopeDataGetRequest(
            data_id=self.data_id,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_timebase",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_frequency(
            self,
            unit: FrequencyUnits = Units.NATIVE
    ) -> float:
        """
        Get the sampling frequency that this data was recorded with.

        Args:
            unit: Unit of measure to represent the frequency in.

        Returns:
            The frequency (inverse of the timebase setting) at the time the data was recorded.
        """
        request = dto.OscilloscopeDataGetRequest(
            data_id=self.data_id,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_frequency",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_delay(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Get the user-specified time period between receipt of the start command and the first data point.
        Under some circumstances, the actual delay may be different - call GetSampleTime(0) to get the effective delay.

        Args:
            unit: Unit of measure to represent the delay in.

        Returns:
            The delay setting at the time the data was recorded.
        """
        request = dto.OscilloscopeDataGetRequest(
            data_id=self.data_id,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_delay",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_sample_time(
            self,
            index: int,
            unit: TimeUnits = Units.NATIVE
    ) -> float:
        """
        Calculate the time a sample was recorded, relative to when the recording was triggered.

        Args:
            index: 0-based index of the sample to calculate the time of.
            unit: Unit of measure to represent the calculated time in.

        Returns:
            The calculated time offset of the data sample at the given index.
        """
        request = dto.OscilloscopeDataGetSampleTimeRequest(
            data_id=self.data_id,
            index=index,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_sample_time",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def get_sample_times(
            self,
            unit: TimeUnits = Units.NATIVE
    ) -> List[float]:
        """
        Calculate the time for all samples, relative to when the recording was triggered.

        Args:
            unit: Unit of measure to represent the calculated time in.

        Returns:
            The calculated time offsets of all data samples.
        """
        request = dto.OscilloscopeDataGetSampleTimeRequest(
            data_id=self.data_id,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_sample_times",
            request,
            dto.DoubleArrayResponse.from_binary)
        return response.values

    def get_data(
            self,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> List[float]:
        """
        Get the recorded data as an array of doubles, with optional unit conversion.
        Note that not all quantities can be unit converted.
        For example, digital I/O channels and pure numbers such as device mode settings have no units.

        Args:
            unit: Unit of measure to convert the data to.

        Returns:
            The recorded data for one oscilloscope channel, converted to the units specified.
        """
        request = dto.OscilloscopeDataGetRequest(
            data_id=self.data_id,
            unit=unit,
        )
        response = call_sync(
            "oscilloscopedata/get_samples",
            request,
            dto.OscilloscopeDataGetSamplesResponse.from_binary)
        return response.data

    @staticmethod
    def __free(
            data_id: int
    ) -> None:
        """
        Releases native resources of an oscilloscope data buffer.

        Args:
            data_id: The ID of the data buffer to delete.
        """
        request = dto.OscilloscopeDataIdentifier(
            data_id=data_id,
        )
        call_sync("oscilloscopedata/free", request)

    def __retrieve_properties(
            self
    ) -> OscilloscopeCaptureProperties:
        """
        Returns recording properties.

        Returns:
            Capture properties.
        """
        request = dto.OscilloscopeDataIdentifier(
            data_id=self.data_id,
        )
        response = call_sync(
            "oscilloscopedata/get_properties",
            request,
            OscilloscopeCaptureProperties.from_binary)
        return response

    def __del__(self) -> None:
        OscilloscopeData.__free(self._data_id)
