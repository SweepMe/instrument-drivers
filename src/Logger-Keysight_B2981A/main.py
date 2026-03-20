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
# * Module: Logger
# * Instrument: Keysight B2981A Femto/Picoammeter


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "KeysightB2981A"

        self.port_manager = True
        self.port_types = ["GPIB", "COM", "USB", "TCPIP"]

        self.variables = ["Current DC"]
        self.units = ["A"]
        self.plottype = [True]
        self.savetype = [True]

        self.port_properties = {
            "timeout": 30,
            "EOL": "\r\n",
            "baudrate": 57600,  # must match instrument setting for RS-232
            "TCPIP_EOLwrite": "\r\n",
            "TCPIP_EOLread": "\r\n",
        }

        self.ranges = {
            "Auto": "Auto",
            "2 pA": 2e-12,
            "20 pA": 2e-11,
            "200 pA": 2e-10,
            "2 nA": 2e-9,
            "20 nA": 2e-8,
            "200 nA": 2e-7,
            "2 µA": 2e-6,
            "20 µA": 2e-5,
            "200 µA": 2e-4,
            "2 mA": 2e-3,
            "20 mA": 2e-2,
        }

        self.nplc_types = {
            "Very Fast (0.01)": 0.01,
            "Fast (0.1)": 0.1,  # Device default is 0.1
            "Medium (1.0)": 1.0,
            "Slow (10.0)": 10.0,
            "Very Slow (100.0)": 100.0,
        }

        # Initialize variables
        self.port_string: str = ""
        self.range: str = ""
        self.nplc: str = ""
        self.zero_correct: bool = True
        self.current_value: float = float("nan")

    def update_gui_parameters(self, parameters) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "NPLC": list(self.nplc_types.keys()),
            "Range": list(self.ranges.keys()),
            "Zero Correction": False,
        }
        return gui_parameters

    def apply_gui_parameters(self, parameters) -> None:
        """Read values input by the user"""
        self.port_string = parameters.get("Port")
        self.range = parameters.get("Range")
        self.nplc = parameters.get("NPLC")
        self.zero_correct = parameters.get("Zero Correction")

    def connect(self) -> None:
        pass

    def initialize(self) -> None:
        self.port.write("*RST")  # Resets the device to initial settings
        self.port.write("*CLS")  # Clears the Status Byte register
        self.port.write(":SYST:BEEP:STAT OFF")

    def configure(self) -> None:
        self.port.write(
            ':SENS:FUNC "CURR"'
        )  # Explicitly set device to current measurement mode
        self.port.write(
            f":SENS:CURR:DC:NPLC {self.nplc_types[self.nplc]}"
        )  # Set integration time in number of power line cycles
        self.set_range(self.range)
        self.set_zero_correction(self.zero_correct)
        self.port.write(":FORM:ELEM:SENS CURR")
        self.port.write("INP ON")  # Connect DUT

    def measure(self) -> None:
        self.port.write(":READ?")

    def read_result(self) -> None:
        try:
            answer = self.port.read()
            self.current_value = float(answer.strip())
        except (ValueError, TypeError):
            self.current_value = float("nan")

    def call(self) -> list:
        return [self.current_value]

    def deinitialize(self):
        self.port.write(":SYST:BEEP:STAT ON")

    # Wrapped functions
    def set_range(self, range_sel):
        range_val = self.ranges.get(range_sel)
        if range_val == "Auto":
            self.port.write(":SENS:CURR:DC:RANG:AUTO ON")
        elif isinstance(range_val, float):
            self.port.write(":SENS:CURR:DC:RANG:AUTO OFF")
            self.port.write(f":SENS:CURR:DC:RANG {range_val}")
        else:
            raise ValueError(f"Unable to set range to {range_val}.")

    def set_zero_correction(self, state: bool) -> None:
        """
        Enable or disable input zero correction.
        """
        if state:
            self.port.write("INP:ZCOR ON")
            # Acquire zero-current:
            # - Input must be open or in a known zero-current condition
            # - This is true in the configure-phase of the sequencer
            self.port.write("INP OFF")  # Open input (guaranteed zero current)
            self.port.write("INP:ZCOR:ACQ")  # Acquire zero reference
            self.port.write("INP ON")  # Reconnect DUT
        else:
            self.port.write("INP:ZCOR OFF")

    def get_identification(self) -> str:
        self.port.write("*IDN?")
        return self.port.read()
