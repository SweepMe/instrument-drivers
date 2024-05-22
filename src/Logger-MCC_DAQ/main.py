# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023-2024 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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

# Contribution: We like to thank TU Dresden/Shayan Miri for providing the initial version of this driver.

# SweepMe! driver
# *Module: Logger
# *Instrument: Measurement Computing Corporation DAQ devices

from pysweepme import addFolderToPATH
from pysweepme.EmptyDeviceClass import EmptyDevice

addFolderToPATH()

# this driver needs libraries installed by the manufacturer software package Universal Library™
# The ImportError is raised in the find_ports method to allow loading the driver in the GUI
mcculw_library_missing = False
try:
    from mcculw import ul
    from mcculw.device_info import DaqDeviceInfo
    from mcculw.enums import AnalogInputMode, InterfaceType, ULRange
except:
    mcculw_library_missing = True


class Device(EmptyDevice):
    """Driver to read out MCC DAQ devices."""

    description = """
    <h3>MCC High-Speed Multifunction DAQ</h3>
    <h4>Setup</h4>
    <p>To use this driver, installation of Universal Library&trade; from the MCC DAQ Software package is needed. Please
    download it from the <a href="https://digilent.com/reference/software/universal-library/windows/start">Digilent Reference</a></p>
    <h4>Parameters</h4>
    <ul>
    <li>For Single-Ended measurements, the High-Pins (CH0H-CHXH) correspond to the first 0-X Analog Channels and the Low
    -Pins (CH0L-CHXL) correspond to the remaining X+1 - 2X Analog Inputs.</li>
    <li>For Differential measurements, the difference between High and Low Pin of the same number (CH0H-CH0L) is 
    measured.</li>
    <li>The Analog Input Channels should be set as colon-separated integers according to the CH.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize driver parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "MCC-DAQ"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []

        self.board_num = 0  # only fixed board 0 supported at the moment

        self.data = []  # object to store results before they are returned in 'call'

        self.measurement_modes = {
            "Single-Ended": "SINGLE_ENDED",
            "Differential": "DIFFERENTIAL",
        }

        self.port_string: str = ""
        self.analog_input_mode: str = ""
        self.analog_inputs: list = []
        self.daq_info = None

        # AI Range
        if mcculw_library_missing:
            self.available_ai_ranges = {}
        else:
            self.available_ai_ranges = {
                "10 V": ULRange.BIP10VOLTS,
                "5 V": ULRange.BIP5VOLTS,
                "2 V": ULRange.BIP2VOLTS,
                "1 V": ULRange.BIP1VOLTS,
            }
        self.ai_range = None

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set standard GUI parameter."""
        return {
            "Analog input mode": list(self.measurement_modes.keys()),
            "Analog input channels": "0, 1",
            "Analog input range": list(self.available_ai_ranges.keys()),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Parse and store GUI options."""
        self.port_string = parameter["Port"]
        self.analog_input_mode = self.measurement_modes[parameter["Analog input mode"]]
        analog_inputs_str = parameter["Analog input channels"].split(",")
        self.analog_inputs = [int(s.strip()) for s in analog_inputs_str]

        for i in range(len(self.analog_inputs)):
            self.variables.append("AI%d" % self.analog_inputs[i])
            self.units.append("V")

        self.ai_range = self.available_ai_ranges[parameter["Analog input range"]]

    def find_ports(self) -> list:
        """Find ports of available DAQ devices."""
        self.check_mcculw()
        ul.ignore_instacal()
        ul.release_daq_device(self.board_num)

        device_list = self.create_device_list()

        if not device_list:
            device_list = ["No device was found"]

        return device_list

    def connect(self) -> None:
        """Connect to the selected port."""
        self.check_mcculw()
        ul.ignore_instacal()

        inventory = ul.get_daq_device_inventory(InterfaceType.ANY)
        device_list = self.create_device_list()

        if self.port_string in device_list:
            descriptor = inventory[device_list.index(self.port_string)]
        elif self.port_string == "No device was found":
            msg = "Please use 'Find Ports' and select a valid port to continue."
            raise Exception(msg)
        else:
            msg = "Selected port was not found. Please use 'Find ports' and check whether the port still exists."
            raise Exception(msg)

        ul.create_daq_device(self.board_num, descriptor)
        ul.flash_led(self.board_num)

    def disconnect(self) -> None:
        """Disconnect from the device."""
        ul.release_daq_device(self.board_num)

    def initialize(self) -> None:
        """Initialize the DAQ device."""
        daq_dev_info = DaqDeviceInfo(self.board_num)
        if not daq_dev_info.supports_analog_input:
            msg = "The DAQ device does not support analog inputs."
            raise Exception(msg)
        self.daq_info = daq_dev_info.get_ai_info()
        # Number of analog inputs can be retrieved from self.daq_info.num_chans

        # AI Range
        if self.ai_range not in self.daq_info.supported_ranges:
            msg = "The DAQ device does not support this AI range."
            raise Exception(msg)

    def configure(self) -> None:
        """Set input mode to single-ended or differential."""
        ul.a_input_mode(self.board_num, AnalogInputMode[self.analog_input_mode])

    def measure(self) -> None:
        """Read out the analog inputs."""
        self.data = []
        resolution_limit = 16

        for ai in self.analog_inputs:
            # Get a value from the device
            if self.daq_info.resolution <= resolution_limit:
                # Use the a_in method for devices with a resolution <= 16
                value = ul.a_in(self.board_num, ai, self.ai_range)
                # Convert the raw value to engineering units
                voltage = ul.to_eng_units(self.board_num, self.ai_range, value)
            else:
                # Use the a_in_32 method for devices with a resolution > 16
                value = ul.a_in_32(self.board_num, ai, self.ai_range)
                # Convert the raw value to engineering units
                voltage = ul.to_eng_units_32(self.board_num, self.ai_range, value)

            self.data.append(voltage)

    def call(self) -> list:
        """Return the measured data."""
        return self.data

    @staticmethod
    def create_device_list() -> list:
        """Create a list of available DAQ devices."""
        device_list = []
        inventory = ul.get_daq_device_inventory(InterfaceType.ANY)
        if len(inventory) > 0:
            for device in inventory:
                device_list.append(str(device) + "_" + device.unique_id)

        return device_list

    @staticmethod
    def check_mcculw() -> None:
        """Check if the mcculw library is installed."""
        if mcculw_library_missing:
            msg = "MCC DAQ Software missing. Install Universal Library (UL)."
            raise ImportError(msg)
