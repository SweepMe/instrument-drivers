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
# * Module: LCRmeter
# * Instrument: Keithley 590

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Keithley 590 LCRmeter."""

    description = ""

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.ranges = {
            "Auto": "R0",
            "2pF": "2pF",  # only for 100kHz
            "20pF": "20pF",
            "200pF": "200pF",
            "2nF": "2nF",
            "20nF": "20nF",
        }

        self.frequencies = {
            "100kHz": "100kHz",
            "1MHz": "1MHz",
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "Address": "15",
            # "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            # "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            # "ValueRMS": 0.02,
            # "ValueBias": 0.0,
            # "Frequency": 1000.0,
            # "Integration": list(self.speeds),
            # "Trigger": ["Internal"],
            # "TriggerDelay": "0.1",
            # "Range": list(self.current_ranges),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.value_level_rms = float(parameter["ValueRMS"])
        self.value_bias = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.integration = self.speeds[parameter["Integration"]]

        self.trigger_type = parameter["Trigger"]  # currently unused
        self.trigger_delay = float(parameter["TriggerDelay"])
        self.measure_range = parameter["Range"]

        # Only use Resistance and reactance measurement
        self.operating_mode = "RjX"

    def connect(self) -> None:
        """Connect to the Keithley 4200-SCS LCRmeter."""

    def initialize(self) -> None:
        """Initialize the Keithley 4200-SCS LCRmeter."""

    def deinitialize(self) -> None:
        """Reset device and close connection."""

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""

    def unconfigure(self) -> None:
        """Reset device."""

    def apply(self) -> None:
        """Apply settings."""

    def measure(self) -> None:
        """Retrieve Impedance results from device."""
        # Only measurement mode RjX is used
        self.resistance, self.reactance = self.measure_impedance()

        self.measured_frequency = self.measure_frequency()
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """
    # TODO: See Manual 4-19 for more commands

    def set_frequency(self, frequency: float) -> None:
        """Set the measurement frequency."""
        frequencies = {
            "100kHz": "F0",
            "1MHz": "F1",
        }
        self.port.write("F0")

    def set_range(self, range: str) -> None:
        """Set the measurement range."""
        ranges_100k = {
            "Auto": "R0",
            "2pF/2uS": "R1",
            "20pF/20uS": "R2",
            "200pF/200uS": "R3",
            "2nF": "R4",
            "R1 x 10": "R5",
            "R2 x 10": "R6",
            "R3 x 10": "R7",
            "R4 x 10": "R8",
            "Auto off": "R9",
        }

        ranges_1M = {
            "Auto": "R0",
            "20pF/200uS": "R1",
            # "20pF/200uS": "R2",  # doubled?
            "200pF/2mS": "R3",
            "2nF/20mS": "R4",
            "Auto off": "R9",
        }

        self.port.write("R0")  # auto

    def set_reading_rate(self, rate: str) -> None:
        """Set the reading rate."""
        rates = {
            "1000 /s": "S0",
            "75 /s": "S1",
            "18 /s": "S2",
            "10 /s": "S3",
            "1 /s": "S4",
        }
        self.port.write("S0")

    def set_trigger_mode_and_source(self, mode: str, source: str) -> None:
        """Set the trigger mode and source.

        modes = {
            "One-shot talk": "T0,0",
            "Sweep, talk": "T0,1",
            "One-shot, GET": "T1,0",
            "Sweep, GET": "T1,1",
            "One-shot, X": "T2,0",
            "Sweep, X": "T2,1",
            "One-shot, external": "T3,0",
            "Sweep, external": "T3,1",
            "One-shot, front panel": "T4,0",
            "Sweep, front panel": "T4,1",
        }
        """
        modes = {
            "One-shot": "0",
            "Sweep": "1",
        }

        sources = {
            "Talk": "0",
            "GET": "1",
            "X": "2",
            "External": "3",
            "Front panel": "4",
        }
        mode = modes["One-shot"]
        source = sources["GET"]

        self.port.write(f"T{source},{mode}")

    def set_zero_on(self, set_on: bool=True) -> None:
        """Set the zero."""
        command = "Z1" if set_on else "Z0"
        self.port.write(command)

    def set_filter_on(self, filter_on: bool=True) -> None:
        """Set the filter."""
        command = "P1" if filter_on else "P0"
        self.port.write(command)

    def set_voltage(self, voltage: float) -> None:
        """Set the voltage."""
        first = -voltage
        last = voltage
        step = voltage / 5

        self.port.write(f"V {first},{last},{step}")

    def set_waveform(self) -> None:
        """0 DC, 1 Single Staircase, 2 Dual Staircase, 3 Pulse Train, 4 External bias source."""
        waveform = 1
        start = 1  # s
        stop = 10
        step = 0.1
        self.port.write(f"W {waveform},{start},{stop},{step}")

    def set_bias_on(self, bias_on: bool = True) -> None:
        """Turn the voltage on."""
        command = "N1" if bias_on else "N0"
        self.port.write(command)
