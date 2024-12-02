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
# * Module: Logger
# * Instrument: Template

from pysweepme.EmptyDeviceClass import EmptyDevice
# from pysweepme.ErrorMessage import debug, error

# use the next two lines to add the folder of this device class to the PATH variable
# from FolderManager import addFolderToPATH
# addFolderToPATH()


class Device(EmptyDevice):
    """Child class to implement functionalities of a measurement device."""
    description = """
                    <h3>Rohde&Schwarz NRT2 Power Reflection Meter</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>Requires VISA library</li>
                    <li>Set up remote operation on device</li>
                    </ul>
                    """

    # Requires VISA library
    # Set up remote operation on device

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Template"

        # SweepMe return parameters
        self.variables = ["Variable1",]
        self.units = ["Unit1",]
        self.plottype = [True,]
        self.savetype = [True,]

        # Communication Parameters
        self.port_types = ["GPIB", "USB", "Ethernet"]
        self.port_manager = True
        self.port_string: str = ""
        self.port_properties = {
            "baudrate": 38400,  # default
            "EOL": "\n",
            # "stopbits": 1,
            # "parity": "N",
        }

        # Device parameters
        self.measurement_type = {
            "Absolute forward": 1,
            "Absolute reverse": 2,
            "Relative forward": 3,
            "Relative reverse": 4,
        }

        self.measurement_mode = [
            "Forward Average",
            "Forward CCDF",
            "Forward PEP",
            "Forward Absorption",
            # etc. see manual page 41
        ]

        self.channel: int = 1
        self.channels = {
            "Forward": 1,
            "Backward": 2,
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Measurement type": list(self.measurement_type.keys()),
            "Channel": list(self.channels.keys()),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.channel = self.channels[parameter["Channel"]]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.port.write('*RST')
        self.port.write("*IDN?")
        idn = self.port.read()
        print(f"Connected to: {idn}")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # self.port.write("*RST")  # reset the device
        # self.port.write("SPEC")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # # Trigger
        # self.port.write("TRIG:NORM")  # normal trigger mode

        # Set result format
        # self.port.write("FORM:SREG ASC")  # ASC, BIN, HEX, OCT - see page 130

        # self.port.write("APPL")
        # ret = self.port.read()
        # print(ret)

        self.port.write("TRIG:MODE:FRE")


        # self.port.write("SYST:HELP:HEAD?")
        # ret = self.port.read()
        # print(ret)

        # connected sensors
        # self.port.write("CAT?")
        # ret = self.port.read()
        # print(f"Connected sensors: {ret}")

        # # set resolution
        # resolution_dbm = {
        #     "1": "I",
        #     "0.1": "OI",
        #     "0.01": "OOI",
        #     "0.001": "OOOI",
        # }
        # self.port.write("CALC1:RES OOI")  # set resolution to 0.01 dB
        #
        # self.port.write("SYST:SPE FAST")  # set speed to fast, measured vaues are no longer displayed

        # Define measurement frequency - 1GHz
        # self.port.write("SENS1:FREQ 1 GHz")

        # Set 1st and 2nd measurement function to
        # Forward Power, Reverse Power
        # meas_type = "POW:FORW:AVER,POW:REV"
        # self.port.write(f"CALC1:CHAN{self.channel}:FEED{self.channel} '{meas_type}'")  # power forward average

        # Set power unit to dBm
        # self.port.write("UNIT1:POWER DBM")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def measure(self) -> None:
        """'measure' should be used to trigger the acquisition of new data."""
        sensor = 1

        # Select sensorTRIG: MODE
        #         FREerun
        #         ::
        #         TRIGger
        #         SENSe: DATA?

        # Start the measurement
        self.port.write("TRIG:IMM")  # page 132

        # Retrieve data
        self.port.write("SENS1:DATA?")
        self.result = self.port.read()
        print(self.result)

        # self.port.write("FTRG")
        # ret = self.port.read()
        # print(ret)

    def call(self) -> str:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        return self.result


    """Wrapper Functions"""
