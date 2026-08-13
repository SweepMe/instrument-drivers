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
from typing import Any

import numpy as np

from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

import redpitaya_scpi as scpi
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug


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

        # Connection
        self.port: Any = None
        self.ip_address: str = ""

        # Timeout in s for receiving an answer from the SCPI server
        self.port_timeout: float = 5.0

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

        self.limits: float = 1.0  # +/- voltage limit of the fast analog outputs
        self.limits_message_shown: bool = (
            False  # whether the clipping message was shown already
        )

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

        self.ip_address = parameters.get("Port", "")
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

    def connect(self):
        # A timeout is essential: without it an unanswered query blocks the driver forever, which
        # can happen if the instrument runs an ecosystem that does not know a command.
        self.port = scpi.scpi(self.ip_address, timeout=self.port_timeout)

        self.port.write = self.port.tx_txt  # redefine scpi-write command
        self.port.read = self.port.rx_txt  # redefine scpi-read command

        # identification = self.get_identification()
        # print("Identification:", identification)

        # board_name = self.get_board_name()
        # print("Board name:", board_name)

        # version = self.get_system_version()
        # print("Version:", version)

    def disconnect(self):
        """Close the connection to the SCPI server.

        This driver does not use the port manager, so it has to close its socket itself. Without
        it, the socket is only closed when the driver instance is garbage collected, which can be
        much later than the end of the run: after an exception the traceback keeps a reference to
        the frame and therefore to the driver instance. A new instance is created for every run,
        so unclosed sockets accumulate for as long as SweepMe! is open.

        The output is switched off in 'deinitialize', which the sequencer calls before this
        function.
        """
        if self.port is None:
            return

        try:
            self.port.close()
        except OSError:
            debug("Signal-RedPitaya_STEMlab: Could not close the connection to the instrument.")
        finally:
            self.port = None

    def configure(self):
        self.limits = 1.0  # +/- Voltage limit of frequency generator

        # Amplitude and offset are also set during a sweep in 'apply'. The clipping message is
        # only shown once per run to not flood the user with message boxes.
        self.limits_message_shown = False

        self.convert_gui_parameters()

        # Reset Generator
        self.port.write("GEN:RST")

        # Set waveform
        self.port.write(
            "SOUR{0}:FUNC {1}".format(self.channel, self.waveforms[self.waveform])
        )  # Set waveform

        # set arbitrary waveform
        if self.waveforms[self.waveform] == "ARBITRARY":
            self.waveformarray = np.loadtxt(self.waveformarray)
            # 'np.nan' as threshold is not accepted anymore since numpy 1.24, use sys.maxsize instead
            np.set_printoptions(threshold=sys.maxsize)
            self.port.write(
                "SOUR{0}:TRAC:DATA:DATA {1}".format(
                    self.channel,
                    np.array2string(self.waveformarray, precision=5, separator=",")[
                        1:-1
                    ]
                    .replace(" ", "")
                    .replace("\n", ""),
                )
            )

        # Set PWM duty cycle
        if self.waveform == "PWM":
            self.set_duty_cycle()

        # set frequency
        self.set_frequency()

        # convert Delay to Phase
        self.set_phase()

        # convert High level, Low level to Amplitude and Offset
        self.set_amplitude_offset()

        # set trigger source
        self.set_trigger_source()

        # set burst mode (after trigger settings!)
        self.set_burst_mode()

        # enable output
        self.port.write("OUTPUT{0}:STATE ON".format(self.channel))

        # start the generation
        self.start_generation()

    def apply(self):
        value = float(self.value)
        # Frequency or Period SweepMode
        if self.sweep_mode == "Frequency in Hz" or self.sweep_mode == "Period in s":
            self.periodfrequency = self.sweep_mode
            self.periodfrequencyvalue = value
            self.set_frequency()
            # 'SOUR<n>:FREQ:FIX' rebuilds the signal, so the generation has to be started again
            self.start_generation()

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
            self.set_amplitude_offset()

        # Phase or Delay SweepMode
        elif self.sweep_mode == "Phase in °" or self.sweep_mode == "Delay in s":
            self.delayphase = self.sweep_mode
            self.delayphasevalue = value
            self.set_phase()
            # the phase is only taken over when the signal starts from the beginning
            self.start_generation()

    def call(self):
        if self.sweep_mode != "None":
            return [self.value]
        else:
            return []

    def deinitialize(self):
        # print("Disable Frequency Generator Channel {}!".format(self.channel))
        self.port.write("OUTPUT{0}:STATE OFF".format(self.channel))  # disable output

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

    def set_trigger_source(self) -> None:
        """Set the trigger source of the generator.

        'IMM' is not a trigger source of the Red Pitaya SCPI server. Valid sources are EXT_PE,
        EXT_NE, INT and GATED. The GUI option "Immediately" therefore uses the internal trigger
        source and relies on the software trigger sent by 'start_generation'.
        """
        trigger_source = self.triggertypes[self.triggertype]
        if trigger_source == "IMM":
            trigger_source = "INT"

        self.port.write("SOUR{0}:TRIG:SOUR {1}".format(self.channel, trigger_source))

    def start_generation(self) -> None:
        """Start the signal generation for internally triggered signals.

        Since Red Pitaya OS 2.00, 'OUTPUT<n>:STATE ON' only supplies the initial voltage
        ('SOUR<n>:INITValue', 0 V by default) to the output but does not start the generation.
        The generation must be started explicitly, otherwise the output stays at 0 V.

        The command resets the FPGA and the signal starts from the beginning. It must therefore
        only be sent when the signal was (re)built, and never at every measurement point of a
        running continuous signal.

        The channel-specific command is used on purpose: the two-channel variant 'SOUR:TRIG:INT'
        is a documented known issue of the SCPI server and is silently ignored.
        """
        if self.triggertypes[self.triggertype] in ("INT", "IMM"):
            self.port.write("SOUR{0}:TRIG:INT".format(self.channel))

    def set_amplitude_offset(self):
        # convert Highlevel, LowLevel to Amplitude and Offset
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

        # set limits
        self.set_limits()

        # set amplitude
        self.port.write("SOUR{0}:VOLT {1:1.7f}".format(self.channel, self.amplitude))

        # set offset
        self.port.write("SOUR{0}:VOLT:OFFS {1:1.7f}".format(self.channel, self.offset))

    def set_duty_cycle(self):
        # convert duty cycle
        if self.dutycyclepulsewidthvalue < 0.0:
            self.dutycycle = 0.0
        elif self.dutycyclepulsewidthvalue > 100.0:
            self.dutycycle = 1.0
        else:
            self.dutycycle = self.dutycyclepulsewidthvalue / 100.0

        # set duty cycle
        self.port.write("SOUR{0}:DCYC {1:1.7f}".format(self.channel, self.dutycycle))

    def set_phase(self):
        # convert Delay to Phase
        if self.delayphase == "Delay in s":
            self.phase = self.frequency * 360 * self.delayphasevalue
        else:
            self.phase = self.delayphasevalue
        if abs(self.phase) > 360:
            # 'math.fmod' keeps the sign of the input, e.g. -450 deg -> -90 deg. Python's '%'
            # returns a non-negative result for a positive modulus, so multiplying it by the sign
            # of the input gives the negated angle for negative phases, e.g. -450 deg -> -270 deg.
            self.phase = math.fmod(self.phase, 360)

        # set phase
        self.port.write("SOUR{0}:PHAS {1:1.7f}".format(self.channel, self.phase))

    def set_frequency(self):
        # convert period to frequency
        if self.periodfrequency == "Period in s":
            self.frequency = 1.0 / self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue

        # set frequency
        self.port.write(
            "SOUR{0}:FREQ:FIX {1:1.7f}".format(self.channel, self.frequency)
        )

    def set_limits(self):
        """Clip amplitude and offset to the output range of the instrument.

        The sum of the one-way amplitude and the absolute offset must not exceed the output
        range of the fast analog outputs (+/- 1 V). Values that violate this condition are
        clipped and the user is informed, as the resulting signal differs from the requested one.
        """
        requested_amplitude = self.amplitude
        requested_offset = self.offset

        if self.amplitude > self.limits:
            self.amplitude = self.limits
        if abs(self.offset) > self.limits:
            self.offset = self.limits * np.sign(self.offset)
        if abs(abs(self.offset) + self.amplitude) > self.limits:
            self.offset = np.sign(self.offset) * (self.limits - self.amplitude)

        if self.amplitude != requested_amplitude or self.offset != requested_offset:
            msg = (
                "Signal-RedPitaya_STEMlab: Amplitude and offset exceed the output range of "
                "+/- {0} V and have been clipped.\n"
                "Requested: amplitude {1} V, offset {2} V\n"
                "Used: amplitude {3} V, offset {4} V".format(
                    self.limits,
                    requested_amplitude,
                    requested_offset,
                    self.amplitude,
                    self.offset,
                )
            )
            debug(msg)
            if not self.limits_message_shown:
                self.limits_message_shown = True
                self.message_box(msg)

    def settings_status(self):
        print("\nFrequency generator channel {0} settings:".format(self.channel))
        self.port.write("OUTPUT{0}:STATE?".format(self.channel))
        print("\tOutput status:", self.port.read())
        self.port.write("SOUR{0}:FUNC?".format(self.channel))
        print("\tWaveform:", self.port.read())
        self.port.write("SOUR{0}:FREQ:FIX?".format(self.channel))
        print("\tFrequency:", self.port.read())
        self.port.write("SOUR{0}:PHAS?".format(self.channel))
        print("\tPhase:", self.port.read())
        self.port.write("SOUR{0}:VOLT?".format(self.channel))
        print("\tAmplitude:", self.port.read())
        self.port.write("SOUR{0}:VOLT:OFFS?".format(self.channel))
        print("\tOffset:", self.port.read())
        self.port.write("SOUR{0}:DCYC?".format(self.channel))
        print("\tDuty cycle:", self.port.read())
        self.port.write("SOUR{0}:BURS:STAT?".format(self.channel))
        print("\tBurst status:", self.port.read())
        self.port.write("SOUR{0}:BURS:NOR?".format(self.channel))
        print("\tNumber of bursts:", self.port.read())
        self.port.write("SOUR{0}:BURS:NCYC?".format(self.channel))
        print("\tNumber of periods in burst:", self.port.read())
        self.port.write("SOUR{0}:BURS:INT:PER?".format(self.channel))
        print("\tBurst period:", self.port.read(), "\n")

    def set_burst_mode(self):
        self.port.write(
            "SOUR{0}:BURS:STAT {1}".format(
                self.channel, self.operationmodes[self.operationmode]
            )
        )  # set OperationMode
        if self.operationmodes[self.operationmode] != "CONTINUOUS":
            self.burstperiod = 10**6 * (
                self.periodnumber / self.frequency + self.burstdelay
            )
            self.port.write(
                "SOUR{0}:BURS:INT:PER {1}".format(self.channel, self.burstperiod)
            )  # total burst period in us (signal + delay)
            self.port.write(
                "SOUR{0}:BURS:NOR {1}".format(self.channel, self.burstnumber)
            )  # number of repeated bursts
            self.port.write(
                "SOUR{0}:BURS:NCYC {1}".format(self.channel, self.periodnumber)
            )  # number of periods in one burst

    def get_identification(self):
        self.port.write("*IDN?")
        return self.port.read()

    def get_board_name(self):
        self.port.write("SYSTem:BRD:Name?")
        return self.port.read()

    def get_board_id(self):
        self.port.write("SYSTem:BRD:ID?")
        return self.port.read()

    def get_system_help(self):
        self.port.write("SYSTem:Help?")
        return self.port.read()

    def get_system_version(self):
        self.port.write("SYST:VERS?")
        return self.port.read()
