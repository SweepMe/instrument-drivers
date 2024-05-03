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


# SweepMe! device class
# Device: Arduino AllPins


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Base class to read out Arduino pins."""
    description = """
        <h3>Arduino AllPins</h3>
        <p>This driver allows to read out given digital and analog pins.</p>
        <p>&nbsp;</p>
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Before the first start, please upload the .ino file that comes with this driver to the Arduino using the
         Arduino IDE.</li>
        <li>Type in the digital channels and analog channels as analog channels. For example "A0, A1, A4" for analog
        inputs.</li>
        <li>If you select "Volt" as unit, the values will be returned between 0-5 V assuming the given
        resolution in Bit. Most Arduino boards come with a resolution of 10 bit (4096 steps)</li>
        <li>If you select "Numerical", an integer value will be returned independent from the resolution or the
        voltage range of the Arduino board.</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <ul>
        <li>If you select analog or digital pins that do no exist at your Arduino board, the driver still reads out
        a value and returns it. So please check yourself whether the requested pins exist.</li>
        </ul>
    """

    def __init__(self) -> None:
        """Initialize the device class."""
        EmptyDevice.__init__(self)

        self.instance_key: str = ""
        self.shortname = "Arduino AllPins"

        self.variables = []
        self.units = []

        self.plottype = [True for x in self.variables]  # True to plot data
        self.savetype = [True for x in self.variables]  # True to save data

        # Communication Parameter
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 3,
            "EOL": "\n",
            "baudrate": 115200,
        }
        self.port_str: str = ""
        self.driver_name: str = ""

        # Device Parameter
        self.max_voltage = 5.0
        self.resolution: int = 4096  # number of steps for 10 bit resolution
        self.unit_dict = {
            "Volt": "V",
            "Numerical": "",
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set standard GUI parameter."""
        return {
            "Digital channels": "2,3,4,5,6,7,8,9,10,11,12,13",
            "Analog channels": "0,1,2,3,4,5,6,7",
            "Analog unit": ["Volt", "Numerical"],
            "Resolution in Bit": 10,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle input from GUI."""
        self.variables = []
        self.units = []

        if parameter["Digital channels"] != "":
            # Remove whitespace and enable input as D1,D2 or 1D, 2D,...
            digital_channels = parameter["Digital channels"].replace(" ", "")
            digital_channels = digital_channels.replace("D", "")

            for pin in digital_channels.split(","):
                if pin != "":
                    self.variables.append("Digital %i" % int(pin))
                    self.units.append("")

        if parameter["Analog channels"] != "":
            # Remove whitespace and enable input as A1,A2 or 1A, 2A,...
            analog_channels = parameter["Analog channels"].replace(" ", "")
            analog_channels = analog_channels.replace("A", "")

            for pin in analog_channels.split(","):
                if pin != "":
                    self.variables.append("Analog %i" % int(pin))
                    self.units.append(self.unit_dict[parameter["Analog unit"]])

        self.resolution = 2 ** int(parameter["Resolution in Bit"]) - 1

        self.port_str = parameter["Port"]
        self.driver_name = parameter["Device"]

    def initialize(self) -> None:
        """Register device in the communication manager."""
        # Set Name/Number of COM Port as key
        self.instance_key = f"{self.driver_name}_{self.port_str}"

        if self.instance_key not in self.device_communication:
            # Wait for Arduino initialization
            self.port.read()
            self.device_communication[self.instance_key] = "Connected"

    def deinitialize(self) -> None:
        """Unregister device from the communication manager."""
        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)

    def measure(self) -> None:
        """Read out the values from the Arduino."""
        command_string = "R"
        for var in self.variables:
            if "Digital" in var:
                pin = int(var.replace("Digital ", ""))
                command_string += f"{pin}D,"
            elif "Analog" in var:
                pin = int(var.replace("Analog ", ""))
                command_string += f"{pin}A,"

        self.port.write(command_string)

    def call(self) -> list:
        """Read out Arduino response and calculate voltages."""
        answer = self.port.read()[:-1]

        ret = []
        for n, val in enumerate(answer.split(",")):
            value = float(val)

            if self.units[n] == "V":
                value *= self.max_voltage / self.resolution

            ret.append(value)

        return ret
