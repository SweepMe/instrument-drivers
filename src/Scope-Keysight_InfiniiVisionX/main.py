# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! driver
# * Module: Scope
# * Instrument: Keysight InfiniiVision X-Series (1000 X, 2000 X, 3000 X, 3000T X, 4000 X, 6000 X)

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice

if TYPE_CHECKING:
    from numpy.typing import NDArray


class Device(EmptyDevice):
    """Driver for the analog channels of Keysight InfiniiVision X-Series oscilloscopes."""

    MAX_CHANNELS: ClassVar[int] = 4
    """The model is only known after connecting, so the GUI always offers the maximum number of channels."""

    FIRST_SERIES_WITH_50_OHM: ClassVar[int] = 3
    """The 1000 X and 2000 X-Series have 1 MOhm inputs only."""

    def __init__(self) -> None:
        """Initialize the driver class and the default parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "InfiniiVision X"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication
        self.port_manager = True
        self.port_types = ["USB", "TCPIP", "GPIB"]
        # Compared as case-sensitive substrings of the *IDN? answer, e.g. "KEYSIGHT TECHNOLOGIES,MSO-X 3024T,..."
        self.port_identifications = ["DSO-X", "MSO-X", "DSOX", "MSOX", "EDU-X", "EDUX"]
        self.port_properties = {
            # Reading the full acquisition record of several channels can take a few seconds.
            "timeout": 10.0,
        }

        # Model dependent capabilities, read from the identification in 'initialize'
        self.model: str = ""
        self.number_of_channels: int = self.MAX_CHANNELS
        self.has_50_ohm_input: bool = True

        # Front panel names to SCPI arguments
        self.trigger_sources = {
            "Channel 1": "CHANnel1",
            "Channel 2": "CHANnel2",
            "Channel 3": "CHANnel3",
            "Channel 4": "CHANnel4",
            "External": "EXTernal",
            "Line": "LINE",
        }
        self.trigger_slopes = {
            "Rising": "POSitive",
            "Falling": "NEGative",
            "Either": "EITHer",
            "Alternating": "ALTernate",
        }
        self.trigger_couplings = {
            "DC": "DC",
            "AC": "AC",
            "LF reject": "LFReject",
        }
        self.acquisition_types = {
            "Normal": "NORMal",
            "Average": "AVERage",
            "High resolution": "HRESolution",
            "Peak detect": "PEAK",
        }
        self.channel_couplings = {
            "DC": "DC",
            "AC": "AC",
        }
        self.channel_impedances = {
            "1 MOhm": "ONEMeg",
            "50 Ohm": "FIFTy",
        }
        self.channel_probes = {
            "1:1": 1,
            "10:1": 10,
            "100:1": 100,
        }

        # Vertical settings offered in the GUI, as V/div. The ranges are 8 divisions.
        self.channel_scales = ["0.001", "0.002", "0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5"]
        self.channel_full_ranges = ["0.008", "0.016", "0.04", "0.08", "0.16", "0.4", "0.8", "1.6", "4", "8", "16", "40"]

        # The scope rounds the number of points down to the next value it can deliver.
        self.points_options = [
            "1000",
            "2000",
            "5000",
            "10000",
            "20000",
            "50000",
            "100000",
            "200000",
            "500000",
            "1000000",
            "2000000",
            "4000000",
        ]

        self.average_options = [str(2**n) for n in range(1, 17)]  # 2 ... 65536

        # Seconds between two status queries while waiting for an acquisition
        self.poll_interval = 0.02

        # GUI parameters, exactly as they arrive from the GUI
        self.gui_parameters: dict[str, Any] = {}

        self.sweepmode: str = "None"

        # Trigger
        self.trigger_source: str = "As is"
        self.trigger_slope: str = "As is"
        self.trigger_coupling: str = "As is"
        self.trigger_level: float | None = None
        self.trigger_timeout: float = 10.0

        # Timebase
        self.time_range_type: str = "As is"
        self.time_range_value: float = 1e-3
        self.time_offset_value: float = 0.0

        # Acquisition
        self.acquisition: str = "As is"
        self.average: int = 2
        self.sampling_rate_type: str = "Maximum points"
        self.number_of_points: int | None = None

        # Channels
        self.voltage_range_type: str = "Voltage range in V"
        self.channels: list[int] = []
        self.channel_names: dict[int, str] = {}
        self.channel_ranges: dict[int, float | None] = {}
        self.channel_offsets: dict[int, float | None] = {}
        self.channel_coupling_selection: dict[int, str] = {}
        self.channel_impedance_selection: dict[int, str] = {}
        self.channel_probe_selection: dict[int, str] = {}

        # Results
        self.time_values: NDArray[np.float64] = np.array([])
        self.channel_data: list[NDArray[np.float64]] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields, depending on the selected trigger, timebase, acquisition and channels."""
        trigger_source = parameters.get("TriggerSource", "As is")
        time_range_type = parameters.get("TimeRange", "As is")
        acquisition = parameters.get("Acquisition", "As is")
        sampling_rate_type = parameters.get("SamplingRateType", "Maximum points")
        voltage_range_type = parameters.get("VoltageRange", "Voltage range in V")

        new_parameters: dict[str, Any] = {
            "SweepMode": ["None", "Time range in s", "Time scale in s/div", "Time offset in s", "Trigger level in V"],
            # "Software" triggers without waiting for an edge, e.g. to read a free running signal
            "TriggerSource": ["As is", *self.trigger_sources.keys(), "Software"],
        }

        if trigger_source != "Software":
            new_parameters["TriggerSlope"] = ["As is", *self.trigger_slopes.keys()]

        # The power line trigger has neither a level nor a coupling
        if trigger_source not in ("Software", "Line"):
            new_parameters["TriggerCoupling"] = ["As is", *self.trigger_couplings.keys()]
            new_parameters["TriggerLevel"] = "As is"

        new_parameters["TriggerTimeout"] = 10.0

        new_parameters["TimeRange"] = ["As is", "Time range in s", "Time scale in s/div"]
        if time_range_type != "As is":
            new_parameters["TimeRangeValue"] = 1e-3
            new_parameters["TimeOffsetValue"] = 0.0

        new_parameters["Acquisition"] = ["As is", *self.acquisition_types.keys()]
        if acquisition == "Average":
            new_parameters["Average"] = self.average_options

        new_parameters["SamplingRateType"] = ["Maximum points", "Number of points"]
        if sampling_rate_type == "Number of points":
            new_parameters["SamplingRate"] = self.points_options

        new_parameters["VoltageRange"] = ["Voltage range in V", "Voltage scale in V/div"]
        channel_range_options = (
            self.channel_scales if voltage_range_type == "Voltage scale in V/div" else self.channel_full_ranges
        )

        for i in range(1, self.MAX_CHANNELS + 1):
            new_parameters[f"Channel{i}"] = i == 1
            if parameters.get(f"Channel{i}", i == 1):
                new_parameters[f"Channel{i}_Name"] = f"Ch{i}"
                new_parameters[f"Channel{i}_Range"] = ["As is", *channel_range_options]
                new_parameters[f"Channel{i}_Offset"] = "As is"
                new_parameters[f"Channel{i}_Coupling"] = ["As is", *self.channel_couplings.keys()]
                new_parameters[f"Channel{i}_Impedance"] = ["As is", *self.channel_impedances.keys()]
                new_parameters[f"Channel{i}_Probe"] = ["As is", *self.channel_probes.keys()]

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the user selections and derive the returned variables.

        The values are converted to numbers in 'convert_gui_parameters', called from 'configure', because this
        function can be called with incomplete values while the user is still editing the fields.
        """
        self.gui_parameters = dict(parameters)

        self.sweepmode = parameters.get("SweepMode", "None")

        self.channels = [i for i in range(1, self.MAX_CHANNELS + 1) if parameters.get(f"Channel{i}", i == 1)]
        self.channel_names = {i: parameters.get(f"Channel{i}_Name", f"Ch{i}") for i in self.channels}

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]
        self.savetype = [True]

        for i in self.channels:
            self.variables.append(f"CH{i} {self.channel_names[i]}")
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self) -> None:
        """Clear the status and error registers and read the capabilities of the connected model."""
        self.clear_status()
        self.read_model_capabilities()

    def configure(self) -> None:
        """Apply the GUI parameters to the instrument."""
        self.convert_gui_parameters()
        self.check_model_capabilities()

        # Settings are applied to a stopped instrument, every measurement point starts its own acquisition
        self.stop_acquisition()
        self.clear_status()

        self.set_waveform_format()

        for channel in range(1, self.number_of_channels + 1):
            if channel in self.channels:
                self.configure_channel(channel)
            else:
                # Unused channels are switched off, so that the used channels get more acquisition memory
                self.set_channel_display(channel, False)

        self.configure_timebase()
        self.configure_acquisition()

        # The trigger is set after the channels, as the trigger level range depends on the channel settings
        self.configure_trigger()

        errors = self.get_errors()
        if errors:
            msg = "The oscilloscope did not accept all settings: " + "; ".join(errors)
            raise ValueError(msg)

    def apply(self) -> None:
        """Set the sweep value."""
        if self.sweepmode == "None":
            return

        value = float(self.value)

        if self.sweepmode == "Time range in s":
            self.set_time_range(value)
        elif self.sweepmode == "Time scale in s/div":
            self.set_time_scale(value)
        elif self.sweepmode == "Time offset in s":
            self.set_time_position(value)
        elif self.sweepmode == "Trigger level in V":
            self.set_trigger_level(value)

    def measure(self) -> None:
        """Start a single acquisition and wait until it is complete."""
        self.single()

        start_time = time.perf_counter()
        while self.is_acquisition_running():
            if self.is_run_stopped():
                self.stop_acquisition()
                return

            if time.perf_counter() - start_time > self.trigger_timeout:
                self.stop_acquisition()
                msg = (
                    f"The oscilloscope did not trigger within the trigger timeout of {self.trigger_timeout} s. "
                    "Check the trigger settings or increase the trigger timeout."
                )
                raise TimeoutError(msg)

            if self.trigger_source == "Software":
                # Each acquisition needs its own trigger, e.g. every single acquisition of an average
                self.force_trigger()

            time.sleep(self.poll_interval)

    def read_result(self) -> None:
        """Read the waveforms of all selected channels."""
        self.channel_data = []
        self.time_values = np.array([])

        if self.is_run_stopped():
            # The acquisition was aborted, empty arrays keep the number of returned values
            self.channel_data = [np.array([]) for _ in self.channels]
            return

        self.set_waveform_points("MAXimum" if self.number_of_points is None else str(self.number_of_points))

        for channel in self.channels:
            self.set_waveform_source(f"CHANnel{channel}")
            preamble = self.get_waveform_preamble()
            data = self.get_waveform_data()

            voltages = (data - preamble["y_reference"]) * preamble["y_increment"] + preamble["y_origin"]
            self.channel_data.append(voltages)

            if self.time_values.size == 0:
                self.time_values = self.get_time_values(preamble, len(data))

    @staticmethod
    def get_time_values(preamble: dict[str, float], number_of_values: int) -> NDArray[np.float64]:
        """Return the time axis of a waveform with the given number of values.

        In peak detect mode, the waveform contains a minimum and a maximum value for every time interval, so it has
        twice as many values as the preamble has points. Both values of a pair get the time of their interval.
        """
        points = int(preamble["points"])
        values_per_point = 2 if number_of_values == 2 * points else 1
        if values_per_point == 1:
            points = number_of_values

        index = np.arange(points)
        time_values = (index - preamble["x_reference"]) * preamble["x_increment"] + preamble["x_origin"]
        return np.repeat(time_values, values_per_point)

    def call(self) -> list[NDArray[np.float64]]:
        """Return the time axis and the voltages of all selected channels."""
        return [self.time_values, *self.channel_data]

    # Functions

    def convert_gui_parameters(self) -> None:
        """Convert the stored GUI parameters to numbers and check them for valid values.

        The converted values are written to separate attributes, so that a later call of 'apply_gui_parameters'
        cannot revert them back to strings.
        """
        parameters = self.gui_parameters

        if not self.channels:
            msg = "Please select at least one channel."
            raise ValueError(msg)

        self.trigger_source = parameters.get("TriggerSource", "As is")
        self.trigger_slope = parameters.get("TriggerSlope", "As is")
        self.trigger_coupling = parameters.get("TriggerCoupling", "As is")
        self.trigger_level = self.to_float_or_none(parameters.get("TriggerLevel", "As is"), "Trigger level")
        self.trigger_timeout = self.to_float(parameters.get("TriggerTimeout", 10.0), "Trigger timeout")

        self.time_range_type = parameters.get("TimeRange", "As is")
        if self.time_range_type != "As is":
            self.time_range_value = self.to_float(parameters.get("TimeRangeValue", 1e-3), "Time range")
            self.time_offset_value = self.to_float(parameters.get("TimeOffsetValue", 0.0), "Time offset")

        self.acquisition = parameters.get("Acquisition", "As is")
        if self.acquisition == "Average":
            self.average = int(self.to_float(parameters.get("Average", 2), "Average"))

        self.sampling_rate_type = parameters.get("SamplingRateType", "Maximum points")
        if self.sampling_rate_type == "Number of points":
            self.number_of_points = int(self.to_float(parameters.get("SamplingRate", 1000), "Number of points"))
        else:
            self.number_of_points = None

        self.voltage_range_type = parameters.get("VoltageRange", "Voltage range in V")
        for i in self.channels:
            self.channel_ranges[i] = self.to_float_or_none(parameters.get(f"Channel{i}_Range", "As is"), "Range")
            self.channel_offsets[i] = self.to_float_or_none(parameters.get(f"Channel{i}_Offset", "As is"), "Offset")
            self.channel_coupling_selection[i] = parameters.get(f"Channel{i}_Coupling", "As is")
            self.channel_impedance_selection[i] = parameters.get(f"Channel{i}_Impedance", "As is")
            self.channel_probe_selection[i] = parameters.get(f"Channel{i}_Probe", "As is")

    @staticmethod
    def to_float(value: str | float | None, name: str) -> float:
        """Convert a GUI value to float, raising a readable error for invalid entries."""
        try:
            return float(value)  # type: ignore[arg-type]  # None is handled by the except clause
        except (TypeError, ValueError):
            msg = f"{name}: '{value}' is not a valid number."
            raise ValueError(msg) from None

    @classmethod
    def to_float_or_none(cls, value: str | float | None, name: str) -> float | None:
        """Convert a GUI value to float, or return None if the value is 'As is' or empty."""
        if value is None or str(value).strip() in ("", "As is"):
            return None
        return cls.to_float(value, name)

    def read_model_capabilities(self) -> None:
        """Derive the number of analog channels and the availability of 50 Ohm inputs from the model number.

        The four digits of the model number are series, two digits bandwidth, and number of analog channels, e.g.
        MSO-X 3024T is a 3000T X-Series model with 200 MHz and 4 channels. Only the 3000 X-Series and above have
        50 Ohm inputs. If the model number cannot be parsed, 4 channels with 50 Ohm inputs are assumed.
        """
        identification = self.get_identification().split(",")
        self.model = identification[1].strip() if len(identification) > 1 else identification[0].strip()

        match = re.search(r"(\d)\d\d([24])[A-Z]*$", self.model.replace(" ", ""))
        if match:
            self.number_of_channels = int(match.group(2))
            self.has_50_ohm_input = int(match.group(1)) >= self.FIRST_SERIES_WITH_50_OHM
        else:
            self.number_of_channels = self.MAX_CHANNELS
            self.has_50_ohm_input = True

    def check_model_capabilities(self) -> None:
        """Raise an error if channels, trigger source or input impedance do not exist on the connected model."""
        missing_channels = [str(i) for i in self.channels if i > self.number_of_channels]
        if missing_channels:
            msg = (
                f"The {self.model} has {self.number_of_channels} analog channels. "
                f"Please deselect channel {', '.join(missing_channels)}."
            )
            raise ValueError(msg)

        if self.trigger_source.startswith("Channel ") and int(self.trigger_source[-1]) > self.number_of_channels:
            msg = f"The {self.model} has no {self.trigger_source}. Please select another trigger source."
            raise ValueError(msg)

        if not self.has_50_ohm_input:
            channels_50_ohm = [str(i) for i in self.channels if self.channel_impedance_selection[i] == "50 Ohm"]
            if channels_50_ohm:
                msg = (
                    f"The {self.model} has no 50 Ohm inputs. "
                    f"Please set the impedance of channel {', '.join(channels_50_ohm)} to '1 MOhm' or 'As is'."
                )
                raise ValueError(msg)

    def configure_timebase(self) -> None:
        """Set the horizontal range or scale together with the horizontal position."""
        if self.time_range_type == "Time range in s":
            self.set_time_range(self.time_range_value)
            self.set_time_position(self.time_offset_value)
        elif self.time_range_type == "Time scale in s/div":
            self.set_time_scale(self.time_range_value)
            self.set_time_position(self.time_offset_value)

    def configure_acquisition(self) -> None:
        """Set the acquisition type and, for averaging, the number of averages."""
        if self.acquisition == "As is":
            return

        self.set_acquisition_type(self.acquisition_types[self.acquisition])
        if self.acquisition == "Average":
            self.set_average_count(self.average)

    def configure_trigger(self) -> None:
        """Set the edge trigger. With 'Software', the trigger settings are left as they are."""
        if self.trigger_source == "Software":
            return

        if self.trigger_source in self.trigger_sources:
            self.set_trigger_mode_edge()
            self.set_trigger_source(self.trigger_sources[self.trigger_source])

        if self.trigger_slope != "As is":
            self.set_trigger_slope(self.trigger_slopes[self.trigger_slope])

        # The power line trigger has neither a level nor a coupling
        if self.trigger_source != "Line":
            if self.trigger_coupling != "As is":
                self.set_trigger_coupling(self.trigger_couplings[self.trigger_coupling])
            if self.trigger_level is not None:
                self.set_trigger_level(self.trigger_level)

    def configure_channel(self, channel: int) -> None:
        """Switch on the channel and apply its settings.

        Probe and impedance are set first, because the allowed range of the channel depends on them.
        """
        self.set_channel_display(channel, True)

        probe = self.channel_probe_selection[channel]
        if probe != "As is":
            self.set_channel_probe(channel, self.channel_probes[probe])

        # Models without 50 Ohm inputs have 1 MOhm only, which therefore is not set
        impedance = self.channel_impedance_selection[channel]
        if impedance != "As is" and self.has_50_ohm_input:
            self.set_channel_impedance(channel, self.channel_impedances[impedance])

        coupling = self.channel_coupling_selection[channel]
        if coupling != "As is":
            self.set_channel_coupling(channel, self.channel_couplings[coupling])

        channel_range = self.channel_ranges[channel]
        if channel_range is not None:
            if self.voltage_range_type == "Voltage scale in V/div":
                self.set_channel_scale(channel, channel_range)
            else:
                self.set_channel_range(channel, channel_range)

        channel_offset = self.channel_offsets[channel]
        if channel_offset is not None:
            self.set_channel_offset(channel, channel_offset)

    # Wrapped device commands

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        self.port.write("*IDN?")
        identification: str = self.port.read()
        return identification

    def get_errors(self) -> list[str]:
        """Read all entries of the error queue."""
        errors = []
        for _ in range(50):  # the queue holds at most 30 entries
            self.port.write(":SYSTem:ERRor?")
            answer = self.port.read()
            if answer.lstrip("+").startswith("0"):
                break
            errors.append(answer)
        return errors

    def single(self) -> None:
        """Start a single acquisition. With averaging, the scope acquires as many triggers as set as count."""
        self.port.write(":SINGle")

    def stop_acquisition(self) -> None:
        """Stop the acquisition."""
        self.port.write(":STOP")

    def force_trigger(self) -> None:
        """Trigger the acquisition without waiting for a trigger event."""
        self.port.write(":TRIGger:FORCe")

    def is_acquisition_running(self) -> bool:
        """Return True while the scope is acquiring, using the Run bit (bit 3) of the operation status register."""
        self.port.write(":OPERegister:CONDition?")
        return bool(int(self.port.read()) & 8)

    def set_waveform_format(self) -> None:
        """Transfer waveforms as signed 16-bit integers, least significant byte first."""
        self.port.write(":WAVeform:FORMat WORD")
        self.port.write(":WAVeform:BYTeorder LSBFirst")
        self.port.write(":WAVeform:UNSigned OFF")
        # MAXimum returns the full acquisition record when the scope is stopped, otherwise the measurement record
        self.port.write(":WAVeform:POINts:MODE MAXimum")

    def set_waveform_points(self, points: str) -> None:
        """Set the maximum number of points to transfer, either an integer or 'MAXimum'."""
        self.port.write(f":WAVeform:POINts {points}")

    def set_waveform_source(self, source: str) -> None:
        """Select the source of the waveform transfer, e.g. 'CHANnel1'."""
        self.port.write(f":WAVeform:SOURce {source}")

    def get_waveform_preamble(self) -> dict[str, float]:
        """Return the scaling information of the current waveform source."""
        self.port.write(":WAVeform:PREamble?")
        values = self.port.read().split(",")
        return {
            "points": int(values[2]),
            "count": int(values[3]),
            "x_increment": float(values[4]),
            "x_origin": float(values[5]),
            "x_reference": float(values[6]),
            "y_increment": float(values[7]),
            "y_origin": float(values[8]),
            "y_reference": float(values[9]),
        }

    def get_waveform_data(self) -> NDArray[np.int16]:
        """Return the raw data of the current waveform source as IEEE 488.2 binary block."""
        self.port.write(":WAVeform:DATA?")
        # The port manager can only read text, so the binary block is read from the underlying pyvisa resource
        data: NDArray[np.int16] = self.port.port.read_binary_values(
            datatype="h",
            is_big_endian=False,
            container=np.array,
        )
        return data

    def set_acquisition_type(self, acquisition_type: str) -> None:
        """Set the acquisition type: NORMal, AVERage, HRESolution or PEAK."""
        self.port.write(f":ACQuire:TYPE {acquisition_type}")

    def set_average_count(self, count: int) -> None:
        """Set the number of averages, 2 to 65536."""
        self.port.write(f":ACQuire:COUNt {count}")

    def set_time_range(self, time_range: float) -> None:
        """Set the full-scale horizontal time in s (10 divisions)."""
        self.port.write(f":TIMebase:RANGe {time_range}")

    def set_time_scale(self, time_scale: float) -> None:
        """Set the horizontal scale in s/div."""
        self.port.write(f":TIMebase:SCALe {time_scale}")

    def set_time_position(self, position: float) -> None:
        """Set the time in s from the trigger event to the time reference point on the screen."""
        self.port.write(f":TIMebase:POSition {position}")

    def set_trigger_mode_edge(self) -> None:
        """Select the edge trigger."""
        self.port.write(":TRIGger:MODE EDGE")

    def set_trigger_source(self, source: str) -> None:
        """Set the source of the edge trigger, e.g. 'CHANnel1', 'EXTernal' or 'LINE'."""
        self.port.write(f":TRIGger:EDGE:SOURce {source}")

    def set_trigger_slope(self, slope: str) -> None:
        """Set the slope of the edge trigger: POSitive, NEGative, EITHer or ALTernate."""
        self.port.write(f":TRIGger:EDGE:SLOPe {slope}")

    def set_trigger_coupling(self, coupling: str) -> None:
        """Set the coupling of the edge trigger: AC, DC or LFReject."""
        self.port.write(f":TRIGger:EDGE:COUPling {coupling}")

    def set_trigger_level(self, level: float) -> None:
        """Set the trigger level in V of the current trigger source."""
        self.port.write(f":TRIGger:EDGE:LEVel {level}")

    def set_channel_display(self, channel: int, state: bool) -> None:
        """Switch a channel on or off."""
        self.port.write(f":CHANnel{channel}:DISPlay {'ON' if state else 'OFF'}")

    def set_channel_range(self, channel: int, channel_range: float) -> None:
        """Set the full-scale vertical range in V (8 divisions)."""
        self.port.write(f":CHANnel{channel}:RANGe {channel_range}")

    def set_channel_scale(self, channel: int, scale: float) -> None:
        """Set the vertical scale in V/div."""
        self.port.write(f":CHANnel{channel}:SCALe {scale}")

    def set_channel_offset(self, channel: int, offset: float) -> None:
        """Set the voltage in V at the center of the screen."""
        self.port.write(f":CHANnel{channel}:OFFSet {offset}")

    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """Set the input coupling: AC or DC."""
        self.port.write(f":CHANnel{channel}:COUPling {coupling}")

    def set_channel_impedance(self, channel: int, impedance: str) -> None:
        """Set the input impedance: ONEMeg or FIFTy."""
        self.port.write(f":CHANnel{channel}:IMPedance {impedance}")

    def set_channel_probe(self, channel: int, attenuation: float) -> None:
        """Set the probe attenuation factor."""
        self.port.write(f":CHANnel{channel}:PROBe {attenuation}")
