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
# * Instrument: Rohde & Schwarz NRT-ZXX

from pysweepme.EmptyDeviceClass import EmptyDevice


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

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "NRT-2"

        # SweepMe return parameters
        self.variables = ["Forward", "Reverse"]
        self.units = ["W", "W"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_types = ["GPIB", "USB", "Ethernet"]
        self.port_manager = True
        self.port_string: str = ""
        self.port_properties = {
            "baudrate": 38400,  # default
            "EOL": "\n",
        }

        # Device parameters
        self.measurement_type = {
            "Absolute forward": 1,
            "Absolute reverse": 2,
            "Relative forward": 3,
            "Relative reverse": 4,
        }
        """
        The device has 4 measurement types, and each type has some measurement modes (e.g. calculation/processing of data)
        """

        self.sensor: int = 1
        self.sensors = [1, 2]  # Device supports 2 sensors

        self.carrier_frequency: float = 0.0
        self.zeroing: bool = True

        self.video_bandwidths = {
            "4 kHz": 4e3,
            "200 kHz": 2e5,
            "600 kHz": 6e5,  # only Z14
            "4 MHz": 4e6,  # only Z
        }
        self.video_bandwidth: float = 2e5

        # Measurement parameters
        self.forward_result: float = 0.
        self.reverse_result: float = 0.

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            # "Measurement type": list(self.measurement_type.keys()),
            "Channel": self.sensors,
            "Zero offset correction": True,
            "Carrier frequency in Hz": 0.0,
            "Video bandwidth": list(self.video_bandwidths.keys()),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.sensor = parameter["Channel"]
        self.zeroing = parameter["Zero offset correction"]
        self.video_bandwidth = self.video_bandwidths[parameter["Video bandwidth"]]
        self.carrier_frequency = float(parameter["Carrier frequency in Hz"])

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.port.write("*RST")
        print(f"Connected sensors: {self.get_sensors()}")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.zeroing:
            self.perform_zeroing()

        if self.carrier_frequency != 0.0:
            self.port.write(f"SENS{self.sensor}:FREQ {self.carrier_frequency}")

        if self.video_bandwidth != 0.0:
            self.set_video_bandwidth(self.video_bandwidth)

        # Set result format
        # self.port.write("FORM:SREG ASC")  # ASC, BIN, HEX, OCT - see page 130

        # Use single trigger mode
        # TODO: Check if this is the correct mode or if NORM should be used
        self.port.write("TRIG:MODE:SING")

        # Set measurement mode
        # self.set_measurement_mode()

        # self.port.write("SYST:HELP:HEAD?")
        # ret = self.port.read()
        # print(ret)

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

    def call(self) -> [float, float]:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        # Start the measurement
        self.port.write("TRIG:IMM")  # see documentation page 132
        return self.get_measurement()

    """Wrapper Functions"""

    def perform_zeroing(self) -> None:
        """Performs zeroing for the sensor that is connected to the selected port."""
        # See manual page 161
        self.port.write(f"CAL{self.sensor}:ZERO ONCE")
        self.port.write("*WAI")  # wait for the zeroing to finish

    def set_video_bandwidth(self, bandwidth: float) -> None:
        """Set the video bandwidth of the device."""
        if bandwidth == 4E3:
            fnum = 0
        elif bandwidth == 200E3:
            fnum = 1
        else:
            # Full bandwidth, depending on sensor
            fnum = 2

        self.port.write(f"SENS{self.sensor}:BWID:VID:FNUM {fnum}")
        self.port.read()

    def get_measurement(self) -> [float, float]:
        """Get the measurement values from the device."""
        self.port.write(f"SENS{self.sensor}:DATA?")
        result = self.port.read()
        forward_result = float(result.split(",")[0])
        reverse_result = float(result.split(",")[1])
        return forward_result, reverse_result

    """ Currently unused functions """

    def set_measurement_mode(self) -> None:
        """Determines the data that are processed."""
        abs_forward_types = {
            "Average power": "POWer:FORWard:AVERage",  # default
            "Peak power of an amplitude-modulated signal": "POW:FORW:PEP",
            "Absorbed average power": "POWer:ABSorption:AVERage",
            "Absorbed peak envelope power (PEP)": "POWer:ABSorption:PEP",
            "Average power within a burst": "POWer:FORWard:AVERage:BURSt",
            "Absorbed burst average": "POWer:ABSorption:AVERage:BURSt",
        }
        abs_reverse_types = {
            "Reflected power disabled": "POWer:OFF",
            "Reflected power": "POWer:REVerse",
        }

        rel_forward_types = {
            "Complementary cumulative distribution function": "POWer:FORWard:CCDFunction",
            "Crest factor": "POWer:CFACtor",
        }

        rel_reverse_types = {
            "Standing wave ratio": "POWer: SWRatio",
            "Return loss": "POWer: RLOSs",
            "Reflection coefficient": "POWer: RCOefficient",
            "Reflection ratio": "POWer: RFRatio",
        }

        forward_channel = 1
        command = f"CALC1:FEED{forward_channel}: 'POWer:FORWard:AVERage'"
        self.port.write(command)

    def get_sensors(self) -> str:
        """Get the connected sensors."""
        self.port.write("CAT?")
        return self.port.read()

    def get_identification(self) -> str:
        """Return the identification string of the device."""
        self.port.write("*IDN?")
        return self.port.read()
