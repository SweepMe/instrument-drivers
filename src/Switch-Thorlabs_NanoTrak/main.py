# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Thorlabs NanoTrak
from __future__ import annotations

import sys

import clr

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error


# Import Kinesis dll
bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)


def add_dotnet_references():
    """Importing Kinesis .NET dll."""
    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericNanoTrakCLI")

    # clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

    import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
    import Thorlabs.MotionControl.GenericMotorCLI as GenericMotorCLI
    import Thorlabs.MotionControl.GenericNanoTrakCLI as GenericNanoTrakCLI
    # import Thorlabs.MotionControl.IntegratedStepperMotorsCLI as IntegratedStepperMotorsCLI

    print("-> Kinesis .NET references added successfully.")

    return DeviceManagerCLI, GenericMotorCLI, GenericNanoTrakCLI


class Device(EmptyDevice):
    """Device class to implement functionalities of Thorlabs NanoTrak via Kinesis."""
    description = """
                    <h3>Driver Template</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>Install Kinesis</li>
                    </ul>
                    """

    dotnet_added = False

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Template"  # short name will be shown in the sequencer

        # Define the variables that can be measured by the device and that are returned by the 'call' function
        self.variables = ["Position"]
        self.units = ["m"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        # self.port_manager = True
        # self.port_types = ["GPIB"]
        # self.port_properties = {
        #     "EOL": "\r\n",
        #     "timeout": 3,
        #     "baudrate": 9600,
        #     "stopbits": 2,
            # "delay": 0.02,
        # }
        self.DeviceManagerCLI = None
        self.GenericMotorCLI = None
        self.GenericNanoTrakCLI = None
        # self.IntegratedStepperMotorsCLI = None

        self.kinesis_device = None
        self.shortname = "K10CR1"
        self.is_simulation = False

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        if not self.dotnet_added:
            self.import_kinesis()

        device_list = self.list_devices()

        # Searching for simulated devices if there are no real devices found
        if not device_list:
            self.DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
            device_list = self.list_devices()
            self.DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

        if not device_list:
            device_list = ["No devices found!"]

        return device_list

    def import_kinesis(self) -> None:
        """Import Kinesis .NET dll."""
        if not self.dotnet_added:
            self.DeviceManagerCLI, self.GenericMotorCLI, self.GenericNanoTrakCLI = add_dotnet_references()
            self.dotnet_added = True

    def list_devices(self) -> list[str]:
        """Lists all devices.

        Bug: Once Simulation mode is switched on, GetDeviceList will also find simulated devices even though simulation
        mode is uninitialized.
        """
        self.DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
        device_list = self.DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
        return [str(serial_num) for serial_num in device_list]

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Position"],
            # "Position": "1",
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        # self.port_string = parameter["Port"]
        self.serial_num = parameter.get("Port", "")
        if not self.dotnet_added:
            self.import_kinesis()

        self.kinesis_device = self.GenericNanoTrakCLI

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.serial_num in ["No devices found!", ""]:
            error("No device connected! Please connect a Thorlabs NanoTrak device.")
            return

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

    def signin(self) -> None:
        """This function is called if the variation of the module that is loading this device class starts."""

    def signout(self) -> None:
        """This function is called if the variation of the module that is loading this device class ends."""

    def reconfigure(self, parameters, keys) -> None:
        """'reconfigure' is called whenever parameters of the GUI change by using the {...}-parameter system."""

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""

    def start(self) -> None:
        """This function can be used to do some first steps before the acquisition of a measurement point starts."""
        debug("->    start")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def reach(self) -> None:
        """'reach' can be added to make sure the latest setvalue applied during 'apply' is reached."""

    def adapt(self) -> None:
        """'adapt' can be used to adapt an instrument to a new situation after other instruments got a new setvalue."""

    def adapt_ready(self) -> None:
        """'adapt_ready' can be used to make sure that a procedure started in 'adapt' is finished.

        Thus, multiple instrument can start an adapt-procedure simultaneously.
        """

    def trigger_ready(self) -> None:
        """'trigger_ready' can be used to make sure that all instruments are ready to start the measurement."""

    def measure(self) -> None:
        """Trigger the acquisition of new data."""

    def request_result(self) -> None:
        """Write command to ask the instrument to send measured data."""

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'request_result'."""

    def process_data(self) -> None:
        """'process_data' can be used for some evaluation of the data before it is returned."""

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [1., 2., 3., 4.]

    def finish(self) -> None:
        """Do some final steps after the acquisition of a measurement point."""

    """Wrapper Functions"""
