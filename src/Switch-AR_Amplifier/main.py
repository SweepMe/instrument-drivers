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
# * Instrument: AR Amplifier

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Switch driver for AR Amplifiers."""

    description = """
                    <h3>AR Amplifier</h3>
                    <p>This driver controls Amplifier devices by Amplifier Research (Now Ametek) such as 15S1G3,
                    30W1000B, and many more that share the same communication protocol.</p>
                    <p>Setup:</p>
                    <ul>
                    <li>Set the Remote-Local Switch to 'Remote'. The status display should show 'POWER: STDBY REMOTE'.
                    </li>
                    <li>Currently only GPIB communication is supported.</li>
                    </ul>
                    <p>Measurement:</p>
                    <ul>
                    <li>Amplification (12 Bit): Input between 0 - 4095</li>
                    <li>Amplification in Percent: Input between 0 - 100</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "AR 12S1G3"

        self.variables = ["Gain"]
        self.units = [""]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "EOL": "\r\n",
            "timeout": 3,
        }

        # Measurement Parameters
        self.mode: str = "Amplification (12 Bit)"

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Amplification (12 Bit)", "Amplification in Percent"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.mode = parameter["SweepMode"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.port.write("R")  # Reset the device

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.port.write("P1")  # Power on

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        self.port.write("P0")  # Power off

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        gain = int(4095 * self.value / 100) if self.mode == "Amplification in Percent" else int(self.value)
        self.set_gain(gain)

    def call(self) -> int:
        """Measure the value of the device."""
        self.port.write("G?")
        ret = self.port.read()
        return int(ret[1:])

    def set_gain(self, gain: int) -> None:
        """Set the gain of the device."""
        if gain < 0 or gain > 4095:
            msg = "Gain must be between 0 and 4095."
            raise ValueError(msg)

        gain = str(int(gain))
        # Command string must be of format 0000 - 4095
        while len(gain) < 4:
            gain = "0" + gain

        self.port.write(f"G{gain}")
