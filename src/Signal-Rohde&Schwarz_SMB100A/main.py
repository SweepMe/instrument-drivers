# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Module: Signal
# * Instrument: Rohde&Schwarz SMB100A

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Rohde&Schwarz SMB100A Signal Generator."""

    def __init__(self) -> None:
        """Initialize device parameters."""
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = [
            "USB",
            # "GPIB",
            "TCPIP"
        ]

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        self.pulse_modes = {
            "Burst": 0,
            "Continuous": 1,
            "Trigger burst": 2,
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": [None],
            "Waveform": ["Pulse"],
            "PeriodFrequency": ["Period in s"],  # "Frequency in Hz"],
            "PeriodFrequencyValue": 2e-6,
            "AmplitudeHiLevel": ["High level in V"],  # "Amplitude in V"],
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevel": ["Low level in V"],  # "Offset in V"],
            "OffsetLoLevelValue": 0.0,
            "DelayPhase": ["Delay in s"],  # "Phase in deg"],
            "DelayPhaseValue": 0.0,
            "DutyCyclePulseWidth": ["Pulse width in s"],  # "Duty cycle in %",],
            "DutyCyclePulseWidthValue": 1e-6,
            "RiseTime": 100e-9,
            "FallTime": 100e-9,
            "Impedance": ["50", "1e6"],
            # "OperationMode": ["Range 20 V (slow)", "Range 5 V (fast)"]
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get the GUI parameters."""
        self.port_string = parameter["Port"]
        # self.identifier = "Keithley_4200-SCS_" + self.port_string
        #
        # self.waveform = parameter["Waveform"]
        # self.periodfrequency = parameter["PeriodFrequency"]
        # self.periodfrequencyvalue = float(parameter["PeriodFrequencyValue"])
        # self.amplitudehilevel = parameter["AmplitudeHiLevel"]
        # self.amplitudehilevelvalue = float(parameter["AmplitudeHiLevelValue"])
        # self.offsetlolevel = parameter["OffsetLoLevel"]
        # self.offsetlolevelvalue = float(parameter["OffsetLoLevelValue"])
        # self.dutycyclepulsewidth = parameter["DutyCyclePulseWidth"]
        # self.dutycyclepulsewidthvalue = float(parameter["DutyCyclePulseWidthValue"])
        # self.delayphase = parameter["DelayPhase"]
        # self.delayphasevalue = float(parameter["DelayPhaseValue"])
        # self.impedance_value = parameter["Impedance"]
        #
        # self.rise_time = parameter["RiseTime"]
        # self.fall_time = parameter["FallTime"]
        #
        # self.channel = parameter["Channel"]
        #
        # self.card_name = self.channel.split("-")[0].strip()
        # self.pulse_channel = int(self.channel.split("-")[1][-1])
        #
        # self.shortname = "4200-SCS %s" % parameter["Channel"]

    def connect(self) -> None:
        """Connect to the device."""
        self.port.write("*RST")
        # self.port.write("*CLS")
        self.port.write("*IDN?")
        ret = self.port.read()
        print(f"Connected to: {ret}")

    def initialize(self) -> None:
        """Initialize the device."""

    def configure(self) -> None:
        """Configure the device."""

    def apply(self):
        self.value = float(self.value)

    def measure(self):
        pass

    def call(self):
        return []
