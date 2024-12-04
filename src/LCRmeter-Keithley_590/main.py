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

        self.variables = ["C", "G", "Voltage bias"]
        self.units = ["F", "S", "V"]  # TODO: Check units
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_string: str = ""

        # Measurement parameters
        self.sweepmode: str = "None"
        self.bias_type: str = "Voltage bias in V"
        self.bias_value: float = 0

        self.average: int = 1

        self.measure_range: str = "Auto"
        self.ranges = {
            "Auto": "R0",
            "2pF": "2pF",  # only for 100kHz
            "20pF": "20pF",
            "200pF": "200pF",
            "2nF": "2nF",
            "20nF": "20nF",
        }

        self.frequency: str = "100kHz"

        self.trigger: str = "One-shot, talk"
        self.trigger_modes = {
            "One-shot, talk": "T0,0",
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

        self.reading_rate: str = "1000 /s"
        self.reading_rates = {
            "1000 /s": "S0",
            "75 /s": "S1",
            "18 /s": "S2",
            "10 /s": "S3",
            "1 /s": "S4",
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "Address": "15",
            "SweepMode": ["None", "Voltage bias in V"],
            # "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "ValueTypeBias": ["Voltage bias in V:"],
            "ValueBias": 0.0,
            "OperatingMode": ["Parallel", "Series"],
            # "ValueRMS": 0.02,
            "Frequency": 1E8,
            "Integration": list(self.reading_rates.keys()),
            "Average": 1,
            "Range": list(self.ranges.keys()),
            "Trigger": list(self.trigger_modes.keys()),
            # "TriggerDelay": "0.1",

        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]

        self.stepmode = parameter["StepMode"]

        self.bias_type = parameter["ValueTypeBias"]
        self.bias_value = float(parameter["ValueBias"])

        self.value_level_rms = float(parameter["ValueRMS"])

        # TODO: Check for rounding errors
        frequency = round(float(parameter["Frequency"]))
        self.frequency = "1MHz" if frequency == 1E9 else "100kHz"

        self.reading_rate = parameter["Integration"]

        # TODO: Move Exceptions to later
        self.average = int(parameter["Average"])
        if self.average < 1:
            msg = "Average must be greater than 0."
            raise ValueError(msg)

        elif self.average > 450 and self.reading_rate != "1000 /s":
            msg = f"Average {self.average} is too high. Maximum is 450."
            raise ValueError(msg)

        elif self.average > 1350 and self.reading_rate == "1000 /s":
            msg = f"Average {self.average} is too high. Maximum is 1350."
            raise ValueError(msg)

        self.measure_range = parameter["Range"]
        self.trigger = parameter["Trigger"]
        # self.trigger_delay = float(parameter["TriggerDelay"])

        # Only use Resistance and reactance measurement
        # self.operating_mode = "RjX"

    def connect(self) -> None:
        """Connect to the Keithley 4200-SCS LCRmeter."""
        # self.port.write("*RST")  # reset
        # self.port.write("*IDN?")
        # instrument_id = self.port.read()
        # print(f"instrument id: {instrument_id}")

    def initialize(self) -> None:
        """Initialize the Keithley 4200-SCS LCRmeter."""
        self.port.write("RENX")  # Go to remote mode
        # TODO: Put device in remote mode

    def deinitialize(self) -> None:
        """Reset device and close connection."""

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""
        self.set_frequency(self.frequency)
        self.set_range(self.measure_range)
        self.set_zero_on()
        self.set_trigger_mode_and_source(self.trigger)
        self.set_reading_rate(self.reading_rate)

        self.set_data_format()

        if self.bias_type == "Voltage bias in V":
            self.set_bias_on(True)
            self.set_voltage(self.bias_value, averaging=self.average)

    def unconfigure(self) -> None:
        """Reset device."""
        self.set_bias_on(False)

    def apply(self) -> None:
        """Apply settings."""
        if self.sweepmode == "Voltage bias in V":
            self.set_voltage(float(self.value))

    def measure(self) -> None:
        """Retrieve Impedance results from device."""
        # self.port.write("A$")  # Sure? A command is used for plotting
        # Maybe wait for measurement to finish

        # Retrieve trigger overrun error due to too fast request from SweepMe!

        self.port.write("B0X")  # Select current reading in buffer???
        # Example uses B3X
        # Why does the example wait for user input on the device???

        answer = self.port.read()
        # print(f"Answer: {answer}")

        # Answer has type ZTSK 1.23E+0, 4.56E+0, 7.89E+0
        # Values are C, G, V
        # TODO: Use mode to receive resistance, reactance, frequency, and voltage bias
        answer = answer.split(",")

        self.capacitance = float(answer[0][4:])  # Remove prefix of type ZTPK
        self.conductance = float(answer[1])
        self.measured_dc_bias = float(answer[2])  # Voltage
        print(f"Capacitance: {self.capacitance}, conductance: {self.conductance}, voltage: {self.measured_dc_bias}")
        #
        # self.resistance = float(answer[1])

        # # Only measurement mode RjX is used
        # self.resistance, self.reactance = self.measure_impedance()
        #
        # self.measured_frequency = self.measure_frequency()
        # self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> tuple:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return self.capacitance, self.conductance, self.measured_dc_bias
        # return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """
    # TODO: See Manual 4-19 for more commands

    def set_frequency(self, frequency: str) -> None:
        """Set the measurement frequency."""
        command = "F0X" if frequency == "100kHz" else "F1X"
        self.port.write(command)

    def set_range(self, measurement_range: str) -> None:
        """Set the measurement range."""
        if self.frequency == "100kHz":
            ranges = {
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
        else:
            ranges = {
                "Auto": "R0",
                "20pF/200uS": "R1",
                # "20pF/200uS": "R2",  # doubled?
                "200pF/2mS": "R3",
                "2nF/20mS": "R4",
                "Auto off": "R9",
            }

        try:
            range_command = ranges[measurement_range]
        except KeyError:
            msg = f"Range {measurement_range} not available for frequency {self.frequency}."
            range_command = ranges["Auto"]
            print(msg)
            # raise ValueError(msg)

        self.port.write(f"{range_command}X")

    def set_reading_rate(self, rate: str) -> None:
        """Set the reading rate."""
        command = f"S{self.reading_rates[rate]}X"
        self.port.write(command)

    def set_trigger_mode_and_source(self, trigger: str) -> None:
        """Set the trigger mode and source."""
        command = f"T{self.trigger_modes[trigger]}X"
        self.port.write(command)

    def set_zero_on(self, set_on: bool = True) -> None:
        """Set the zero."""
        command = "Z1X" if set_on else "Z0X"
        self.port.write(command)

    def set_filter_on(self, filter_on: bool = True) -> None:
        """Set the filter."""
        command = "P1X" if filter_on else "P0X"
        self.port.write(command)

    def set_voltage(self, voltage: float, list_mode: bool = False, averaging: int = 1) -> None:
        """Set the voltage.

        TODO: Check which parameters are used for which waveform type (manual 3.14)
        Note: minimum step size to be applied is 5mV.
        """
        max_voltage = 20
        if abs(voltage) > max_voltage:
            msg = f"Voltage {voltage} is out of range. Choose between -20 V and 20 V."
            raise ValueError(msg)

        # single voltage
        command = f"V,,,{voltage},{averaging}X"  # Commas needed to skip start, stop, and step values

        if list_mode:
            # TODO: Add List Mode
            first = -voltage
            last = voltage
            step = voltage / 5
            command = f"V {first},{last},{step}X"

        self.port.write(command)

    def set_waveform(self) -> None:
        """0 DC, 1 Single Staircase, 2 Dual Staircase, 3 Pulse Train, 4 External bias source."""
        waveform = 1
        start = 1  # s
        stop = 10
        step = 0.1
        self.port.write(f"W {waveform},{start},{stop},{step}X")

    def set_bias_on(self, bias_on: bool = True) -> None:
        """Turn the voltage on."""
        command = "N1X" if bias_on else "N0X"
        self.port.write(command)

    def set_data_format(self) -> None:
        """Set the data format.

        Possible values:
        G0 Prefix on, suffix off, one reading
        G1 Prefix off, suffix on, one reading
        G2 Prefix on, suffix on, one reading
        G3 Prefix on, suffix off, multiple readings
        G4 Prefix off, suffix on, multiple readings
        G5 Prefix on, suffix on, multiple readings

        Prefix: type of data, e.g. NGPK
        N = Normal
        Z = Zeroed

        T = Triple C,G,V
        C = Capacitance
        G = Conductance
        V = Voltage
        Z = 1/C^2
        R = C/Cp
        D = CA - CD?
        N = [VA-VB]
        C = Constant

        S = Series model
        P = Parallel model

        K = 100kHz Frequency
        M = 1MHz Frequency
        D = Disconnect

        Suffix: buffer location, e.g. B0051
        """
        command = "G0X"
        self.port.write(command)
