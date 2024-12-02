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
# * Module: Switch
# * Instrument: Rohde&Schwarz HMP4030

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Child class to implement functionalities of a measurement device."""
    description = """
                    <h3>Rohde & Schwarz HMP 4030</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>-</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "RS HMP 4030"

        # SweepMe return parameters
        # self.variables = ["Variable1",]
        # self.units = ["Unit1",]
        # self.plottype = [True,]
        # self.savetype = [True,]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["TCPIP", "USB", "GPIB"]
        self.port_properties = {
            "timeout": 5,
            # "delay": 0.0,
        }

        # Device parameters
        self.some_dict = {
            "key1": "value1",
            "key2": "value2",
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Parameters": list(self.some_dict.keys()),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.port.write("*RST")
        self.port.write("*IDN?")
        idn = self.port.read()
        print(f"\nHello, I am: '{idn}'")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def measure(self) -> None:
        """'measure' should be used to trigger the acquisition of new data.

        If all drivers use this function for this purpose, the data acquisition can start almost simultaneously.
        """

    def call(self) -> list[float]:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables.

        This function can only be omitted if no variables are defined in self.variables.
        """
        return [1., 2., 3., 4.]


    """Wrapper Functions"""
