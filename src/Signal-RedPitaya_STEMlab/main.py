# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022, 2024, 2026 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank TU Dresden/Toni Bärschneider for providing the initial version of this driver.

# SweepMe! device class
# Type: Signal
# Device: Red pitaya STEMlab


from __future__ import annotations

import math
import sys
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme import Label, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call)
Channel = Annotated[int, Selector(), Range(1, 2)]
Volts = Annotated[float, Unit("V")]
Hertz = Annotated[float, Unit("Hz")]
Phase = Annotated[float, Unit("°"), Range(-360.0, 360.0)]
DutyCycle = Annotated[float, Range(0.0, 1.0)]
Waveform = Literal["SINE", "SQUARE", "TRIANGLE", "SAWU", "SAWD", "PWM", "ARBITRARY", "DC"]
TriggerSource = Annotated[Literal["INT", "EXT_PE", "EXT_NE", "GATED"], Label("Trigger source")]
BurstState = Annotated[Literal["CONTINUOUS", "BURST"], Label("Burst state")]
BurstCycles = Annotated[int, Range(1, 65535), Label("Burst cycles")]  # 65536 is ignored by the board
BurstRepetitions = Annotated[int, Range(1, 65536), Label("Burst repetitions")]  # 65536 means infinite
BurstPeriod = Annotated[float, Unit("µs"), Label("Burst period")]
OutputOn = Annotated[bool, Label("Output on")]

# +/- V of the fast analog outputs (STEMlab): the one-way amplitude plus the absolute offset must stay within it. Beyond
# it the board clips the signal without a word, so the driver refuses such a combination; it never clips.
OUTPUT_RANGE = 1.0


def _check_output_range(amplitude: float, offset: float) -> None:
    """Refuse amplitude and offset whose sum leaves the output range; the board would clip the signal."""
    if abs(amplitude) + abs(offset) > OUTPUT_RANGE + 1e-9:
        msg = (
            f"Amplitude {amplitude:g} V plus offset {offset:g} V exceed the output range of +/- {OUTPUT_RANGE:g} V: "
            f"amplitude plus absolute offset must stay within it."
        )
        raise ValueError(msg)


