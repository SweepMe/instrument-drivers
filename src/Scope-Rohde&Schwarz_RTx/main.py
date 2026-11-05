# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024-2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Rohde&Schwarz RTx

from __future__ import annotations

import re
import time
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme.commands import Elements, Label, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call). The spellings are the
# keywords of the R&S RTO1000/RTO2000 (user manual 1332.9725.02) and RTE1000 (user manual 1326.1032.02) "Remote
# control commands" chapters; the instrument accepts the short and the long form. Ranges are declared only where the
# three manuals state the same bounds for every model; what differs per model is checked in the command.
Channel = Annotated[int, Selector(), Range(1, 4)]  # CHANnel<m>, m = 1..4; a two-channel model refuses 3 and 4
# TRIGger<m>:LEVel<n>: n = 1..4 selects the level of channel 1 to 4, 5 the level of the external trigger input
TriggerInput = Annotated[int, Selector(), Range(1, 5), Label("Trigger input")]
Volts = Annotated[float, Unit("V")]
Seconds = Annotated[float, Unit("s")]
SecondsPerDivision = Annotated[float, Unit("s/div"), Label("Time scale")]
VoltsPerDivision = Annotated[float, Unit("V/div"), Label("Voltage scale")]
Divisions = Annotated[float, Unit("div")]
SamplesPerSecond = Annotated[float, Unit("Sa/s"), Label("Sample rate")]
Times = Annotated[np.ndarray, Elements(Seconds)]
Voltages = Annotated[np.ndarray, Elements(Volts)]
ChannelCoupling = Literal["DC", "DCLimit", "AC"]  # CHANnel<m>:COUPling: DC = 50 Ohm, DCLimit = 1 MOhm, AC = 1 MOhm
# TRIGger<m>:SOURce, the analog sources; LINE is documented for the RTE only and refused on other families
TriggerSource = Literal["CHAN1", "CHAN2", "CHAN3", "CHAN4", "EXTernanalog", "SBUS", "LINE"]
# TRIGger<m>:TYPE, the types all three manuals list; the driver configures only EDGE and ANEDge
TriggerType = Literal[
    "EDGE",
    "GLITch",
    "WIDTh",
    "RUNT",
    "WINDow",
    "TIMeout",
    "INTerval",
    "SLEWrate",
    "STATe",
    "PATTern",
    "ANEDge",
    "SERPattern",
    "TV",
]
TriggerSlope = Literal["POSitive", "NEGative", "EITHer"]  # TRIGger<m>:EDGE:SLOPe
ExternalTriggerSlope = Literal["POSitive", "NEGative"]  # TRIGger<m>:ANEDge:SLOPe
TriggerMode = Literal["AUTO", "NORMal", "FREerun"]  # TRIGger<m>:MODE
# FORMat[:DATA]; REAL,64 exists on the RTO2000 with firmware 5.60 only and is left out
DataFormat = Literal["ASCii", "REAL,32", "INT,8", "INT,16"]
ByteOrder = Literal["LSBFirst", "MSBFirst"]  # FORMat:BORDer
RecordLengthMode = Literal["RESolution", "RECLength"]  # ACQuire:POINts:AUTO
DecimationMode = Literal["SAMPle", "PDETect", "HRESolution", "RMS"]  # CHANnel<m>:TYPE
WaveformArithmetics = Literal["OFF", "ENVelope", "AVERage"]  # CHANnel<m>:ARIThmetics

# Scope module labels -> instrument keywords
TRIGGER_SOURCES: dict[str, TriggerSource] = {
    "Channel 1": "CHAN1",
    "Channel 2": "CHAN2",
    "Channel 3": "CHAN3",
    "Channel 4": "CHAN4",
    "External": "EXTernanalog",
    "Line": "LINE",
    "Serial bus": "SBUS",
}
# The trigger sources whose level TRIGger<m>:LEVel<n> can set, with their suffix n
TRIGGER_INPUTS: dict[str, int] = {"Channel 1": 1, "Channel 2": 2, "Channel 3": 3, "Channel 4": 4, "External": 5}
TRIGGER_SLOPES: dict[str, TriggerSlope] = {"Rising": "POSitive", "Falling": "NEGative"}
TRIGGER_COUPLINGS: dict[str, ChannelCoupling] = {"DC": "DC", "DCLimit": "DCLimit", "AC": "AC"}
CHANNEL_COUPLINGS: dict[str, ChannelCoupling] = {"DC 50 Ohm": "DC", "DC 1 MOhm": "DCLimit", "AC 1 MOhm": "AC"}
# Largest time scale (TIMebase:SCALe) and acquisition time (TIMebase:RANGe) per family: "25E-12 to 10000 (RTO, RTP) |
# 5000 (RTE)" and "250E-12 to 100E+3 (RTO, RTP) | 50E+3 (RTE)"
TIME_SCALE_MAXIMUM: dict[str, float] = {"RTO": 10000.0, "RTP": 10000.0, "RTE": 5000.0}
TIME_RANGE_MAXIMUM: dict[str, float] = {"RTO": 100e3, "RTP": 100e3, "RTE": 50e3}
# Bit 0 of the event status register, set by *OPC once all preceding commands have been executed (appendix "Command
# sequence and synchronization" of the manuals)
OPERATION_COMPLETE_BIT = 1
# Pause between two polls of the event status register while a single acquisition runs
POLL_INTERVAL = 0.05
# The channel counts the K-code of the order number in the *IDN? answer can encode (e.g. 1329.7002k24 = RTO2024)
CHANNEL_COUNTS = (2, 4)
# A waveform header answers one value per sample interval in SAMPle, HRESolution and RMS decimation; 2 in PDETect and
# envelope mode, which the trace reader does not unpack
VALUES_PER_SAMPLE = 1


