# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2024-2026 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Peter Hegarty (TU Dresden) for providing the initial version of this driver.

# SweepMe! driver
# * Module: Scope
# * Instrument: Tektronix DPOseries

from __future__ import annotations

import time
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme.commands import Elements, Label, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call). The spellings of the
# Literal choices are the full-length keywords of the programmer manual 077-0010-26, which the instrument accepts
# as commands and answers with 'HEADer OFF' and 'VERBose ON' (set in initialize), so a read-back matches its Literal.
Channel = Annotated[int, Selector(), Range(1, 4)]  # CH<x>: "x can range from 1 through 4"
Volts = Annotated[float, Unit("V")]
Seconds = Annotated[float, Unit("s")]
VoltsPerDivision = Annotated[float, Unit("V/div"), Label("Vertical scale")]
SecondsPerDivision = Annotated[float, Unit("s/div"), Label("Horizontal scale")]
SamplesPerSecond = Annotated[float, Unit("S/s"), Label("Sample rate")]
# CH<x>:TERmination <NR3>: "the channel input resistance, which can be specified as 50 Ohm or 1,000,000 Ohm"
Impedance = Annotated[Literal[50, 1000000], Unit("Ohm")]
Times = Annotated[np.ndarray, Elements(Seconds)]
Voltages = Annotated[np.ndarray, Elements(Volts)]
ChannelCoupling = Literal["AC", "DC", "DCREJECT", "GND"]  # CH<x>:COUPling
TriggerSource = Literal["AUXILIARY", "CH1", "CH2", "CH3", "CH4", "LINE"]  # TRIGger:A:EDGE:SOUrce, analog sources
TriggerSlope = Literal["RISE", "FALL", "EITHER"]  # TRIGger:A:EDGE:SLOpe
TriggerCoupling = Literal["AC", "DC", "HFREJ", "LFREJ", "NOISEREJ"]  # TRIGger:A:EDGE:COUPling (A trigger)
AcquisitionMode = Literal["SAMPLE", "PEAKDETECT", "HIRES", "AVERAGE", "WFMDB", "ENVELOPE"]  # ACQuire:MODe
AcquisitionType = Literal["RUNSTOP", "SEQUENCE"]  # ACQuire:STOPAfter
HorizontalMode = Literal["AUTO", "CONSTANT", "MANUAL"]  # HORizontal:MODE
DataEncoding = Literal[  # DATa:ENCdg
    "ASCII",
    "FASTEST",
    "RIBINARY",
    "RPBINARY",
    "FPBINARY",
    "SRIBINARY",
    "SRPBINARY",
    "SFPBINARY",
]
DataWidth = Literal[1, 2, 4, 8]  # WFMOutpre:BYT_Nr
DataPoint = Annotated[int, Range(1, None)]  # DATa:STARt and DATa:STOP: "ranges from 1 to the record length"

# Scope module labels -> instrument keywords
TRIGGER_SOURCES: dict[str, TriggerSource] = {
    "CH1": "CH1",
    "CH2": "CH2",
    "CH3": "CH3",
    "CH4": "CH4",
    "AUX": "AUXILIARY",
    "LINE": "LINE",
}
TRIGGER_SLOPES: dict[str, TriggerSlope] = {"Rising": "RISE", "Falling": "FALL", "Either": "EITHER"}
TRIGGER_COUPLINGS: dict[str, TriggerCoupling] = {
    "AC": "AC",
    "DC": "DC",
    "HF rejection": "HFREJ",
    "LF rejection": "LFREJ",
    "LF recection": "LFREJ",  # the misspelled label of earlier versions, kept so saved sequences still load
    "Noise rejection": "NOISEREJ",
}
CHANNEL_COUPLINGS: dict[str, ChannelCoupling] = {"DC": "DC", "AC": "AC", "DC reject": "DCREJECT", "Ground": "GND"}
IMPEDANCES: dict[str, Impedance] = {"50": 50, "1e6": 1000000}
# The instrument counts 10 horizontal and 10 vertical divisions; a range in the GUI is converted to a per-division
# scale with this number.
DIVISIONS = 10
# The event queue holds up to 33 events (manual, "Queues"); more reads of EVMsg? are never needed.
EVENT_QUEUE_LENGTH = 33
# Event codes below this are command, execution and device errors (manual, tables 3-4 to 3-6); the system events,
# execution warnings and internal warnings above it do not stop a measurement.
FIRST_NON_ERROR_EVENT = 400
# Event codes 0 and 1 mean "No events to report" (manual, table 3-3).
NO_EVENT_CODES = (0, 1)