class Device(EmptyDevice):
    """Driver for the fast analog outputs of Red Pitaya STEMlab boards."""

    def __init__(self) -> None:
        EmptyDevice.__init__(self)
        self.shortname = "STEMlab"

        self.waveforms: dict[str, str] = {
            "Sine": "SINE",
            "Square": "SQUARE",
            "Triangle": "TRIANGLE",
            "Saw up": "SAWU",
            "Saw down": "SAWD",
            "PWM": "PWM",
            "Arbitrary": "ARBITRARY",
            "DC": "DC",
        }

        # "Immediately" is not a trigger source of the instrument. It uses the internal trigger
        # source and additionally sends the software trigger, see 'trigger_ready'.
        self.triggertypes: dict[str, str] = {
            "Internal": "INT",
            "External NE": "EXT_NE",
            "External PE": "EXT_PE",
            "Immediately": "IMM",
            "Gated": "GATED",
        }

        self.operationmodes: dict[str, str] = {
            "Continuous": "CONTINUOUS",
            "Burst": "BURST",
        }

        self.sweep_modes: list[str] = [
            "None",
            "Frequency in Hz",
            "Period in s",
            "Amplitude in V",
            "Offset in V",
            "High level in V",
            "Low level in V",
            "Phase in °",
            "Delay in s",
        ]

        # The board is addressed through its SCPI server, a plain TCP socket that terminates
        # every line with CR LF. The port manager opens it, so several driver instances (e.g.
        # one per output) share one connection. The port is entered as 'ip:5000'.
        self.port_manager = True
        self.port_types = ["SOCKET"]
        self.port_properties = {
            "SOCKET_EOLwrite": "\r\n",
            "SOCKET_EOLread": "\r\n",
            # A timeout is essential: without it an unanswered query blocks the driver forever,
            # which can happen if the instrument runs an ecosystem that does not know a command.
            "timeout": 5,
            "fixed_port": 5000,  # the SCPI server always listens on 5000
        }

        # GUI parameters, exactly as they arrive from the GUI
        self.gui_parameters: dict[str, Any] = {}

        self.channel: str | int = 1
        self.sweep_mode: str = "None"
        self.waveform: str = "Sine"
        self.periodfrequency: str = "Frequency in Hz"
        self.periodfrequencyvalue: str | float = 1000.0
        self.amplitudehilevel: str = "Amplitude in V"
        self.amplitudehilevelvalue: str | float = 0.9
        self.offsetlolevel: str = "Offset in V"
        self.offsetlolevelvalue: str | float = 0.0
        self.delayphase: str = "Phase in °"
        self.delayphasevalue: str | float = 0.0
        self.dutycyclepulsewidth: str = "Duty cycle in %"
        self.dutycyclepulsewidthvalue: str | float = 50.0
        self.triggertype: str = "Internal"
        self.operationmode: str = "Continuous"
        self.burstnumber: str | int = 1
        self.periodnumber: str | int = 3
        self.burstdelay: str | float = 0.0
        self.waveformarray: Any = ""

        # Values derived during configure
        self.frequency: float = 1000.0
        self.phase: float = 0.0
        self.amplitude: float = 0.9
        self.offset: float = 0.0
        self.dutycycle: float = 0.5
        self.burstperiod: float = 0.0


    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields, depending on the currently selected waveform and operation mode.

        Fields that have no effect for the current selection are not shown, e.g. the duty cycle
        is only relevant for the PWM waveform and the burst fields only for the burst mode.
        """
        new_parameters: dict[str, Any] = {
            "SweepMode": self.sweep_modes,
            "Channel": ["1", "2"],
            "Waveform": list(self.waveforms.keys()),
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 1000,
            "AmplitudeHiLevel": ["Amplitude in V", "High level in V"],
            "AmplitudeHiLevelValue": 0.9,
            "OffsetLoLevel": ["Offset in V", "Low level in V"],
            "OffsetLoLevelValue": 0.0,
            "DelayPhase": ["Phase in °", "Delay in s"],
            "DelayPhaseValue": 0,
        }

        waveform = parameters.get("Waveform", "Sine")

        if waveform == "PWM":
            new_parameters["DutyCyclePulseWidth"] = ["Duty cycle in %"]
            new_parameters["DutyCyclePulseWidthValue"] = 50

        if waveform == "Arbitrary":
            new_parameters["ArbitraryWaveformFile"] = self.get_folder("CUSTOMFILES")

        new_parameters["Trigger"] = list(self.triggertypes.keys())
        new_parameters["OperationMode"] = list(self.operationmodes.keys())

        if parameters.get("OperationMode", "Continuous") == "Burst":
            new_parameters["BurstRepetitions"] = 1
            new_parameters["BurstSignalRepetitions"] = 3
            new_parameters["BurstDelay"] = 0

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the user selections and derive the returned variables.

        The values are only kept as they arrive from the GUI. They are converted to numbers in
        'convert_gui_parameters', which is called from 'configure', because this function can be
        called with incomplete or empty values while the user is still editing the fields.

        The raw values are deliberately kept in a separate dictionary instead of being converted
        in place. SweepMe! may call this function again after 'configure', which would otherwise
        silently replace the converted numbers by the original strings.
        """
        self.gui_parameters = dict(parameters)

        # The channel is needed by every phase function, 'deinitialize' included, which a host
        # driving the driver without 'configure' may call first (e.g. several instances on one
        # board, one per output). It is therefore taken over here already; 'convert_gui_parameters'
        # validates it again. An incomplete value while the user is still editing keeps the old one.
        try:
            self.channel = int(parameters.get("Channel", self.channel))
        except (TypeError, ValueError):
            pass

        self.sweep_mode = parameters.get("SweepMode", "None")

        if self.sweep_mode == "None":
            self.variables = []
            self.units = []
            self.plottype = []
            self.savetype = []
        else:
            # e.g. "High level in V" -> variable "High level", unit "V"
            quantity, _, unit = self.sweep_mode.partition(" in ")
            self.variables = [quantity]
            self.units = [unit]
            self.plottype = [True]
            self.savetype = [True]

    def apply_selectors(self, channel: int) -> None:
        """Take over the channel a bench entry binds, so that the stages act on it (Instrument Control)."""
        self.channel = int(channel)

    def connect(self):
        """Check that the SCPI server answers.

        The socket itself is opened by the port manager, which hands over no port at all when the
        board cannot be reached. Querying '*IDN?' here makes a stopped SCPI server fail at
        connect, with a message, instead of on the first command of the run.
        """
        hint = (
            "Start the SCPI server on the board (web interface -> Development -> SCPI server) "
            "and enter the port as 'ip:5000'."
        )
        if self.port is None:
            msg = f"Signal-RedPitaya_STEMlab: The connection to the board could not be opened. {hint}"
            raise ConnectionError(msg)
        try:
            self.get_identification()
        except (OSError, TimeoutError) as e:
            msg = (
                f"Signal-RedPitaya_STEMlab: No SCPI server answers at "
                f"{self.port.port_properties['ID']}. {hint} Error is: {e}."
            )
            raise ConnectionError(msg) from e

    def deinitialize(self):
        # print("Disable Frequency Generator Channel {}!".format(self.channel))
        self.set_output_state(self.channel, False)

    def configure(self):
        self.convert_gui_parameters()

        self.reset_generator()

        self.set_waveform(self.channel, self.waveforms[self.waveform])

        if self.waveforms[self.waveform] == "ARBITRARY":
            self.set_arbitrary_waveform(self.channel, np.loadtxt(self.waveformarray))

        # Set PWM duty cycle
        if self.waveform == "PWM":
            self._apply_duty_cycle()

        # set frequency
        self._apply_frequency()

        # convert Delay to Phase
        self._apply_phase()

        # convert High level, Low level to Amplitude and Offset
        self._apply_amplitude_offset()

        # set trigger source
        self._apply_trigger_source()

        # set burst mode (after trigger settings!)
        self._apply_burst_mode()

        self.set_output_state(self.channel, True)

        # start the generation
        self._start_generation()

    def apply(self):
        value = float(self.value)
        # Frequency or Period SweepMode
        if self.sweep_mode == "Frequency in Hz" or self.sweep_mode == "Period in s":
            self.periodfrequency = self.sweep_mode
            self.periodfrequencyvalue = value
            self._apply_frequency()
            # 'SOUR<n>:FREQ:FIX' rebuilds the signal, so the generation has to be started again
            self._start_generation()

        # Amplitude or Offset SweepMode
        elif (
            self.sweep_mode == "Amplitude in V"
            or self.sweep_mode == "Offset in V"
            or self.sweep_mode == "High level in V"
            or self.sweep_mode == "Low level in V"
        ):
            # print("sweep:", self.value)
            if (
                self.sweep_mode == "Amplitude in V"
                or self.sweep_mode == "High level in V"
            ):
                self.amplitudehilevel = self.sweep_mode
                self.amplitudehilevelvalue = value
            else:
                self.offsetlolevel = self.sweep_mode
                self.offsetlolevelvalue = value
            # Amplitude and offset are applied by the FPGA without rebuilding the signal, so the
            # generation must not be started again here. Doing so would reset the signal to its
            # start phase at every measurement point and destroy the continuous waveform.
            self._apply_amplitude_offset()

        # Phase or Delay SweepMode
        elif self.sweep_mode == "Phase in °" or self.sweep_mode == "Delay in s":
            self.delayphase = self.sweep_mode
            self.delayphasevalue = value
            self._apply_phase()
            # the phase is only taken over when the signal starts from the beginning
            self._start_generation()

    def call(self):
        if self.sweep_mode != "None":
            return [self.value]
        else:
            return []

    # Functions

    def convert_gui_parameters(self) -> None:
        """Convert the stored GUI parameters to numbers and check them for valid values.

        This is done here and not in 'apply_gui_parameters' because that function can be called
        with incomplete or empty fields while the user is still editing them. It reads from
        'self.gui_parameters' and writes to separate attributes, so that a later call of
        'apply_gui_parameters' cannot revert the converted values back to strings.
        """
        parameters = self.gui_parameters

        # Selections that need no conversion
        self.waveform = parameters.get("Waveform", "Sine")
        self.periodfrequency = parameters.get("PeriodFrequency", "Frequency in Hz")
        self.amplitudehilevel = parameters.get("AmplitudeHiLevel", "Amplitude in V")
        self.offsetlolevel = parameters.get("OffsetLoLevel", "Offset in V")
        self.delayphase = parameters.get("DelayPhase", "Phase in °")
        self.dutycyclepulsewidth = parameters.get(
            "DutyCyclePulseWidth", "Duty cycle in %"
        )
        self.waveformarray = parameters.get("ArbitraryWaveformFile", "")
        self.triggertype = parameters.get("Trigger", "Internal")
        self.operationmode = parameters.get("OperationMode", "Continuous")

        try:
            self.channel = int(parameters.get("Channel", 1))
            self.periodfrequencyvalue = float(
                parameters.get("PeriodFrequencyValue", 1000)
            )
            self.amplitudehilevelvalue = float(
                parameters.get("AmplitudeHiLevelValue", 0.9)
            )
            self.offsetlolevelvalue = float(parameters.get("OffsetLoLevelValue", 0.0))
            self.delayphasevalue = float(parameters.get("DelayPhaseValue", 0))
            self.dutycyclepulsewidthvalue = float(
                parameters.get("DutyCyclePulseWidthValue", 50)
            )
        except ValueError as e:
            msg = f"Signal-RedPitaya_STEMlab: Please enter numeric values into all number fields. Error is: {e}."
            raise ValueError(msg)

        if self.operationmode == "Burst":
            try:
                self.burstnumber = int(parameters.get("BurstRepetitions", 1))
                self.periodnumber = int(parameters.get("BurstSignalRepetitions", 3))
                self.burstdelay = float(parameters.get("BurstDelay", 0))
            except ValueError as e:
                msg = f"Signal-RedPitaya_STEMlab: Please enter numeric values for burst mode. Error is: {e}."
                raise ValueError(msg)

        if self.channel not in (1, 2):
            msg = f"Signal-RedPitaya_STEMlab: Channel must be 1 or 2, but '{self.channel}' was given."
            raise ValueError(msg)

        if self.waveform not in self.waveforms:
            msg = (
                f"Signal-RedPitaya_STEMlab: Unknown waveform '{self.waveform}'. "
                f"Supported waveforms are: {', '.join(self.waveforms)}."
            )
            raise ValueError(msg)

        if self.triggertype not in self.triggertypes:
            msg = (
                f"Signal-RedPitaya_STEMlab: Unknown trigger '{self.triggertype}'. "
                f"Supported triggers are: {', '.join(self.triggertypes)}."
            )
            raise ValueError(msg)

        # The instrument only knows the burst states CONTINUOUS and BURST. Older versions of this
        # driver offered a 'Stream' mode that is not supported by the SCPI server.
        if self.operationmode not in self.operationmodes:
            msg = (
                f"Signal-RedPitaya_STEMlab: Unsupported operation mode '{self.operationmode}'. "
                f"Please select one of: {', '.join(self.operationmodes)}."
            )
            raise ValueError(msg)

        if self.periodfrequency == "Period in s" and self.periodfrequencyvalue <= 0.0:
            msg = "Signal-RedPitaya_STEMlab: The period must be larger than 0 s."
            raise ValueError(msg)

        if (
            self.periodfrequency == "Frequency in Hz"
            and self.periodfrequencyvalue <= 0.0
        ):
            msg = "Signal-RedPitaya_STEMlab: The frequency must be larger than 0 Hz."
            raise ValueError(msg)

        if self.operationmode == "Burst" and self.periodnumber < 1:
            msg = "Signal-RedPitaya_STEMlab: The number of signal periods per burst must be at least 1."
            raise ValueError(msg)

        if self.operationmode == "Burst" and self.burstnumber < 1:
            msg = "Signal-RedPitaya_STEMlab: The number of burst repetitions must be at least 1."
            raise ValueError(msg)

    # -- GUI-driven helpers -----------------------------------------------------
    # They derive the instrument values from the GUI selections and send them through the
    # communication commands below, always for the channel selected in the GUI.

    def _apply_trigger_source(self) -> None:
        """Set the trigger source selected in the GUI.

        'IMM' is not a trigger source of the Red Pitaya SCPI server. Valid sources are EXT_PE,
        EXT_NE, INT and GATED. The GUI option "Immediately" therefore uses the internal trigger
        source and relies on the software trigger sent by '_start_generation'.
        """
        trigger_source = self.triggertypes[self.triggertype]
        if trigger_source == "IMM":
            trigger_source = "INT"

        self.set_trigger_source(self.channel, trigger_source)

    def _start_generation(self) -> None:
        """Start the signal generation for internally triggered signals.

        Since Red Pitaya OS 2.00, 'OUTPUT<n>:STATE ON' only supplies the initial voltage
        ('SOUR<n>:INITValue', 0 V by default) to the output but does not start the generation.
        The generation must be started explicitly, otherwise the output stays at 0 V.

        The command resets the FPGA and the signal starts from the beginning. It must therefore
        only be sent when the signal was (re)built, and never at every measurement point of a
        running continuous signal.
        """
        if self.triggertypes[self.triggertype] in ("INT", "IMM"):
            self.trigger(self.channel)

    def _apply_amplitude_offset(self) -> None:
        """Convert high level / low level to amplitude and offset and send them; refused beyond the output range."""
        if (
            self.amplitudehilevel == "High level in V"
            and self.offsetlolevel == "Low level in V"
        ):
            self.amplitude = abs(
                (self.amplitudehilevelvalue - self.offsetlolevelvalue) / 2
            )
            self.offset = (self.amplitudehilevelvalue + self.offsetlolevelvalue) / 2
        elif (
            self.amplitudehilevel == "High level in V"
            and self.offsetlolevel == "Offset in V"
        ):
            self.amplitude = abs(self.amplitudehilevelvalue - self.offsetlolevelvalue)
            self.offset = self.offsetlolevelvalue
        elif (
            self.amplitudehilevel == "Amplitude in V"
            and self.offsetlolevel == "Low level in V"
        ):
            self.amplitude = self.amplitudehilevelvalue
            self.offset = self.amplitudehilevelvalue + self.offsetlolevelvalue
        elif (
            self.amplitudehilevel == "Amplitude in V"
            and self.offsetlolevel == "Offset in V"
        ):
            self.amplitude = self.amplitudehilevelvalue
            self.offset = self.offsetlolevelvalue

        self.set_amplitude_and_offset(self.channel, self.amplitude, self.offset)

    def _apply_duty_cycle(self) -> None:
        """Convert the duty cycle in % from the GUI to 0..1 and send it."""
        if not 0.0 <= self.dutycyclepulsewidthvalue <= 100.0:  # noqa: PLR2004  # percent
            msg = f"The duty cycle must lie between 0 and 100 %, not {self.dutycyclepulsewidthvalue:g} %."
            raise ValueError(msg)
        self.dutycycle = self.dutycyclepulsewidthvalue / 100.0

        self.set_duty_cycle(self.channel, self.dutycycle)

    def _apply_phase(self) -> None:
        """Convert a delay to a phase if needed and send the phase."""
        if self.delayphase == "Delay in s":
            self.phase = self.frequency * 360 * self.delayphasevalue
        else:
            self.phase = self.delayphasevalue
        if abs(self.phase) > 360:
            # 'math.fmod' keeps the sign of the input, e.g. -450 deg -> -90 deg. Python's '%'
            # returns a non-negative result for a positive modulus, so multiplying it by the sign
            # of the input gives the negated angle for negative phases, e.g. -450 deg -> -270 deg.
            self.phase = math.fmod(self.phase, 360)

        self.set_phase(self.channel, self.phase)

    def _apply_frequency(self) -> None:
        """Convert a period to a frequency if needed and send the frequency."""
        if self.periodfrequency == "Period in s":
            self.frequency = 1.0 / self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue

        self.set_frequency(self.channel, self.frequency)

    def _apply_burst_mode(self) -> None:
        """Send the operation mode and, for bursts, the burst timing from the GUI."""
        self.set_burst_state(self.channel, self.operationmodes[self.operationmode])
        if self.operationmodes[self.operationmode] != "CONTINUOUS":
            # total burst period in us (signal + delay)
            self.burstperiod = 10**6 * (
                self.periodnumber / self.frequency + self.burstdelay
            )
            self.set_burst_period(self.channel, self.burstperiod)
            self.set_burst_repetitions(self.channel, self.burstnumber)
            self.set_burst_cycles(self.channel, self.periodnumber)

    # -- Communication commands -------------------------------------------------
    # One SCPI command each, declared with pysweepme's @command, so that a pysweepme script or an agent can address
    # every property of the generator directly and every call is checked against the annotations. 'channel' is the
    # output, 1 or 2. The SCPI server does not acknowledge set commands, so a set does not read back.
    # Reference:
    # https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-gen.html

    @command(hazards="Resets both outputs of the board, also one that another driver instance drives.")
    def reset_generator(self) -> None:
        """Reset both generator channels to their default settings ('GEN:RST')."""
        self.port.write("GEN:RST")

    @command
    def set_waveform(self, channel: Channel, waveform: Waveform) -> None:
        """Set the waveform: SINE, SQUARE, TRIANGLE, SAWU, SAWD, PWM, ARBITRARY or DC ('SOUR<n>:FUNC')."""
        self.port.write("SOUR{0}:FUNC {1}".format(channel, waveform))

    @command(returns=("waveform",), reads="setpoint")
    def get_waveform(self, channel: Channel) -> str:
        """Return the waveform as SCPI name, e.g. 'SINE'."""
        return self.port.query("SOUR{0}:FUNC?".format(channel))

    @command
    def set_arbitrary_waveform(self, channel: Channel, data: list) -> None:
        """Upload an arbitrary waveform: 16384 samples normalized to -1..1 ('SOUR<n>:TRAC:DATA:DATA').

        With fewer samples the output frequency is higher than the configured one. The waveform
        must be selected with set_waveform(channel, "ARBITRARY") to be used.
        """
        samples = np.asarray(data, dtype=float).ravel()
        # 'np.nan' as threshold is not accepted anymore since numpy 1.24, use sys.maxsize instead
        np.set_printoptions(threshold=sys.maxsize)
        self.port.write(
            "SOUR{0}:TRAC:DATA:DATA {1}".format(
                channel,
                np.array2string(samples, precision=5, separator=",")[1:-1]
                .replace(" ", "")
                .replace("\n", ""),
            )
        )

    @command
    def set_frequency(self, channel: Channel, frequency: Hertz) -> None:
        """Set the frequency in Hz ('SOUR<n>:FREQ:FIX', 1 Hz to 50 MHz, board dependent).

        The instrument rebuilds the signal; with the internal trigger source the generation
        has to be started again with trigger(channel) afterwards.
        """
        self.port.write("SOUR{0}:FREQ:FIX {1:1.7f}".format(channel, frequency))

    @command(returns=("frequency",), reads="setpoint")
    def get_frequency(self, channel: Channel) -> Hertz:
        """Return the frequency in Hz."""
        return float(self.port.query("SOUR{0}:FREQ:FIX?".format(channel)))

    @command
    def set_phase(self, channel: Channel, phase: Phase) -> None:
        """Set the phase in degrees ('SOUR<n>:PHAS', -360 to 360).

        The phase is only taken over when the signal starts from the beginning, i.e. after
        trigger(channel).
        """
        self.port.write("SOUR{0}:PHAS {1:1.7f}".format(channel, phase))

    @command(returns=("phase",), reads="setpoint")
    def get_phase(self, channel: Channel) -> Phase:
        """Return the phase in degrees."""
        return float(self.port.query("SOUR{0}:PHAS?".format(channel)))

    @command(composite=True)  # reads the offset to check the output range
    def set_amplitude(self, channel: Channel, amplitude: Volts) -> None:
        """Set the one-way amplitude in V ('SOUR<n>:VOLT').

        Amplitude plus absolute offset must stay within the output range (+/- 1 V on STEMlab), else the amplitude is
        refused; set_amplitude_and_offset changes both. The amplitude is applied without restarting the signal.
        """
        _check_output_range(amplitude, self.get_offset(channel))
        self.port.write("SOUR{0}:VOLT {1:1.7f}".format(channel, amplitude))

    @command(returns=("amplitude",), reads="setpoint")
    def get_amplitude(self, channel: Channel) -> Volts:
        """Return the one-way amplitude in V."""
        return float(self.port.query("SOUR{0}:VOLT?".format(channel)))

    @command(composite=True)  # reads the amplitude to check the output range
    def set_offset(self, channel: Channel, offset: Volts) -> None:
        """Set the DC offset in V ('SOUR<n>:VOLT:OFFS'). Applied without restarting the signal.

        Amplitude plus absolute offset must stay within the output range (+/- 1 V on STEMlab), else the offset is
        refused; set_amplitude_and_offset changes both.
        """
        _check_output_range(self.get_amplitude(channel), offset)
        self.port.write("SOUR{0}:VOLT:OFFS {1:1.7f}".format(channel, offset))

    @command(returns=("offset",), reads="setpoint")
    def get_offset(self, channel: Channel) -> Volts:
        """Return the DC offset in V."""
        return float(self.port.query("SOUR{0}:VOLT:OFFS?".format(channel)))

    @command(composite=True)
    def set_amplitude_and_offset(self, channel: Channel, amplitude: Volts, offset: Volts) -> None:
        """Set amplitude and offset in V together, in the order that keeps the output range at every step.

        Refused, with nothing sent, when amplitude plus absolute offset exceed the output range (+/- 1 V on STEMlab).
        """
        _check_output_range(amplitude, offset)
        # One of the two orders always stays within the range when the old and the new pair do
        if abs(amplitude) + abs(self.get_offset(channel)) <= OUTPUT_RANGE:
            self.set_amplitude(channel, amplitude)
            self.set_offset(channel, offset)
        else:
            self.set_offset(channel, offset)
            self.set_amplitude(channel, amplitude)

    @command
    def set_duty_cycle(self, channel: Channel, duty_cycle: DutyCycle) -> None:
        """Set the duty cycle of the PWM waveform as a fraction 0..1 ('SOUR<n>:DCYC')."""
        self.port.write("SOUR{0}:DCYC {1:1.7f}".format(channel, duty_cycle))

    @command(returns=("duty_cycle",), reads="setpoint")
    def get_duty_cycle(self, channel: Channel) -> DutyCycle:
        """Return the PWM duty cycle as a fraction 0..1."""
        return float(self.port.query("SOUR{0}:DCYC?".format(channel)))

    @command
    def set_trigger_source(self, channel: Channel, source: TriggerSource) -> None:
        """Set the trigger source: INT, EXT_PE, EXT_NE or GATED ('SOUR<n>:TRIG:SOUR')."""
        self.port.write("SOUR{0}:TRIG:SOUR {1}".format(channel, source))

    @command(returns=("source",), reads="setpoint")
    def get_trigger_source(self, channel: Channel) -> TriggerSource:
        """Return the trigger source, e.g. 'INT'."""
        return self.port.query("SOUR{0}:TRIG:SOUR?".format(channel))

    @command(hazards="Restarts the signal from its start phase: a signal that is running jumps.")
    def trigger(self, channel: Channel) -> None:
        """Trigger the channel, i.e. (re)start the generation from the start phase ('SOUR<n>:TRIG:INT').

        Required once after set_output_state(channel, True) since Red Pitaya OS 2.00, and again
        after set_frequency or set_phase, because those rebuild the signal. It resets the FPGA
        and restarts the signal, so it must not be sent repeatedly into a running continuous
        signal. The channel-specific command is used on purpose: the two-channel variant
        'SOUR:TRIG:INT' is a documented known issue of the SCPI server and is silently ignored.
        """
        self.port.write("SOUR{0}:TRIG:INT".format(channel))

    @command
    def set_burst_state(self, channel: Channel, burst_state: BurstState) -> None:
        """Set the operation mode: CONTINUOUS or BURST ('SOUR<n>:BURS:STAT')."""
        self.port.write("SOUR{0}:BURS:STAT {1}".format(channel, burst_state))

    @command(returns=("burst_state",), reads="setpoint")
    def get_burst_state(self, channel: Channel) -> BurstState:
        """Return the operation mode, 'CONTINUOUS' or 'BURST'."""
        return self.port.query("SOUR{0}:BURS:STAT?".format(channel))

    @command
    def set_burst_cycles(self, channel: Channel, cycles: BurstCycles) -> None:
        """Set the number of signal periods in one burst ('SOUR<n>:BURS:NCYC')."""
        self.port.write("SOUR{0}:BURS:NCYC {1}".format(channel, cycles))

    @command(returns=("cycles",), reads="setpoint")
    def get_burst_cycles(self, channel: Channel) -> BurstCycles:
        """Return the number of signal periods in one burst."""
        return int(self.port.query("SOUR{0}:BURS:NCYC?".format(channel)))

    @command
    def set_burst_repetitions(self, channel: Channel, repetitions: BurstRepetitions) -> None:
        """Set the number of bursts ('SOUR<n>:BURS:NOR'); 65536 means infinite."""
        self.port.write("SOUR{0}:BURS:NOR {1}".format(channel, repetitions))

    @command(returns=("repetitions",), reads="setpoint")
    def get_burst_repetitions(self, channel: Channel) -> BurstRepetitions:
        """Return the number of bursts."""
        return int(self.port.query("SOUR{0}:BURS:NOR?".format(channel)))

    @command
    def set_burst_period(self, channel: Channel, period: BurstPeriod) -> None:
        """Set the burst period in us, i.e. signal plus delay until the next burst ('SOUR<n>:BURS:INT:PER')."""
        self.port.write("SOUR{0}:BURS:INT:PER {1}".format(channel, int(round(period))))

    @command(returns=("period",), reads="setpoint")
    def get_burst_period(self, channel: Channel) -> BurstPeriod:
        """Return the burst period in us."""
        return float(self.port.query("SOUR{0}:BURS:INT:PER?".format(channel)))

    @command
    def set_output_state(self, channel: Channel, enabled: OutputOn) -> None:
        """Switch the output on or off ('OUTPUT<n>:STATE').

        Since OS 2.00 switching on only applies the initial voltage; trigger(channel) starts
        the signal.
        """
        self.port.write("OUTPUT{0}:STATE {1}".format(channel, "ON" if enabled else "OFF"))

    @command(returns=("enabled",), reads="setpoint")
    def get_output_state(self, channel: Channel) -> OutputOn:
        """Return whether the output is switched on."""
        answer = self.port.query("OUTPUT{0}:STATE?".format(channel))
        return answer.strip().upper() in ("ON", "1")

    @command(returns=("settings",), reads="setpoint", composite=True)
    def get_settings(self, channel: Channel) -> dict:
        """Return the current generator settings of a channel as a dictionary."""
        return {
            "output": self.get_output_state(channel),
            "waveform": self.get_waveform(channel),
            "frequency": self.get_frequency(channel),
            "phase": self.get_phase(channel),
            "amplitude": self.get_amplitude(channel),
            "offset": self.get_offset(channel),
            "duty_cycle": self.get_duty_cycle(channel),
            "trigger_source": self.get_trigger_source(channel),
            "burst_state": self.get_burst_state(channel),
            "burst_repetitions": self.get_burst_repetitions(channel),
            "burst_cycles": self.get_burst_cycles(channel),
            "burst_period": self.get_burst_period(channel),
        }

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the '*IDN?' string of the board."""
        return self.port.query("*IDN?")

    @command(returns=("board_name",), reads="state")
    def get_board_name(self) -> str:
        """Return the name of the board ('SYSTem:BRD:Name?')."""
        return self.port.query("SYSTem:BRD:Name?")

    @command(returns=("board_id",), reads="state")
    def get_board_id(self) -> str:
        """Return the id of the board ('SYSTem:BRD:ID?')."""
        return self.port.query("SYSTem:BRD:ID?")

    @command(returns=("system_help",), reads="state")
    def get_system_help(self) -> str:
        """Return the list of SCPI commands the server knows ('SYSTem:Help?', several kB)."""
        return self.port.query("SYSTem:Help?")

    @command(returns=("system_version",), reads="state")
    def get_system_version(self) -> str:
        """Return the ecosystem version of the board ('SYST:VERS?')."""
        return self.port.query("SYST:VERS?")
