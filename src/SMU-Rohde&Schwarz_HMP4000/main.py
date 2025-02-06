# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2025 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank D M S Sultan for providing the initial version of this driver.

# SweepMe! driver
# * Module: SMU
# * Instrument: Rohde&Schwarz HMP4000

import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for Rohde&Schwarz HMP4000 Source Unit."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        # Communication Parameters
        self.shortname = "HMP4000"
        self.port_manager = True
        self.port_types = ["COM", "USBTMC", "TCPIP"]
        self.port_string: str = ""

        self.port_properties = {
            "timeout": 1,
            "EOL": "\n",
            "baudrate": 9600,
        }

        # SweepMe! Parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.commands = {
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

        # Measurement Parameters
        self.source: str = "Voltage in V"
        self.protection: float = 5.0
        self.channel: int = 1

        self.v: float = 0.0
        self.i: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": [
                "Voltage in V",
                "Voltage in V (with wait)",
                "Current in A",
                "Current in A (with wait)",
            ],
            "Channel": [1, 2, 3, 4],
            "RouteOut": ["Front"],
            "Compliance": 5.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.channel = int(parameter["Channel"])

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.port_string.startswith("TCPIP"):
            if self.port_string.endswith("INSTR"):
                msg = (
                    "Instrument does not support VXI-11 standard visa runtime address ending with 'INSTR'."
                    "Only socket based connections sending with 'SOCKET' are supported."
                )
                raise Exception(msg)
            elif self.port_string.endswith("SOCKET"):
                self.port.port.write_termination = "\n"
                self.port.port.read_termination = "\n"
            else:
                msg = "Unhandled TCPIP resource name."
                raise Exception(msg)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # Use the next two lines to check whether a message remains in the buffer
        # residual_message = self.port.read()
        # print("Residual message in buffer")

        # self.port.write("*CLS")  # clear status and output buffers of the HMP

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:SEL ON")

        if self.source.startswith("Voltage"):
            self.port.write("CURR %1.3f" % float(self.protection))
            self.port.write("VOLT 0")

        elif self.source.startswith("Current"):
            self.port.write("VOLT %1.3f" % float(self.protection))
            self.port.write("CURR 0")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:SEL OFF")

    def poweron(self) -> None:
        """Turn on the device.

        This function is called if the measurement procedure enters a branch of the sequencer and the module has not
        been used in the previous branch.
        """
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:GEN ON")

    def poweroff(self) -> None:
        """Turn off the device."""
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:GEN OFF")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.port.write("INST OUT%i" % self.channel)

        if self.source.startswith("Voltage"):
            self.port.write("VOLT %1.3f" % float(self.value))

        elif self.source.startswith("Current"):
            self.port.write("CURR %1.3f" % float(self.value))

        # wait for achieving the set voltage or set current before
        # other channels are changed
        if "(with wait)" in self.source:
            time.sleep(0.5)

    def measure(self) -> None:
        """Trigger the acquisition of data."""
        self.port.write("INST OUT%i" % self.channel)

        self.port.write("MEAS:VOLT?")
        self.v = float(self.port.read())

        self.port.write("MEAS:CURR?")
        self.i = float(self.port.read())

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.v, self.i]

    """ Currently unused functions """

    def get_identification(self) -> str:
        """Get the identification string of the device."""
        self.port.write("*IDN?")
        return self.port.read()
