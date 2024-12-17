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
import time

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
                    <h3>Rohde&Schwarz NRT-ZXX Directional Power Sensor</h3>
                    <p>Direct control of the sensor via NRT-Z3 adapter.</p>
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
        self.variables = ["Forward", "Reverse"]
        self.units = ["Unit1", "Unit2"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_types = ["COM"]
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

        # Curated
        self.measurement_mode = [
            "Forward average power",
            "Reverse average power",
            "Peak power",
            "CCDF",
        ]

        self.channel: int = 1
        self.channels = {
            "Forward": 1,
            "Backward": 2,
        }

        self.carrier_frequency: str = "0"

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Carrier frequency in Hz": "0",
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.carrier_frequency = parameter["Carrier frequency in Hz"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        # The device starts with max 10s boot mode followed by 7s selft test. Afterwards it is ready and returns @8E oper
        for _ in range(30):
            self.port.write("APPL")
            ret = self.port.read()
            time.sleep(1)
            if ret.startswith("@8E oper"):
                break
        else:
            msg = "Device not ready"
            raise Exception(msg)

        self.port.write("ID")
        idn = self.port.read()
        print(f"Connected to: {idn}")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.port.write("RESET")  # Reset the device
        print(self.port.read())  # always read out after setting
        # TODO: Before or after connect?
        # self.port.write("DIR AUTO")  # Sensor automatically assigns direction
        if float(self.carrier_frequency) > 0:
            self.port.write(f"FREQ {self.carrier_frequency}")
            self.port.read()

        # Set averaging
        # self.port.write("FILT:AVER:COUN")

        # Or set time
        # self.port.write("FILT:INT:TIME")

        # For triggered measurements
        # self.port.write("FILT:AVER:MODE

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def measure(self) -> None:
        """'measure' should be used to trigger the acquisition of new data."""
        self.forward_result, self.reverse_result = self.trigger_remote_controlled_measurement()

    def call(self) -> str:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        return self.forward_result, self.reverse_result

    """Wrapper Functions"""

    def start_continuous_measurement(self) -> [float, float]:
        """Starts a continuous measurement at a high speed controlled by an internal timer, without any reference to an
        external trigger. Reads the last result.

        No effect of set averaging.
        """
        self.port.write("FTRG")
        ret = self.port.read()
        split_answer = ret.split(" ")

        forward_result = float(split_answer[1])
        reverse_result = float(split_answer[2])
        return forward_result, reverse_result

    def trigger_remote_controlled_measurement(self) -> [float, float]:
        """Start new measurement and read out result. If averaging is enabled it is used."""
        self.port.write("RTRG")
        ret = self.port.read()
        split_answer = ret.split(" ")

        forward_result = float(split_answer[1])
        reverse_result = float(split_answer[2])
        return forward_result, reverse_result

    def clear_buffer(self):
        self.port.write("PURGE")
        self.port.read()

    def set_forward_measurement_function(self):
        forward_modes = {
            "NOTSET": 1,
            "AVER": 2,
            "CBAV": 3,
            "CCDF": 4,
        }
        command = f"FOR:"

    def set_reverse_measurement_function(self):
        command = f"REV:"

    def get_triggered_values(self):
        command = "RTRG"

    def set_averaging(self, count: int):
        if count not in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            raise ValueError("Invalid averaging count")
        self.port.write(f"FILT:AVER:COUN {count}")
        self.port.read()
        # automatically sets FILT:AVER:MODE to USER

    def set_integration(self, time_s: float):
        if time_s < 5E-3 or time_s > 0.1111:
            raise ValueError("Invalid integration time")
        self.port.write(f"FILT:INT:TIME {time_s}")
        self.port.read()
        # automatically sets FILT:INT:MODE to TIME

    def set_video_bandwidth(self):
        bandwidths = [
            4E3,
            2E5,
            6E5,  # only Z14
            4E6,  # only Z44
        ]

    def set_forward_mode(self):
        modes = {
            "Average power": "AVER",  # needs carrier frequency
            "Calculated burst average": "CBAV",  # needs BURS:WIDT and BURS:PER
            "Complementary cumulative distribution function": "CCDF",  # Needs correct video bandwidth
            "Crest factor": "CF", # Needs correct video bandwidth
            "Measured burst average": "MBAV",  # instead of duty cycle needs video bandwidth
            "Peak envelope power": "PEP",  # needs PEP:HOLD and PEP:TIME
        }

        # This also sets the reverse measurement mode
        reverse_mode = {
            "Average power": "Reverse average power",
            "Calculated burst average": "Reverse CBAV",
            "Complementary cumulative distribution function": "Forward average power",  # TODO: Typo in doc???
            "Crest factor": "Forward average power",
            "Measured burst average": "Reverse MBAV",
            "Peak envelope power": "Reverse average power",
        }
        # can also measure reflection coefficient (RCO), return loss (RL), standing wave ratio (SWR)