class Device(EmptyDevice):
    """Driver for the analog channels of Tektronix DPO7000 series oscilloscopes and their siblings."""

    def __init__(self) -> None:
        """Define the returned variables, the port and the default values of every attribute."""
        super().__init__()

        self.shortname = "DPO7000"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]

        self.port_properties = {
            "timeout": 5.0,
            "delay": 1.0,
        }

        # GUI parameters, exactly as they arrive from the GUI; converted in configure()
        self.gui_parameters: dict[str, Any] = {}
        self.channels: list[int] = []

        # Values derived from the GUI parameters in configure()
        self.trigger_source: str = "As is"
        self.trigger_coupling: str = "As is"
        self.trigger_slope: str = "As is"
        self.trigger_level: float = 0.0
        self.trigger_timeout: float = 30.0
        self.time_range: str = "Time range in s"
        self.time_range_value: float = 5e-4
        self.sampling_rate: float = 1e7
        self.average: str = "As is"
        self.acquisition: str = "As is"
        self.channel_ranges: dict[int, str] = {}
        self.channel_offsets: dict[int, float] = {}
        self.channel_impedances: dict[int, str] = {}
        self.channel_couplings: dict[int, str] = {}

        # Instrument state read back in configure()
        self.acquisition_type: str = "RUNSTOP"
        self.acquisition_mode: str = "SAMPLE"
        self.number_averages: int = 1
        self.identification: str = ""

        # Measured data
        self.times: np.ndarray = np.array([])
        self.voltages: list[np.ndarray] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields of the Scope module with their defaults."""
        new_parameters: dict[str, Any] = {
            "SweepMode": ["None"],
            "TriggerSlope": ["As is", *TRIGGER_SLOPES],
            "TriggerSource": ["As is", *TRIGGER_SOURCES, "None"],
            "TriggerCoupling": ["As is", "DC", "AC", "HF rejection", "LF rejection", "Noise rejection"],
            "TriggerLevel": 0,
            "TriggerTimeout": 30.0,
            "TimeRange": ["Time range in s", "Time scale in s/div", "Record length"],
            "TimeRangeValue": 5e-4,
            "TimeOffsetValue": 0.0,
            "SamplingRateType": ["Samples per s"],
            "SamplingRate": int(1e7),
            "Acquisition": ["As is", "Single", "Continuous"],
            "Average": ["As is", "1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "VoltageRange": ["Voltage range in V"],
        }

        for i in range(1, 5):
            new_parameters[f"Channel{i}"] = i == 1
            new_parameters[f"Channel{i}_Name"] = f"CH{i}"
            new_parameters[f"Channel{i}_Range"] = [
                "As is",
                "1e-2",
                "2e-2",
                "5e-2",
                "1e-1",
                "2e-1",
                "5e-1",
                "1",
                "2",
                "5",
                "10",
                "20",
                "50",
            ]
            new_parameters[f"Channel{i}_Offset"] = 0.0
            new_parameters[f"Channel{i}_Impedance"] = ["As is", *IMPEDANCES]
            new_parameters[f"Channel{i}_Coupling"] = ["As is", *CHANNEL_COUPLINGS]

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the raw GUI parameters and derive the returned variables from the selected channels.

        The values are converted to numbers in convert_gui_parameters(), called from configure(), so that a later
        call of this function with the raw strings cannot revert converted values.
        """
        self.gui_parameters = dict(parameters)

        self.channels = [i for i in range(1, 5) if parameters.get(f"Channel{i}", False)]

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]
        self.savetype = [True]

        for i in self.channels:
            name = str(parameters.get(f"Channel{i}_Name", f"CH{i}"))
            self.variables.append(name if name != "" else f"CH{i}")
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self) -> None:
        """Check the user input, set the answer format and prepare the waveform transfer, once per run.

        The driver deliberately sends no reset, so that everything the GUI leaves "As is" stays as set on the
        instrument.
        """
        if len(self.channels) == 0:
            msg = "Please select at least one channel to be read out."
            raise ValueError(msg)

        self.identification = self.get_identification()

        # Answers without headers and with full-length keywords, so that read-backs match the declared Literals
        self.set_header(False)
        self.set_verbose(True)
        self.clear_status()

        # Waveform transfer: the whole record as ASCII values with 16-bit resolution. The manual (DATa:STOP):
        # "If you always want to transfer complete waveforms, set DATa:STARt to 1 and DATa:STOP to the maximum record
        # length, or larger."
        self.set_data_start(1)
        self.set_data_stop(2_000_000_000)
        self.set_data_encoding("ASCII")
        self.set_data_width(2)

    def configure(self) -> None:
        """Convert the GUI parameters and write the acquisition, trigger, timebase and channel settings."""
        self.convert_gui_parameters()
        self._configure_acquisition()
        self._configure_trigger()
        self._configure_timebase()
        self._configure_channels()
        self._raise_on_errors()

    def measure(self) -> None:
        """Acquire a single sequence if configured, then read the waveform of every selected channel."""
        if self.acquisition_type == "SEQUENCE":
            self.set_acquisition_running(True)
            self._wait_for_acquisition()
            if self.is_run_stopped():
                return

        self.voltages = []
        for i in self.channels:
            times, voltages = self.get_waveform(i)
            if i == self.channels[0]:
                self.times = times
            self.voltages.append(voltages)

    def call(self) -> list[np.ndarray]:
        """Return the time axis and one trace per selected channel."""
        return [self.times, *self.voltages]

    # -- Helpers of the semantic functions ----------------------------------------------------------------------------

    def _configure_acquisition(self) -> None:
        """Write the acquisition type and the averaging, or read them back for "As is"."""
        if self.acquisition == "Continuous":
            self.set_acquisition_running(True)
            self.set_acquisition_type("RUNSTOP")
        elif self.acquisition == "Single":
            self.set_acquisition_running(False)
            self.set_acquisition_type("SEQUENCE")
        self.acquisition_type = self.get_acquisition_type()

        if self.average == "As is":
            self.number_averages = self.get_averages()
        else:
            self.number_averages = int(self.average)
            self.set_averages(self.number_averages)
            self.set_acquisition_mode("SAMPLE" if self.number_averages == 1 else "AVERAGE")
        self.acquisition_mode = self.get_acquisition_mode()

    def _configure_trigger(self) -> None:
        """Write the source, level, slope and coupling of the A edge trigger where they are not "As is"."""
        if self.trigger_source not in ("As is", "None"):
            self.set_trigger_source(TRIGGER_SOURCES[self.trigger_source])
            if self.trigger_level == 0.0:
                # A level of 0 means: let the instrument put the level at 50 % of the trigger signal
                self.autoset_trigger_level()
            else:
                self.set_trigger_level(self.trigger_level)

        if self.trigger_slope != "As is":
            self.set_trigger_slope(TRIGGER_SLOPES[self.trigger_slope])

        if self.trigger_coupling != "As is":
            self.set_trigger_coupling(TRIGGER_COUPLINGS[self.trigger_coupling])

    def _configure_timebase(self) -> None:
        """Write the horizontal mode with the time scale or the record length, and the sample rate.

        The time range and the time scale need the automatic horizontal mode, in which the record length is
        read-only; a record length needs the manual mode, in which the scale is read-only (HORizontal:MODE).
        """
        if self.time_range == "Record length":
            self.set_horizontal_mode("MANUAL")
            self.set_record_length(int(self.time_range_value))
        else:
            self.set_horizontal_mode("AUTO")
            if self.time_range == "Time range in s":
                self.set_horizontal_scale(self.time_range_value / DIVISIONS)
            else:
                self.set_horizontal_scale(self.time_range_value)
        self.set_sample_rate(self.sampling_rate)

    def _configure_channels(self) -> None:
        """Switch the selected channels on and write their termination, coupling, scale and offset."""
        for i in self.channels:
            if self.channel_impedances[i] != "As is":
                self.set_impedance(i, IMPEDANCES[self.channel_impedances[i]])
            if self.channel_couplings[i] != "As is":
                self.set_coupling(i, CHANNEL_COUPLINGS[self.channel_couplings[i]])
            self.set_display(i, True)
            if self.channel_ranges[i] != "As is":
                self.set_vertical_scale(i, float(self.channel_ranges[i]) / DIVISIONS)
            self.set_offset(i, self.channel_offsets[i])

    def convert_gui_parameters(self) -> None:
        """Convert the stored GUI parameters to numbers, then check them.

        Done here and not in apply_gui_parameters(), which may be called with incomplete fields while the user is
        still editing them; the converted values live in attributes of their own.
        """
        parameters = self.gui_parameters

        self.trigger_source = str(parameters.get("TriggerSource", "As is"))
        self.trigger_coupling = str(parameters.get("TriggerCoupling", "As is"))
        self.trigger_slope = str(parameters.get("TriggerSlope", "As is"))
        self.time_range = str(parameters.get("TimeRange", "Time range in s"))
        self.average = str(parameters.get("Average", "As is"))
        self.acquisition = str(parameters.get("Acquisition", "As is"))

        try:
            self.trigger_level = float(parameters.get("TriggerLevel", 0.0))
            self.trigger_timeout = float(parameters.get("TriggerTimeout", 30.0))
            self.time_range_value = float(parameters.get("TimeRangeValue", 5e-4))
            self.sampling_rate = float(parameters.get("SamplingRate", 1e7))
            self.channel_offsets = {i: float(parameters.get(f"Channel{i}_Offset", 0.0)) for i in self.channels}
        except ValueError as e:
            msg = f"Scope-Tektronix_DPOseries: Please enter numeric values into all number fields. Error is: {e}"
            raise ValueError(msg) from e

        self.channel_ranges = {i: str(parameters.get(f"Channel{i}_Range", "As is")) for i in self.channels}
        self.channel_impedances = {i: str(parameters.get(f"Channel{i}_Impedance", "As is")) for i in self.channels}
        self.channel_couplings = {i: str(parameters.get(f"Channel{i}_Coupling", "As is")) for i in self.channels}

        self._check_gui_parameters()

    def _check_gui_parameters(self) -> None:
        """Raise with a message for the user when a converted GUI parameter is not supported."""
        if self.trigger_source not in ("As is", "None", *TRIGGER_SOURCES):
            msg = f"Scope-Tektronix_DPOseries: Unknown trigger source '{self.trigger_source}'."
            raise ValueError(msg)
        if self.trigger_slope not in ("As is", *TRIGGER_SLOPES):
            msg = f"Scope-Tektronix_DPOseries: Unknown trigger slope '{self.trigger_slope}'."
            raise ValueError(msg)
        if self.trigger_coupling not in ("As is", *TRIGGER_COUPLINGS):
            msg = f"Scope-Tektronix_DPOseries: Unknown trigger coupling '{self.trigger_coupling}'."
            raise ValueError(msg)
        if self.acquisition not in ("As is", "Single", "Continuous"):
            msg = f"Scope-Tektronix_DPOseries: Acquisition mode '{self.acquisition}' is not supported."
            raise ValueError(msg)
        if self.average != "As is" and int(self.average) < 1:
            msg = "Scope-Tektronix_DPOseries: The number of averages must be at least 1."
            raise ValueError(msg)
        if self.trigger_timeout <= 0.0:
            msg = "Scope-Tektronix_DPOseries: The trigger timeout must be larger than 0 s."
            raise ValueError(msg)
        for i in self.channels:
            if self.channel_impedances[i] not in ("As is", *IMPEDANCES):
                msg = f"Scope-Tektronix_DPOseries: Unknown impedance '{self.channel_impedances[i]}' of channel {i}."
                raise ValueError(msg)
            if self.channel_couplings[i] not in ("As is", *CHANNEL_COUPLINGS):
                msg = f"Scope-Tektronix_DPOseries: Unknown coupling '{self.channel_couplings[i]}' of channel {i}."
                raise ValueError(msg)

    def _wait_for_acquisition(self) -> None:
        """Wait until a single sequence has completed, bounded by the trigger timeout.

        The acquisition state answers 0 once the sequence is done. In average mode the number of acquisitions is
        checked as well, so that an averaged waveform is only read after all its acquisitions.
        """
        start = time.time()
        while not self.is_run_stopped():
            running = self.get_acquisition_running()
            averaged = self.acquisition_mode != "AVERAGE" or self.get_acquisition_number() >= self.number_averages
            if not running and averaged:
                return
            if time.time() - start > self.trigger_timeout:
                msg = (
                    f"Scope-Tektronix_DPOseries: The acquisition did not complete within {self.trigger_timeout} s. "
                    "Please check the trigger source, level and slope, or increase the trigger timeout."
                )
                raise TimeoutError(msg)

    def _raise_on_errors(self) -> None:
        """Read the event queue and raise with the command, execution and device errors the instrument reported."""
        self.get_event_status()  # loads the event queue (manual, "Queues")
        events = self.get_events()
        errors = [event for event in events if int(event.split(",", 1)[0]) < FIRST_NON_ERROR_EVENT]
        for event in events:
            if event not in errors:
                self.message_log(f"Scope-Tektronix_DPOseries: instrument event {event}")
        if errors:
            msg = f"Scope-Tektronix_DPOseries: The instrument reported errors: {'; '.join(errors)}"
            raise ValueError(msg)

    @staticmethod
    def _value(answer: str) -> str:
        """Return the value of an answer, without a response header should one be present (':HEADER value')."""
        answer = answer.strip()
        if answer.startswith(":"):
            answer = answer.split(" ", 1)[-1]
        return answer.strip()

    # -- Communication commands ---------------------------------------------------------------------------------------
    # One instrument command each, declared with pysweepme's @command. The instrument accepts the keywords in the
    # abbreviated and the full-length form; the driver sends the full-length form and, with HEADer OFF and
    # VERBose ON, receives it back. Section numbers refer to the programmer manual 077-0010-26.

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the instrument (*IDN?)."""
        return self._value(self.port.query("*IDN?"))

    @command
    def reset(self) -> None:
        """Reset the programmable interface settings to the factory defaults (*RST); DATa settings are kept."""
        self.port.write("*RST")

    @command
    def clear_status(self) -> None:
        """Clear the event queue and the status registers (*CLS)."""
        self.port.write("*CLS")

    @command(returns=("event_status",), reads="state")
    def get_event_status(self) -> int:
        """Return and clear the Standard Event Status Register (*ESR?), which loads the event queue for get_events."""
        return int(self._value(self.port.query("*ESR?")))

    @command(returns=("events",), reads="state")
    def get_events(self) -> list[str]:
        """Return and remove the pending events as 'code,"message"' entries (EVMsg?), read after get_event_status."""
        events: list[str] = []
        for _ in range(EVENT_QUEUE_LENGTH):
            event = self._value(self.port.query("EVMsg?"))
            code = int(event.split(",", 1)[0])
            if code in NO_EVENT_CODES:
                break
            events.append(event)
        return events

    @command
    def set_header(self, header: bool) -> None:
        """Switch the response headers of query answers on or off (HEADer)."""
        self.port.write(f"HEADer {'ON' if header else 'OFF'}")

    @command(returns=("header",), reads="setpoint")
    def get_header(self) -> bool:
        """Return whether query answers carry a response header."""
        return self._value(self.port.query("HEADer?")) == "1"

    @command
    def set_verbose(self, verbose: bool) -> None:
        """Select full-length (True) or minimum-length (False) keywords in query answers (VERBose)."""
        self.port.write(f"VERBose {'ON' if verbose else 'OFF'}")

    @command(returns=("verbose",), reads="setpoint")
    def get_verbose(self) -> bool:
        """Return whether query answers use full-length keywords."""
        return self._value(self.port.query("VERBose?")) == "1"

    # -- Acquisition: the ACQuire group --

    @command
    def set_acquisition_running(self, acquisition_running: bool) -> None:
        """Start (True) or stop (False) acquisitions (ACQuire:STATE); a start restarts a single sequence."""
        self.port.write(f"ACQuire:STATE {'RUN' if acquisition_running else 'STOP'}")

    @command(returns=("acquisition_running",), reads="setpoint")
    def get_acquisition_running(self) -> bool:
        """Return whether acquisitions are running; False once a single sequence has completed."""
        return self._value(self.port.query("ACQuire:STATE?")) == "1"

    @command
    def set_acquisition_type(self, acquisition_type: AcquisitionType) -> None:
        """Select continuous acquisitions (RUNSTOP) or a single sequence (SEQUENCE) (ACQuire:STOPAfter)."""
        self.port.write(f"ACQuire:STOPAfter {acquisition_type}")

    @command(returns=("acquisition_type",), reads="setpoint")
    def get_acquisition_type(self) -> AcquisitionType:
        """Return the acquisition type, RUNSTOP for continuous and SEQUENCE for single."""
        return self._value(self.port.query("ACQuire:STOPAfter?"))  # type: ignore[return-value]

    @command(
        warnings="At a sample rate at or above the base sample rate (6.25 GS/s for 70K, 5 GS/s for 5K and 7K "
        "oscilloscopes) HIRES and PEAKDETECT are silently replaced by SAMPLE; ACQuire:MODe:ACTUal? tells.",
    )
    def set_acquisition_mode(self, acquisition_mode: AcquisitionMode) -> None:
        """Set the acquisition mode of all live waveforms (ACQuire:MODe)."""
        self.port.write(f"ACQuire:MODe {acquisition_mode}")

    @command(returns=("acquisition_mode",), reads="setpoint")
    def get_acquisition_mode(self) -> AcquisitionMode:
        """Return the acquisition mode, e.g. SAMPLE or AVERAGE."""
        return self._value(self.port.query("ACQuire:MODe?"))  # type: ignore[return-value]

    @command
    def set_averages(self, averages: int) -> None:
        """Set the number of acquisitions that make up an averaged waveform (ACQuire:NUMAVg)."""
        self.port.write(f"ACQuire:NUMAVg {averages}")

    @command(returns=("averages",), reads="setpoint")
    def get_averages(self) -> int:
        """Return the number of acquisitions that make up an averaged waveform."""
        return int(self._value(self.port.query("ACQuire:NUMAVg?")))

    @command(returns=("acquisition_number",), reads="state")
    def get_acquisition_number(self) -> int:
        """Return the number of acquisitions since the last start of the acquisition (ACQuire:NUMACq?)."""
        return int(self._value(self.port.query("ACQuire:NUMACq?")))

    # -- Trigger: the A trigger of edge type --

    @command
    def set_trigger_source(self, trigger_source: TriggerSource) -> None:
        """Set the source of the A edge trigger (TRIGger:A:EDGE:SOUrce)."""
        self.port.write(f"TRIGger:A:EDGE:SOUrce {trigger_source}")

    @command(returns=("trigger_source",), reads="setpoint")
    def get_trigger_source(self) -> TriggerSource:
        """Return the source of the A edge trigger."""
        return self._value(self.port.query("TRIGger:A:EDGE:SOUrce?"))  # type: ignore[return-value]

    @command
    def set_trigger_slope(self, trigger_slope: TriggerSlope) -> None:
        """Set the slope of the A edge trigger (TRIGger:A:EDGE:SLOpe); EITHER is not available on MSO/DPO5000."""
        self.port.write(f"TRIGger:A:EDGE:SLOpe {trigger_slope}")

    @command(returns=("trigger_slope",), reads="setpoint")
    def get_trigger_slope(self) -> TriggerSlope:
        """Return the slope of the A edge trigger."""
        return self._value(self.port.query("TRIGger:A:EDGE:SLOpe?"))  # type: ignore[return-value]

    @command
    def set_trigger_coupling(self, trigger_coupling: TriggerCoupling) -> None:
        """Set the coupling of the A edge trigger (TRIGger:A:EDGE:COUPling)."""
        self.port.write(f"TRIGger:A:EDGE:COUPling {trigger_coupling}")

    @command(returns=("trigger_coupling",), reads="setpoint")
    def get_trigger_coupling(self) -> TriggerCoupling:
        """Return the coupling of the A edge trigger."""
        return self._value(self.port.query("TRIGger:A:EDGE:COUPling?"))  # type: ignore[return-value]

    @command
    def set_trigger_level(self, trigger_level: Volts) -> None:
        """Set the level of the A trigger in user units, usually volts (TRIGger:A:LEVel)."""
        self.port.write(f"TRIGger:A:LEVel {trigger_level}")

    @command(returns=("trigger_level",), reads="setpoint")
    def get_trigger_level(self) -> Volts:
        """Return the level of the A trigger."""
        return float(self._value(self.port.query("TRIGger:A:LEVel?")))

    @command
    def autoset_trigger_level(self) -> None:
        """Set the A trigger level to 50 % of the range of the trigger signal (TRIGger:A SETLevel)."""
        self.port.write("TRIGger:A SETLevel")

    # -- Timebase: the HORizontal group --

    @command
    def set_horizontal_mode(self, horizontal_mode: HorizontalMode) -> None:
        """Set the horizontal mode (HORizontal:MODE): AUTO and CONSTANT set the scale, MANUAL the record length."""
        self.port.write(f"HORizontal:MODE {horizontal_mode}")

    @command(returns=("horizontal_mode",), reads="setpoint")
    def get_horizontal_mode(self) -> HorizontalMode:
        """Return the horizontal mode."""
        return self._value(self.port.query("HORizontal:MODE?"))  # type: ignore[return-value]

    @command
    def set_horizontal_scale(self, horizontal_scale: SecondsPerDivision) -> None:
        """Set the horizontal scale in s per division (HORizontal:MODE:SCAle); read-only in MANUAL mode."""
        self.port.write(f"HORizontal:MODE:SCAle {horizontal_scale}")

    @command(returns=("horizontal_scale",), reads="setpoint")
    def get_horizontal_scale(self) -> SecondsPerDivision:
        """Return the horizontal scale in s per division."""
        return float(self._value(self.port.query("HORizontal:MODE:SCAle?")))

    @command
    def set_record_length(self, record_length: int) -> None:
        """Set the record length in samples (HORizontal:MODE:RECOrdlength); read-only in AUTO and CONSTANT mode."""
        self.port.write(f"HORizontal:MODE:RECOrdlength {record_length}")

    @command(returns=("record_length",), reads="setpoint")
    def get_record_length(self) -> int:
        """Return the record length in samples."""
        return int(float(self._value(self.port.query("HORizontal:MODE:RECOrdlength?"))))

    @command
    def set_sample_rate(self, sample_rate: SamplesPerSecond) -> None:
        """Set the sample rate in samples per second (HORizontal:MODE:SAMPLERate)."""
        self.port.write(f"HORizontal:MODE:SAMPLERate {sample_rate:.0f}")

    @command(returns=("sample_rate",), reads="setpoint")
    def get_sample_rate(self) -> SamplesPerSecond:
        """Return the sample rate in samples per second."""
        return float(self._value(self.port.query("HORizontal:MODE:SAMPLERate?")))

    # -- Channels: the CH<x> and SELect commands --

    @command
    def set_display(self, channel: Channel, display: bool) -> None:
        """Switch the display, and with it the acquisition, of a channel waveform on or off (SELect:CH<x>)."""
        self.port.write(f"SELect:CH{channel} {'ON' if display else 'OFF'}")

    @command(returns=("display",), reads="setpoint")
    def get_display(self, channel: Channel) -> bool:
        """Return whether a channel waveform is displayed."""
        return self._value(self.port.query(f"SELect:CH{channel}?")) == "1"

    @command
    def set_vertical_scale(self, channel: Channel, vertical_scale: VoltsPerDivision) -> None:
        """Set the vertical scale of a channel in V per division (CH<x>:SCAle); the range depends on the probe."""
        self.port.write(f"CH{channel}:SCAle {vertical_scale}")

    @command(returns=("vertical_scale",), reads="setpoint")
    def get_vertical_scale(self, channel: Channel) -> VoltsPerDivision:
        """Return the vertical scale of a channel in V per division."""
        return float(self._value(self.port.query(f"CH{channel}:SCAle?")))

    @command
    def set_offset(self, channel: Channel, offset: Volts) -> None:
        """Set the vertical offset of a channel, the level at the center of the acquisition window (CH<x>:OFFSet)."""
        self.port.write(f"CH{channel}:OFFSet {offset}")

    @command(returns=("offset",), reads="setpoint")
    def get_offset(self, channel: Channel) -> Volts:
        """Return the vertical offset of a channel."""
        return float(self._value(self.port.query(f"CH{channel}:OFFSet?")))

    @command
    def set_coupling(self, channel: Channel, coupling: ChannelCoupling) -> None:
        """Set the input coupling of a channel (CH<x>:COUPling); DCREJECT needs a probe with that feature."""
        self.port.write(f"CH{channel}:COUPling {coupling}")

    @command(returns=("coupling",), reads="setpoint")
    def get_coupling(self, channel: Channel) -> ChannelCoupling:
        """Return the input coupling of a channel."""
        return self._value(self.port.query(f"CH{channel}:COUPling?"))  # type: ignore[return-value]

    @command
    def set_impedance(self, channel: Channel, impedance: Impedance) -> None:
        """Set the input termination of a channel to 50 Ohm or 1 MOhm (CH<x>:TERmination); 50 Ohm needs the hardware."""
        self.port.write(f"CH{channel}:TERmination {impedance}")

    @command(returns=("impedance",), reads="setpoint")
    def get_impedance(self, channel: Channel) -> Impedance:
        """Return the input termination of a channel in Ohm."""
        return int(float(self._value(self.port.query(f"CH{channel}:TERmination?"))))  # type: ignore[return-value]

    # -- Waveform transfer: the DATa, WFMOutpre and CURVe commands --

    @command
    def select_data_source(self, channel: Channel) -> None:
        """Select the channel whose waveform the preamble and curve queries answer (DATa:SOUrce)."""
        self.port.write(f"DATa:SOUrce CH{channel}")

    @command(returns=("data_source",), reads="setpoint")
    def get_data_source(self) -> str:
        """Return the selected waveform source of the preamble and curve queries, e.g. CH1."""
        return self._value(self.port.query("DATa:SOUrce?"))

    @command
    def set_data_encoding(self, data_encoding: DataEncoding) -> None:
        """Set the format of outgoing waveform data (DATa:ENCdg); the driver reads ASCII."""
        self.port.write(f"DATa:ENCdg {data_encoding}")

    @command(returns=("data_encoding",), reads="setpoint")
    def get_data_encoding(self) -> DataEncoding:
        """Return the format of outgoing waveform data."""
        return self._value(self.port.query("DATa:ENCdg?"))  # type: ignore[return-value]

    @command
    def set_data_width(self, data_width: DataWidth) -> None:
        """Set the number of bytes per waveform point (WFMOutpre:BYT_Nr); 1 or 2 for channel data."""
        self.port.write(f"WFMOutpre:BYT_Nr {data_width}")

    @command(returns=("data_width",), reads="setpoint")
    def get_data_width(self) -> DataWidth:
        """Return the number of bytes per waveform point."""
        return int(self._value(self.port.query("WFMOutpre:BYT_Nr?")))  # type: ignore[return-value]

    @command
    def set_data_start(self, data_start: DataPoint) -> None:
        """Set the first data point of a waveform transfer (DATa:STARt)."""
        self.port.write(f"DATa:STARt {data_start}")

    @command(returns=("data_start",), reads="setpoint")
    def get_data_start(self) -> int:
        """Return the first data point of a waveform transfer."""
        return int(self._value(self.port.query("DATa:STARt?")))

    @command
    def set_data_stop(self, data_stop: DataPoint) -> None:
        """Set the last data point of a waveform transfer (DATa:STOP); above the record length the record ends it."""
        self.port.write(f"DATa:STOP {data_stop}")

    @command(returns=("data_stop",), reads="setpoint")
    def get_data_stop(self) -> int:
        """Return the last data point of a waveform transfer."""
        return int(self._value(self.port.query("DATa:STOP?")))

    @command(returns=("waveform_preamble",), reads="state")
    def get_waveform_preamble(self) -> dict[str, float | int | str]:
        """Return the formatting and scaling of the selected waveform source (WFMOutpre?) as a dictionary.

        The keys are the preamble fields in the order the instrument answers them with headers off: BYT_NR, BIT_NR,
        ENCDG, BN_FMT, BYT_OR, WFID, NR_PT, PT_FMT, XUNIT, XINCR, XZERO, PT_OFF, YUNIT, YMULT, YOFF, YZERO and NR_FR.
        """
        fields = self._value(self.port.query("WFMOutpre?")).split(";")
        names = (
            "BYT_NR",
            "BIT_NR",
            "ENCDG",
            "BN_FMT",
            "BYT_OR",
            "WFID",
            "NR_PT",
            "PT_FMT",
            "XUNIT",
            "XINCR",
            "XZERO",
            "PT_OFF",
            "YUNIT",
            "YMULT",
            "YOFF",
            "YZERO",
            "NR_FR",
        )
        if len(fields) < len(names) - 1:  # NR_FR is only answered with FastFrame
            msg = f"Scope-Tektronix_DPOseries: Unexpected waveform preamble: {fields}"
            raise ValueError(msg)
        preamble: dict[str, float | int | str] = {}
        for name, field in zip(names, fields, strict=False):
            if name in ("BYT_NR", "BIT_NR", "NR_PT", "PT_OFF", "NR_FR"):
                preamble[name] = int(field)
            elif name in ("XINCR", "XZERO", "YMULT", "YOFF", "YZERO"):
                preamble[name] = float(field)
            else:
                preamble[name] = field.strip('"')
        return preamble

    @command(returns=("curve",), reads="last")
    def get_curve(self) -> list[int]:
        """Return the waveform of the selected source as digitizing levels (CURVe?), in ASCII encoding."""
        answer = self._value(self.port.query("CURVe?"))
        return [int(point) for point in answer.split(",")]

    @command(returns=("time", "voltage"), reads="last", composite=True)
    def get_waveform(self, channel: Channel) -> tuple[Times, Voltages]:
        """Read the last acquired waveform of a channel as time in s and voltage in V.

        Selects the channel as data source, reads the preamble and the curve, and scales the digitizing levels with
        the preamble: Xn = XZERO + XINCR * (n - PT_OFF), Yn = YZERO + YMULT * (yn - YOFF) (manual, WFMInpre:PT_Fmt).
        """
        self.select_data_source(channel)
        preamble = self.get_waveform_preamble()
        levels = np.array(self.get_curve(), dtype=float)
        times = float(preamble["XZERO"]) + float(preamble["XINCR"]) * (np.arange(len(levels)) - int(preamble["PT_OFF"]))
        voltages = float(preamble["YZERO"]) + float(preamble["YMULT"]) * (levels - float(preamble["YOFF"]))
        return times, voltages