class Device(EmptyDevice):
    """Driver for the analog channels of Rohde&Schwarz RTO1000, RTO2000 and RTE1000 oscilloscopes."""

    def __init__(self) -> None:
        """Define the returned variables, the port and the default values of every attribute."""
        super().__init__()

        self.shortname = "RTx"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]
        # A long ASCII waveform takes a while to transfer, hence a longer timeout than the default of 2 s
        self.port_properties = {"timeout": 10.0}

        # GUI parameters, exactly as they arrive from the GUI; converted in configure()
        self.gui_parameters: dict[str, Any] = {}
        self.channels: list[int] = []

        # Values derived from the GUI parameters in configure()
        self.sweep_mode: str = "None"
        self.trigger_source: str = "As is"
        self.trigger_coupling: str = "As is"
        self.trigger_slope: str = "As is"
        self.trigger_level: float | None = None
        self.trigger_timeout: float = 30.0
        self.time_range: str = "As is"
        self.time_range_value: float = 1e-3
        self.time_offset_value: float = 0.0
        self.acquisition: str = "As is"
        self.average: str = "As is"
        self.sampling_rate_type: str = "As is sampling rate"
        self.sampling_rate: str = "As is"
        self.channel_ranges: dict[int, str] = {}
        self.channel_offsets: dict[int, str] = {}
        self.channel_impedances: dict[int, str] = {}
        self.channel_couplings: dict[int, str] = {}

        # Instrument properties read in initialize()
        self.identification: str = ""
        self.model_family: str = ""  # "RTO", "RTE" or "RTP" from the *IDN? answer; "" when unknown
        self.channel_count: int = 0  # 2 or 4 from the *IDN? answer; 0 when unknown, which checks nothing

        # Measured data
        self.times: np.ndarray = np.array([])
        self.voltages: list[np.ndarray] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields of the Scope module with their defaults."""
        new_parameters: dict[str, Any] = {
            "SweepMode": ["None", "Time range in s", "Time scale in s/div", "Time offset in s"],
            "TriggerSlope": ["As is", *TRIGGER_SLOPES],
            "TriggerSource": ["As is", *TRIGGER_SOURCES, "Software"],
            "TriggerCoupling": ["As is", *TRIGGER_COUPLINGS],
            "TriggerLevel": "As is",
            "TriggerTimeout": 30.0,
            "TimeRange": ["As is", "Time range in s:", "Time scale in s/div:"],
            "TimeRangeValue": 1e-3,
            "TimeOffsetValue": 0.0,
            "Acquisition": ["As is", "Continuous", "Single"],
            "Average": ["As is", "1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "SamplingRateType": [
                "As is sampling rate",
                "Auto sampling rate",
                "Sampling rate in Sa/s:",
                "Sample resolution in s:",
                "Samples per time range:",
            ],
            "SamplingRate": "As is",
        }

        for i in range(1, 5):
            new_parameters[f"Channel{i}"] = i == 1
            new_parameters[f"Channel{i}_Name"] = f"Ch{i}"
            new_parameters[f"Channel{i}_Range"] = [
                "As is",
                "0.01",
                "0.02",
                "0.05",
                "0.1",
                "0.2",
                "0.5",
                "1",
                "2",
                "5",
                "10",
                "20",
                "50",
                "100",
            ]
            new_parameters[f"Channel{i}_Offset"] = "As is"
            new_parameters[f"Channel{i}_Impedance"] = ["As is", "50 Ohm"]
            new_parameters[f"Channel{i}_Coupling"] = ["As is", *CHANNEL_COUPLINGS]

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the raw GUI parameters and derive the returned variables from the selected channels.

        The values are converted to numbers in configure(), so that a later call of this function with the raw
        strings cannot revert converted values.
        """
        self.gui_parameters = dict(parameters)

        self.channels = [i for i in range(1, 5) if parameters.get(f"Channel{i}", False)]

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]
        self.savetype = [True]

        for i in self.channels:
            name = str(parameters.get(f"Channel{i}_Name", f"Ch{i}"))
            self.variables.append(name if name != "" else f"Ch{i}")
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self) -> None:
        """Identify the instrument, check the user input and set the data format, once per run.

        The driver deliberately sends no reset or preset, so that everything the GUI leaves "As is" stays as set on
        the instrument.
        """
        self.identification = self.get_identification()
        self.model_family, self.channel_count = self._parse_identification(self.identification)

        if len(self.channels) == 0:
            msg = "Scope-Rohde&Schwarz_RTx: Please select at least one channel to be read out."
            raise ValueError(msg)
        if self.channel_count and max(self.channels) > self.channel_count:
            msg = (
                f"Scope-Rohde&Schwarz_RTx: The connected model has {self.channel_count} channels, but channel "
                f"{max(self.channels)} is selected."
            )
            raise ValueError(msg)
        self._convert_gui_parameters()

        self.clear_status()
        # The trace reader parses comma-separated ASCII values
        self.set_data_format("ASCii")
        self.set_display_update(True)

    def configure(self) -> None:
        """Convert the GUI parameters and write the timebase, trigger, acquisition and channel settings."""
        self._convert_gui_parameters()
        self._configure_timebase()
        self._configure_trigger()
        self._configure_acquisition()
        self._configure_sample_rate()
        self._configure_channels()
        # Make sure all settings are processed before the error queue is read
        self.wait_for_operation_complete()
        self._raise_on_errors()

    def apply(self) -> None:
        """Set the new sweep value of the timebase."""
        if self.sweep_mode.startswith("Time range"):
            self.set_time_range(float(self.value))
        elif self.sweep_mode.startswith("Time scale"):
            self.set_time_scale(float(self.value))
        elif self.sweep_mode.startswith("Time offset"):
            self.set_horizontal_position(float(self.value))

    def measure(self) -> None:
        """Acquire a single acquisition if configured, then read the waveform of every selected channel."""
        # Restart the averaging so that only fresh acquisitions enter the waveform
        self.reset_waveform_arithmetics()

        if self.acquisition == "Single":
            # *CLS clears a stale operation-complete bit before the acquisition is started
            self.clear_status()
            self.run_single()
            if self.trigger_source == "Software":
                self.force_trigger()
            self._wait_for_single_acquisition()
            if self.is_run_stopped():
                return
        else:
            if self.trigger_source == "Software":
                self.force_trigger()
            self.wait_for_operation_complete()

        self.voltages = []
        for i in self.channels:
            times, voltages = self.get_trace(i)
            if i == self.channels[0]:
                self.times = times
            self.voltages.append(voltages)

    def call(self) -> list[np.ndarray]:
        """Return the time axis and one trace per selected channel."""
        return [self.times, *self.voltages]

    # -- Helpers of the semantic functions ----------------------------------------------------------------------------

    def _convert_gui_parameters(self) -> None:
        """Convert the stored GUI parameters to numbers and check them, with a message for the user.

        Done here and not in apply_gui_parameters(), which may be called with incomplete fields while the user is
        still editing them; the converted values live in attributes of their own.
        """
        parameters = self.gui_parameters

        self.sweep_mode = str(parameters.get("SweepMode", "None"))
        self.trigger_source = str(parameters.get("TriggerSource", "As is"))
        self.trigger_coupling = str(parameters.get("TriggerCoupling", "As is"))
        self.trigger_slope = str(parameters.get("TriggerSlope", "As is"))
        self.time_range = str(parameters.get("TimeRange", "As is"))
        self.acquisition = str(parameters.get("Acquisition", "As is"))
        self.average = str(parameters.get("Average", "As is"))
        self.sampling_rate_type = str(parameters.get("SamplingRateType", "As is sampling rate"))
        self.sampling_rate = str(parameters.get("SamplingRate", "As is")).strip()

        try:
            trigger_level = str(parameters.get("TriggerLevel", "As is")).strip()
            self.trigger_level = None if trigger_level in ("", "As is") else float(trigger_level)
            self.trigger_timeout = float(parameters.get("TriggerTimeout", 30.0))
            self.time_range_value = float(parameters.get("TimeRangeValue", 1e-3))
            self.time_offset_value = float(parameters.get("TimeOffsetValue", 0.0))
            if self.sampling_rate != "As is" and not self.sampling_rate_type.startswith(("As is", "Auto")):
                float(self.sampling_rate)
        except ValueError as e:
            msg = f"Scope-Rohde&Schwarz_RTx: Please enter numeric values into all number fields. Error is: {e}"
            raise ValueError(msg) from e

        self.channel_ranges = {i: str(parameters.get(f"Channel{i}_Range", "As is")).strip() for i in self.channels}
        self.channel_offsets = {i: str(parameters.get(f"Channel{i}_Offset", "As is")).strip() for i in self.channels}
        self.channel_impedances = {i: str(parameters.get(f"Channel{i}_Impedance", "As is")) for i in self.channels}
        self.channel_couplings = {i: str(parameters.get(f"Channel{i}_Coupling", "As is")) for i in self.channels}

        self._check_gui_parameters()

    def _check_gui_parameters(self) -> None:
        """Raise with a message for the user when a converted GUI parameter is not supported."""
        self._check_trigger_and_acquisition_parameters()
        self._check_channel_parameters()

    def _check_trigger_and_acquisition_parameters(self) -> None:
        """Raise when a trigger, timebase or acquisition parameter is not supported."""
        if self.trigger_source not in ("As is", "Software", *TRIGGER_SOURCES):
            msg = f"Scope-Rohde&Schwarz_RTx: Unknown trigger source '{self.trigger_source}'."
            raise ValueError(msg)
        if self.trigger_slope not in ("As is", *TRIGGER_SLOPES):
            msg = f"Scope-Rohde&Schwarz_RTx: Unknown trigger slope '{self.trigger_slope}'."
            raise ValueError(msg)
        if self.trigger_coupling not in ("As is", *TRIGGER_COUPLINGS):
            msg = f"Scope-Rohde&Schwarz_RTx: Unknown trigger coupling '{self.trigger_coupling}'."
            raise ValueError(msg)
        if self.acquisition not in ("As is", "Continuous", "Single"):
            msg = f"Scope-Rohde&Schwarz_RTx: Acquisition mode '{self.acquisition}' is not supported."
            raise ValueError(msg)
        if self.average != "As is" and int(self.average) < 1:
            msg = "Scope-Rohde&Schwarz_RTx: The number of averages must be at least 1."
            raise ValueError(msg)
        if self.trigger_timeout <= 0.0:
            msg = "Scope-Rohde&Schwarz_RTx: The trigger timeout must be larger than 0 s."
            raise ValueError(msg)
        if self.time_range != "As is" and self.time_range_value <= 0.0:
            msg = "Scope-Rohde&Schwarz_RTx: The time range or time scale must be a positive number."
            raise ValueError(msg)

    def _check_channel_parameters(self) -> None:
        """Raise when a range, offset, impedance or coupling of a selected channel is not supported."""
        for i in self.channels:
            for field, text in (("range", self.channel_ranges[i]), ("offset", self.channel_offsets[i])):
                if text not in ("", "As is"):
                    try:
                        float(text)
                    except ValueError as e:
                        msg = f"Scope-Rohde&Schwarz_RTx: The {field} of channel {i} must be a number, not '{text}'."
                        raise ValueError(msg) from e
            if self.channel_impedances[i] not in ("As is", "50 Ohm"):
                msg = f"Scope-Rohde&Schwarz_RTx: Unknown impedance '{self.channel_impedances[i]}' of channel {i}."
                raise ValueError(msg)
            if self.channel_couplings[i] not in ("As is", *CHANNEL_COUPLINGS):
                msg = f"Scope-Rohde&Schwarz_RTx: Unknown coupling '{self.channel_couplings[i]}' of channel {i}."
                raise ValueError(msg)
            if self.channel_impedances[i] == "50 Ohm" and self.channel_couplings[i] in ("DC 1 MOhm", "AC 1 MOhm"):
                msg = (
                    f"Scope-Rohde&Schwarz_RTx: Channel {i} cannot have 50 Ohm impedance and the coupling "
                    f"'{self.channel_couplings[i]}' at the same time; the 50 Ohm termination is the coupling "
                    "'DC 50 Ohm'."
                )
                raise ValueError(msg)

    def _configure_timebase(self) -> None:
        """Write the acquisition time or the time scale, and the horizontal position, where not "As is"."""
        if self.time_range == "As is":
            return
        if self.time_range.startswith("Time range"):
            self.set_time_range(self.time_range_value)
        elif self.time_range.startswith("Time scale"):
            self.set_time_scale(self.time_range_value)
        self.set_horizontal_position(self.time_offset_value)

    def _configure_trigger(self) -> None:
        """Write the A trigger: normal mode, then source, level, type, slope and coupling where not "As is".

        The external trigger input uses the analog edge trigger type (ANEDge) with its own slope and coupling
        commands; every other source uses the edge trigger type (EDGE).
        """
        # A waveform is only acquired if a trigger occurs; a software trigger is forced in measure()
        self.set_trigger_mode("NORMal")

        if self.trigger_source not in ("As is", "Software"):
            self.set_trigger_source(TRIGGER_SOURCES[self.trigger_source])
            if self.trigger_source in TRIGGER_INPUTS and self.trigger_level is not None:
                self.set_trigger_level(TRIGGER_INPUTS[self.trigger_source], self.trigger_level)

        if self.trigger_source == "External":
            self.set_trigger_type("ANEDge")
            if self.trigger_coupling != "As is":
                self.set_external_trigger_coupling(TRIGGER_COUPLINGS[self.trigger_coupling])
            if self.trigger_slope != "As is":
                self.set_external_trigger_slope(TRIGGER_SLOPES[self.trigger_slope])
        else:
            if self.trigger_source != "As is":
                self.set_trigger_type("EDGE")
            if self.trigger_slope != "As is":
                self.set_trigger_slope(TRIGGER_SLOPES[self.trigger_slope])

    def _configure_acquisition(self) -> None:
        """Start or stop the acquisition and write the acquisition count with the waveform arithmetic.

        A single acquisition is started in measure(), so the running acquisition is stopped here. The acquisition
        count is the number of waveforms of a single acquisition and of the average; the average is switched on for
        the selected channels when the count is larger than 1 and off for a count of 1.
        """
        if self.acquisition == "Continuous":
            self.run_continuous()
        elif self.acquisition == "Single":
            self.stop()

        if self.average != "As is":
            count = int(self.average)
            self.set_acquisition_count(count)
            for i in self.channels:
                self.set_waveform_arithmetics(i, "AVERage" if count > 1 else "OFF")

    def _configure_sample_rate(self) -> None:
        """Write the sample rate, the resolution or the record length, or keep the resolution constant."""
        if self.sampling_rate_type.startswith("As is"):
            return
        if self.sampling_rate_type.startswith("Auto"):
            self.set_record_length_mode("RESolution")
        elif self.sampling_rate != "As is":
            if self.sampling_rate_type.startswith("Sampling rate"):
                self.set_sample_rate(float(self.sampling_rate))
            elif self.sampling_rate_type.startswith("Sample resolution"):
                self.set_resolution(float(self.sampling_rate))
            elif self.sampling_rate_type.startswith("Samples per time range"):
                self.set_record_length(int(float(self.sampling_rate)))

    def _configure_channels(self) -> None:
        """Switch the unselected channels off and the selected ones on, and write their settings.

        Unselected channels are switched off because they may still be on from an earlier run. The coupling is
        written before the range, because the range limits depend on the input termination.
        """
        channel_count = self.channel_count if self.channel_count else max(CHANNEL_COUNTS)
        for i in range(1, channel_count + 1):
            if i not in self.channels:
                self.set_channel_active(i, False)

        for i in self.channels:
            self.set_channel_active(i, True)
            self.set_decimation_mode(i, "SAMPle")
            if self.channel_impedances[i] == "50 Ohm":
                # The 50 Ohm termination is selected through the coupling (CHANnel<m>:COUPling DC)
                self.set_coupling(i, "DC")
            elif self.channel_couplings[i] != "As is":
                self.set_coupling(i, CHANNEL_COUPLINGS[self.channel_couplings[i]])
            if self.channel_ranges[i] not in ("", "As is"):
                self.set_voltage_range(i, float(self.channel_ranges[i]))
            if self.channel_offsets[i] not in ("", "As is"):
                self.set_voltage_offset(i, float(self.channel_offsets[i]))

    def _wait_for_single_acquisition(self) -> None:
        """Wait until the single acquisition has completed, bounded by the trigger timeout.

        Follows the polling method of the manuals' appendix "Command sequence and synchronization": *OPC sets the
        operation-complete bit of the event status register once the acquisition has finished, and *ESR? is polled
        for it. The enable mask (*ESE) of that method only matters for service requests, which the driver does not
        use.
        """
        self.request_operation_complete()
        start = time.time()
        while not self.is_run_stopped():
            if self.get_event_status() & OPERATION_COMPLETE_BIT:
                return
            if time.time() - start > self.trigger_timeout:
                msg = (
                    f"Scope-Rohde&Schwarz_RTx: The acquisition did not complete within {self.trigger_timeout} s. "
                    "Please check the trigger source, level and slope, or increase the trigger timeout."
                )
                raise TimeoutError(msg)
            time.sleep(POLL_INTERVAL)

    def _raise_on_errors(self) -> None:
        """Read the error queue and raise with the messages the instrument reported."""
        errors = self.get_errors()
        if errors:
            msg = f"Scope-Rohde&Schwarz_RTx: The instrument reported errors: {'; '.join(errors)}"
            raise ValueError(msg)

    def _check_channel(self, channel: int) -> None:
        """Raise when the connected model does not have the channel."""
        if self.channel_count and channel > self.channel_count:
            msg = f"The connected model has {self.channel_count} channels, channel {channel} does not exist."
            raise ValueError(msg)

    # -- Communication commands ---------------------------------------------------------------------------------------
    # One instrument command each, declared with pysweepme's @command. The commands send the keywords in their long
    # form. All trigger commands address the A trigger (suffix 1); the trigger mode and the force command take no
    # suffix ("irrelevant, omit the suffix" in the manuals). Section titles refer to the RTO1000 manual 1332.9725.02
    # version 11 (firmware 3.70); the RTO2000 (version 30, firmware 5.60) and RTE (1326.1032.02 version 21, firmware
    # 4.80) manuals document the same commands unless noted.

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the instrument (*IDN?), e.g. Rohde&Schwarz,RTO,1329.7002k24/...,3.50."""
        return str(self.port.query("*IDN?")).strip()

    @command
    def reset(self) -> None:
        """Reset the instrument to its default state (*RST)."""
        self.port.write("*RST")

    @command
    def clear_status(self) -> None:
        """Clear the status registers and the error queue (*CLS)."""
        self.port.write("*CLS")

    @command
    def request_operation_complete(self) -> None:
        """Set bit 0 of the event status register once all preceding commands have been executed (*OPC)."""
        self.port.write("*OPC")

    @command(returns=("event_status",), reads="state")
    def get_event_status(self) -> int:
        """Return and clear the event status register (*ESR?); bit 0 is set once *OPC has completed."""
        return int(self.port.query("*ESR?").strip())

    @command
    def wait_for_operation_complete(self) -> None:
        """Wait until all preceding commands have been executed (*OPC?), bounded by the port timeout."""
        answer = self.port.query("*OPC?").strip()
        if answer != "1":
            msg = f"Unexpected answer to *OPC?: {answer!r}"
            raise ValueError(msg)

    @command(returns=("errors",), reads="state")
    def get_errors(self) -> list[str]:
        """Return and remove all entries of the error queue as 'code,message' (SYSTem:ERRor:ALL?); empty if none."""
        answer = self.port.query("SYSTem:ERRor:ALL?").strip()
        # One answer holds all entries, e.g. -222,"Data out of range;TIM:SCAL 1E-20",-113,"Undefined header"
        return [f"{code},{text}" for code, text in re.findall(r'(-?\d+),"((?:[^"]|"")*)"', answer) if int(code) != 0]

    @command(returns=("error_codes",), reads="state")
    def get_error_codes(self) -> list[int]:
        """Return and remove all entries of the error queue as codes (SYSTem:ERRor:CODE:ALL?); empty if none."""
        answer = self.port.query("SYSTem:ERRor:CODE:ALL?").strip()
        return [int(code) for code in answer.split(",") if int(code) != 0]

    @command(returns=("error_count",), reads="state")
    def get_error_count(self) -> int:
        """Return the number of entries in the error queue (SYSTem:ERRor:COUNt?)."""
        return int(self.port.query("SYSTem:ERRor:COUNt?").strip())

    # -- General remote settings: FORMat and SYSTem:DISPlay --

    @command
    def set_data_format(self, data_format: DataFormat) -> None:
        """Set the format of the waveform data query (FORMat[:DATA]); the driver reads ASCii."""
        self.port.write(f"FORMat:DATA {data_format}")

    @command(returns=("data_format",), reads="setpoint")
    def get_data_format(self) -> str:
        """Return the format of the waveform data query, e.g. ASC,0 or REAL,32."""
        return str(self.port.query("FORMat:DATA?")).strip()

    @command
    def set_byte_order(self, byte_order: ByteOrder) -> None:
        """Set the byte order of INT,16 waveform data (FORMat:BORDer)."""
        self.port.write(f"FORMat:BORDer {byte_order}")

    @command(returns=("byte_order",), reads="setpoint")
    def get_byte_order(self) -> str:
        """Return the byte order of INT,16 waveform data, LSBF or MSBF."""
        return str(self.port.query("FORMat:BORDer?")).strip()

    @command
    def set_display_update(self, display_update: bool) -> None:
        """Switch the display update during remote control on or off (SYSTem:DISPlay:UPDate); off is faster."""
        self.port.write(f"SYSTem:DISPlay:UPDate {'ON' if display_update else 'OFF'}")

    @command(returns=("display_update",), reads="setpoint")
    def get_display_update(self) -> bool:
        """Return whether the display is updated during remote control."""
        return self._is_on(self.port.query("SYSTem:DISPlay:UPDate?"))

    # -- Starting and stopping the acquisition --

    @command
    def run_continuous(self) -> None:
        """Start the continuous acquisition (RUN)."""
        self.port.write("RUN")

    @command
    def run_single(self) -> None:
        """Start a single acquisition of the number of waveforms set with set_acquisition_count (SINGle)."""
        self.port.write("SINGle")

    @command
    def stop(self) -> None:
        """Stop the running acquisition (STOP)."""
        self.port.write("STOP")

    # -- Time base --

    @command
    def set_time_scale(self, time_scale: Annotated[SecondsPerDivision, Range(25e-12, None)]) -> None:
        """Set the time per division (TIMebase:SCALe); at most 10000 s/div on an RTO or RTP, 5000 s/div on an RTE."""
        self._check_maximum("time scale", time_scale, TIME_SCALE_MAXIMUM)
        self.port.write(f"TIMebase:SCALe {time_scale}")

    @command(returns=("time_scale",), reads="setpoint")
    def get_time_scale(self) -> SecondsPerDivision:
        """Return the time per division in s/div."""
        return float(self.port.query("TIMebase:SCALe?"))

    @command
    def set_time_range(self, time_range: Annotated[Seconds, Range(250e-12, None)]) -> None:
        """Set the acquisition time across the 10 divisions (TIMebase:RANGe); at most 100 ks (RTO) or 50 ks (RTE)."""
        self._check_maximum("time range", time_range, TIME_RANGE_MAXIMUM)
        self.port.write(f"TIMebase:RANGe {time_range}")

    @command(returns=("time_range",), reads="setpoint")
    def get_time_range(self) -> Seconds:
        """Return the acquisition time in s."""
        return float(self.port.query("TIMebase:RANGe?"))

    @command
    def set_horizontal_position(self, horizontal_position: Annotated[Seconds, Range(-100e24, 100e24)]) -> None:
        """Set the time between the reference point and the trigger point (TIMebase:HORizontal:POSition)."""
        self.port.write(f"TIMebase:HORizontal:POSition {horizontal_position}")

    @command(returns=("horizontal_position",), reads="setpoint")
    def get_horizontal_position(self) -> Seconds:
        """Return the time between the reference point and the trigger point in s."""
        return float(self.port.query("TIMebase:HORizontal:POSition?"))

    @command
    def set_record_length_mode(self, record_length_mode: RecordLengthMode) -> None:
        """Keep the resolution or the record length constant when the time scale changes (ACQuire:POINts:AUTO)."""
        self.port.write(f"ACQuire:POINts:AUTO {record_length_mode}")

    @command(returns=("record_length_mode",), reads="setpoint")
    def get_record_length_mode(self) -> str:
        """Return what is kept constant when the time scale changes, RES or RECL."""
        return str(self.port.query("ACQuire:POINts:AUTO?")).strip()

    @command
    def set_sample_rate(self, sample_rate: SamplesPerSecond) -> None:
        """Set the number of captured waveform points per second (ACQuire:SRReal, firmware 3.40 or newer).

        The accepted range depends on the model (up to 20 GSa/s with interpolation off on an RTO1000), so none is
        declared; the instrument refuses what it cannot do.
        """
        self.port.write(f"ACQuire:SRReal {sample_rate}")

    @command(returns=("sample_rate",), reads="setpoint")
    def get_sample_rate(self) -> SamplesPerSecond:
        """Return the number of captured waveform points per second in Sa/s."""
        return float(self.port.query("ACQuire:SRReal?"))

    @command
    def set_resolution(self, resolution: Annotated[Seconds, Range(1e-15, 0.5)]) -> None:
        """Set the time between two waveform points (ACQuire:RESolution)."""
        self.port.write(f"ACQuire:RESolution {resolution}")

    @command(returns=("resolution",), reads="setpoint")
    def get_resolution(self) -> Seconds:
        """Return the time between two waveform points in s."""
        return float(self.port.query("ACQuire:RESolution?"))

    @command
    def set_record_length(self, record_length: Annotated[int, Range(1000, 1_000_000_000)]) -> None:
        """Set the number of waveform points across the acquisition time (ACQuire:POINts)."""
        self.port.write(f"ACQuire:POINts:VALue {record_length}")

    @command(returns=("record_length",), reads="setpoint")
    def get_record_length(self) -> int:
        """Return the number of waveform points across the acquisition time."""
        return int(float(self.port.query("ACQuire:POINts:VALue?")))

    # -- Acquisition --

    @command
    def set_acquisition_count(self, acquisition_count: Annotated[int, Range(1, 16777215)]) -> None:
        """Set the number of waveforms of a single acquisition and of the average (ACQuire:COUNt)."""
        self.port.write(f"ACQuire:COUNt {acquisition_count}")

    @command(returns=("acquisition_count",), reads="setpoint")
    def get_acquisition_count(self) -> int:
        """Return the number of waveforms of a single acquisition and of the average."""
        return int(float(self.port.query("ACQuire:COUNt?")))

    @command(returns=("acquisition_number",), reads="state")
    def get_acquisition_number(self) -> int:
        """Return the number of acquisitions acquired so far (ACQuire:CURRent?)."""
        return int(float(self.port.query("ACQuire:CURRent?")))

    @command
    def reset_waveform_arithmetics(self) -> None:
        """Restart the average and envelope calculation of all waveforms (ACQuire:ARESet:IMMediate)."""
        self.port.write("ACQuire:ARESet:IMMediate")

    # -- Trigger: the A trigger (suffix 1) --

    @command
    def set_trigger_mode(self, trigger_mode: TriggerMode) -> None:
        """Set what happens without a trigger (TRIGger:MODE): AUTO triggers anyway, NORMal waits, FREerun ignores."""
        self.port.write(f"TRIGger:MODE {trigger_mode}")

    @command(returns=("trigger_mode",), reads="setpoint")
    def get_trigger_mode(self) -> str:
        """Return the trigger mode, AUTO, NORM or FRE."""
        return str(self.port.query("TRIGger:MODE?")).strip()

    # check_driver: ignore DC012 - LINE is checked against the connected model family, not against the choices
    @command
    def set_trigger_source(self, trigger_source: TriggerSource) -> None:
        """Set the source of the A trigger (TRIGger1:SOURce); LINE exists on the RTE only."""
        if trigger_source == "LINE" and self.model_family and self.model_family != "RTE":
            msg = f"The trigger source LINE is documented for the RTE only, not for the connected {self.model_family}."
            raise ValueError(msg)
        if trigger_source.startswith("CHAN"):
            self._check_channel(int(trigger_source[-1]))
        self.port.write(f"TRIGger1:SOURce {trigger_source}")

    @command(returns=("trigger_source",), reads="setpoint")
    def get_trigger_source(self) -> str:
        """Return the source of the A trigger, e.g. CHAN1, EXT or SBUS."""
        return str(self.port.query("TRIGger1:SOURce?")).strip()

    @command
    def set_trigger_type(self, trigger_type: TriggerType) -> None:
        """Set the type of the A trigger (TRIGger1:TYPE); ANEDge is the only type of the external trigger input."""
        self.port.write(f"TRIGger1:TYPE {trigger_type}")

    @command(returns=("trigger_type",), reads="setpoint")
    def get_trigger_type(self) -> str:
        """Return the type of the A trigger, e.g. EDGE or ANED."""
        return str(self.port.query("TRIGger1:TYPE?")).strip()

    @command
    def set_trigger_level(self, trigger_input: TriggerInput, trigger_level: Volts) -> None:
        """Set the A trigger level of a channel (1 to 4) or of the external trigger input (5) (TRIGger1:LEVel<n>).

        The level must lie within the display range of the source; the instrument refuses other values.
        """
        if trigger_input in range(1, 5):
            self._check_channel(trigger_input)
        self.port.write(f"TRIGger1:LEVel{trigger_input} {trigger_level}")

    @command(returns=("trigger_level",), reads="setpoint")
    def get_trigger_level(self, trigger_input: TriggerInput) -> Volts:
        """Return the A trigger level of a channel (1 to 4) or of the external trigger input (5) in V."""
        if trigger_input in range(1, 5):
            self._check_channel(trigger_input)
        return float(self.port.query(f"TRIGger1:LEVel{trigger_input}?"))

    @command
    def set_trigger_slope(self, trigger_slope: TriggerSlope) -> None:
        """Set the slope of the A edge trigger (TRIGger1:EDGE:SLOPe)."""
        self.port.write(f"TRIGger1:EDGE:SLOPe {trigger_slope}")

    @command(returns=("trigger_slope",), reads="setpoint")
    def get_trigger_slope(self) -> str:
        """Return the slope of the A edge trigger, POS, NEG or EITH."""
        return str(self.port.query("TRIGger1:EDGE:SLOPe?")).strip()

    @command
    def set_external_trigger_coupling(self, external_trigger_coupling: ChannelCoupling) -> None:
        """Set the coupling of the external trigger input (TRIGger1:ANEDge:COUPling): DC 50 Ohm, DCLimit 1 MOhm, AC."""
        self.port.write(f"TRIGger1:ANEDge:COUPling {external_trigger_coupling}")

    @command(returns=("external_trigger_coupling",), reads="setpoint")
    def get_external_trigger_coupling(self) -> str:
        """Return the coupling of the external trigger input, DC, DCL or AC."""
        return str(self.port.query("TRIGger1:ANEDge:COUPling?")).strip()

    @command
    def set_external_trigger_slope(self, external_trigger_slope: ExternalTriggerSlope) -> None:
        """Set the slope of the analog edge trigger on the external trigger input (TRIGger1:ANEDge:SLOPe)."""
        self.port.write(f"TRIGger1:ANEDge:SLOPe {external_trigger_slope}")

    @command(returns=("external_trigger_slope",), reads="setpoint")
    def get_external_trigger_slope(self) -> str:
        """Return the slope of the analog edge trigger on the external trigger input, POS or NEG."""
        return str(self.port.query("TRIGger1:ANEDge:SLOPe?")).strip()

    @command
    def force_trigger(self) -> None:
        """Provoke an immediate single acquisition while the acquisition waits for a trigger (TRIGger:FORCe)."""
        self.port.write("TRIGger:FORCe")

    # -- Channels: the CHANnel<m> commands --

    @command
    def set_channel_active(self, channel: Channel, active: bool) -> None:
        """Switch the channel signal on or off (CHANnel<m>:STATe)."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:STATe {'ON' if active else 'OFF'}")

    @command(returns=("active",), reads="setpoint")
    def get_channel_active(self, channel: Channel) -> bool:
        """Return whether the channel signal is on."""
        self._check_channel(channel)
        return self._is_on(self.port.query(f"CHANnel{channel}:STATe?"))

    @command
    def set_decimation_mode(self, channel: Channel, decimation_mode: DecimationMode) -> None:
        """Set how the ADC samples are reduced to waveform points (CHANnel<m>:TYPE), e.g. SAMPle or PDETect."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:TYPE {decimation_mode}")

    @command(returns=("decimation_mode",), reads="setpoint")
    def get_decimation_mode(self, channel: Channel) -> str:
        """Return the decimation mode of the channel, SAMP, PDET, HRES or RMS."""
        self._check_channel(channel)
        return str(self.port.query(f"CHANnel{channel}:TYPE?")).strip()

    @command
    def set_waveform_arithmetics(self, channel: Channel, waveform_arithmetics: WaveformArithmetics) -> None:
        """Set how consecutive acquisitions build the waveform (CHANnel<m>:ARIThmetics): OFF, ENVelope or AVERage."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:ARIThmetics {waveform_arithmetics}")

    @command(returns=("waveform_arithmetics",), reads="setpoint")
    def get_waveform_arithmetics(self, channel: Channel) -> str:
        """Return the waveform arithmetic of the channel, OFF, ENV or AVER."""
        self._check_channel(channel)
        return str(self.port.query(f"CHANnel{channel}:ARIThmetics?")).strip()

    @command
    def set_coupling(self, channel: Channel, coupling: ChannelCoupling) -> None:
        """Set the input coupling (CHANnel<m>:COUPling): DC is 50 Ohm, DCLimit 1 MOhm, AC 1 MOhm through a capacitor."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:COUPling {coupling}")

    @command(returns=("coupling",), reads="setpoint")
    def get_coupling(self, channel: Channel) -> str:
        """Return the input coupling of the channel, DC, DCL or AC."""
        self._check_channel(channel)
        return str(self.port.query(f"CHANnel{channel}:COUPling?")).strip()

    @command
    def set_voltage_range(self, channel: Channel, voltage_range: Volts) -> None:
        """Set the voltage range across the 10 vertical divisions (CHANnel<m>:RANGe).

        With a 1:1 probe the range is 10 mV to 10 V at 50 Ohm and 10 mV to 100 V at 1 MOhm, multiplied by the
        attenuation of the probe, so none is declared.
        """
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:RANGe {voltage_range}")

    @command(returns=("voltage_range",), reads="setpoint")
    def get_voltage_range(self, channel: Channel) -> Volts:
        """Return the voltage range across the 10 vertical divisions in V."""
        self._check_channel(channel)
        return float(self.port.query(f"CHANnel{channel}:RANGe?"))

    @command
    def set_voltage_scale(self, channel: Channel, voltage_scale: VoltsPerDivision) -> None:
        """Set the vertical scale in V per division (CHANnel<m>:SCALe); the range depends on the probe and coupling."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:SCALe {voltage_scale}")

    @command(returns=("voltage_scale",), reads="setpoint")
    def get_voltage_scale(self, channel: Channel) -> VoltsPerDivision:
        """Return the vertical scale in V per division."""
        self._check_channel(channel)
        return float(self.port.query(f"CHANnel{channel}:SCALe?"))

    @command
    def set_vertical_position(self, channel: Channel, vertical_position: Annotated[Divisions, Range(-5, 5)]) -> None:
        """Set the vertical position of the waveform in divisions (CHANnel<m>:POSition); positive moves it up."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:POSition {vertical_position}")

    @command(returns=("vertical_position",), reads="setpoint")
    def get_vertical_position(self, channel: Channel) -> Divisions:
        """Return the vertical position of the waveform in divisions."""
        self._check_channel(channel)
        return float(self.port.query(f"CHANnel{channel}:POSition?"))

    @command
    def set_voltage_offset(self, channel: Channel, voltage_offset: Volts) -> None:
        """Set the offset voltage subtracted from the signal (CHANnel<m>:OFFSet); the range depends on the probe."""
        self._check_channel(channel)
        self.port.write(f"CHANnel{channel}:OFFSet {voltage_offset}")

    @command(returns=("voltage_offset",), reads="setpoint")
    def get_voltage_offset(self, channel: Channel) -> Volts:
        """Return the offset voltage subtracted from the signal in V."""
        self._check_channel(channel)
        return float(self.port.query(f"CHANnel{channel}:OFFSet?"))

    # -- Waveform data --

    @command(returns=("start_time", "stop_time", "record_length", "values_per_sample"), reads="last")
    def get_waveform_header(self, channel: Channel) -> tuple[Seconds, Seconds, int, int]:
        """Return start time, stop time, record length and values per sample interval (CHANnel<m>:DATA:HEADer?)."""
        self._check_channel(channel)
        fields = self.port.query(f"CHANnel{channel}:DATA:HEADer?").strip().split(",")
        if len(fields) != 4:  # noqa: PLR2004 - the four fields of table "Header data"
            msg = f"Unexpected waveform header of channel {channel}: {fields}"
            raise ValueError(msg)
        return float(fields[0]), float(fields[1]), int(float(fields[2])), int(float(fields[3]))

    @command(returns=("voltage",), reads="last")
    def get_waveform_values(self, channel: Channel) -> Voltages:
        """Return the last acquired waveform of a channel in V (CHANnel<m>:DATA?), in the ASCii data format."""
        self._check_channel(channel)
        answer = self.port.query(f"CHANnel{channel}:DATA?")
        return np.fromstring(answer, dtype=float, sep=",")

    @command(returns=("time", "voltage"), reads="last", composite=True)
    def get_trace(self, channel: Channel) -> tuple[Times, Voltages]:
        """Read the last acquired waveform of a channel as time in s and voltage in V.

        Reads the header for the time axis, evenly spaced from the start to the stop time over the record length,
        and the waveform values. Decimation and arithmetic modes with two values per sample interval (peak detect,
        envelope) are refused.
        """
        start_time, stop_time, record_length, values_per_sample = self.get_waveform_header(channel)
        if values_per_sample != VALUES_PER_SAMPLE:
            msg = (
                f"Channel {channel} answers {values_per_sample} values per sample interval; only decimation and "
                "arithmetic modes with one value (no peak detect or envelope) are supported."
            )
            raise ValueError(msg)
        voltages = self.get_waveform_values(channel)
        if len(voltages) != record_length:
            msg = f"Channel {channel} answered {len(voltages)} values, but its header announces {record_length}."
            raise ValueError(msg)
        times = np.linspace(start_time, stop_time, record_length)
        return times, voltages

    # -- Helpers of the communication commands ------------------------------------------------------------------------

    @staticmethod
    def _is_on(answer: str) -> bool:
        """Return whether a boolean answer means on; the instrument answers 1/0, the manuals write ON/OFF."""
        return answer.strip().upper() in ("1", "ON")

    @staticmethod
    def _parse_identification(identification: str) -> tuple[str, int]:
        """Return the model family and the channel count from the *IDN? answer, "" and 0 where not recognised.

        The answer is Rohde&Schwarz,<family>,<order number>k<variant>/<serial>,<firmware>; the last digit of the
        variant is the channel count of every RTO1000, RTO2000 and RTE1000 model (user manual, "Models").
        """
        family, order_number = ([*identification.split(","), "", ""])[1:3]
        match = re.search(r"[kK](\d)(\d)\b", order_number)
        channel_count = int(match.group(2)) if match else 0
        family = family.strip().upper()
        return family, channel_count if channel_count in CHANNEL_COUNTS else 0

    def _check_maximum(self, name: str, value: float, maxima: dict[str, float]) -> None:
        """Raise when a value exceeds the maximum of the connected model family; unknown families are not checked."""
        maximum = maxima.get(self.model_family)
        if maximum is not None and value > maximum:
            msg = f"The {name} {value} exceeds the maximum of {maximum} of the connected {self.model_family}."
            raise ValueError(msg)
