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
# * Module: LCRmeter
# * Instrument: Metrohm Autolab PGSTAT

from __future__ import annotations

import time
from pathlib import Path

import clr
from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Metrohm Autolab PGSTAT used as LCRmeter."""

    description = r"""
    <h3>Metrohm Autolab PGSTAT</h3>
    <p>This driver controls Metrohm Autolab Potentiostats.</p>
    <h4>Setup</h4>
    <p>Install the Autolab SDK 2.1.</p>
    <ul>
    <li>Download the SDK from the <a href="https://www.metrohm.com/en/service/software-center/autolab-sdk.html">Metrohm Homepage</a>. </li>
    <li>Install to the standard path: C:\Program Files\Metrohm Autolab\Autolab SDK 2.1</li>
    <li>As of July 2024, the SDK Version 2.1.7 might not work with older Autolab devices. Contact us at contact@sweep-me.net for help.</li>
    </ul>
    <p>Copy the LCRmeter_Metrohm-AutolabPGSTAT.ini file to public documents/SweepMe!/CustomFiles. This can be done in Tools -&gt; Modules&amp;Devices -&gt; right-click on version number -&gt; copy configuration file to public folder. In this file:</p>
    <ul>
    <li>Set the path to your .Adk Setup File.</li>
    <li>Set the path to the Hardware Setup files for each device.</li>
    <li>These files are typically saved at C:\Program Files\Metrohm Autolab\Autolab SDK 2.1.\Hardware Setup Files</li>
    </ul>
    <h4>General Tips</h4>
    <ul>
    <li>Nova must be closed when starting the measurement.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
        self.identifier: str = ""
        self.port_string: str = ""

        # Device Parameter
        self.autolab = None
        self.adk_path = ""
        self.hardware_setup_file = ""

        if self.load_nova_sdk():
            self.Fra: Instrument.Fra = None
            self.Ei: Instrument.Ei = None

        # Sweep Parameter
        self.sweepmode = None
        self.stepmode = None

        # Measurement Parameters
        self.frequency: float = 0.0
        self.ac_amplitude: float = 0.0
        self.dc_bias: float = 0.0
        self.measure_range: str = ""
        self.measurement_ranges = {
            "1000 A": "CR00_1000A",
            "100 A": "CR01_100A",
            "80 A": "CR02_80A",
            "50 A": "CR03_50A",
            "40 A": "CR04_40A",
            "20 A": "CR05_20A",
            "10 A": "CR06_10A",
            "1 A": "CR07_1A",
            "100 mA": "CR08_100mA",
            "10 mA": "CR09_10mA",
            "1 mA": "CR10_1mA",
            "100 uA": "CR11_100uA",
            "10 uA": "CR12_10uA",
            "1 uA": "CR13_1uA",
            "100 nA": "CR14_100nA",
            "10 nA": "CR15_10nA",
            "1 nA": "CR16_1nA",
            "100 pA": "CR17_100pA",
            "10 pA": "CR18_10pA",
            "1 pA": "CR19_1pA",
        }
        self.speed: str = ""
        self.speeds = {
            "Ultra High Speed": "UltraHigh_Speed",
            "High Speed": "High_Speed",
            "High Stability": "High_Stability",
        }
        self.number_of_cycles: int = 1

        # Measured Values
        self.resistance: float = 0.0
        self.reactance: float = 0.0
        self.measured_frequency: float = 0.0
        self.measured_dc_bias: float = 0.0

        self.is_connected = None

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "ValueRMS": 0.02,
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "Integration": list(self.speeds),
            "Range": list(self.measurement_ranges),
            "Trigger": ["Internal"],
            "Average": list(range(1, 17)),  # maximum of 16 cycles
            "speed": "High Speeeeed",
        }

    def find_ports(self) -> list[str]:
        """Get available hardware setup files defined in the .ini file."""
        try:
            ini_data = self.get_configoptions("Autolab HardwareSetup")
            hardware_setup_files = ini_data["hardware_setup_files"].replace("\n", "").split(",")
        except KeyError:
            hardware_setup_files = []
            debug("Autolab: No HardwareSetup files found in .ini file. Ensure the .ini file is set up correctly.")

        return hardware_setup_files

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.adk_path = self.get_adk_path()
        self.hardware_setup_file = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.ac_amplitude = float(parameter["ValueRMS"])
        self.dc_bias = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.speed = self.speeds[parameter["Integration"]]
        self.measure_range = self.measurement_ranges[parameter["Range"]]
        self.number_of_cycles = int(parameter["Average"])

    def connect(self) -> None:
        """Connect to the Metrohm Autolab LCRmeter."""
        if not self.load_nova_sdk():
            msg = ("Autolab: Could not import Nova SDK. "
                   "Ensure the Nova SDK is installed and the .ini file is set up correctly.")
            raise ImportError(msg)

        self.autolab = Instrument()
        self.autolab.AutolabConnection.EmbeddedExeFileToStart = self.adk_path
        self.autolab.set_HardwareSetupFile(self.hardware_setup_file)

        print("Connecting to Autolab...")
        # TODO: handle error if Nova is still running or not connected to the device
        self.autolab.Connect()
        print("Connected to Autolab.")

        self.is_connected = True

        self.Fra = self.autolab.Fra
        self.Ei = self.autolab.Ei

    def disconnect(self) -> None:
        """Disconnect from the Metrohm Autolab LCRmeter."""

        if self.is_connected:
            self.autolab.Disconnect()

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""
        # Initial Measurement Parameters
        self.set_frequency(self.frequency)
        self.set_dc_bias(self.dc_bias)
        self.set_ac_voltage(self.ac_amplitude)

        # General Measurement Parameters
        self.Fra.WaveType = self.Fra.WaveType.Sine

        # If needed, this parameter could be added to the GUI
        self.Fra.MinimumIntegrationTime = 0.125

        self.Fra.MinimumIntegrationCycles = self.number_of_cycles
        self.set_measure_range(self.measure_range)
        self.set_speed(self.speed)

        # Prepare device
        self.Ei.EnableDsgInput = True
        self.Ei.CellOnOff = self.Ei.EICellOnOff.On

        InstrumentExtensions.SwitchFraOn(self.autolab)
        time.sleep(1)  # wait to stabilize

    def unconfigure(self) -> None:
        """Reset device."""
        self.Ei.CellOnOff = self.Ei.EICellOnOff.Off
        self.Ei.EnableDsgInput = False

    def apply(self) -> None:
        """Apply settings."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

    def measure(self) -> None:
        """Run the measurement."""
        self.Fra.Start()

    def request_result(self) -> None:
        """Retrieve the measured values from the device."""
        self.resistance, self.reactance = self.measure_resistance_reactance()

        # Currently, the set values are returned
        # It is unclear whether it is possible to measure the applied values for frequency and bias voltage
        self.measured_frequency = self.measure_frequency()
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here wrapped functions start """

    def load_nova_sdk(self) -> bool:
        """Get the path to the Nova SDK from the .ini file and load the required libraries."""
        try:
            ini_data = self.get_configoptions("Autolab HardwareSetup")
            sdk_path = ini_data["sdk_path"]
        except KeyError:
            debug("Autolab: No sdk_path found in ini file. Ensure the .ini file is set up correctly.")
            return False

        if Path(sdk_path).exists() is False:
            debug("Autolab: Invalid sdk_path. Ensure the Nova SDK is installed and the .ini file is set up correctly.")
            return False

        autolab_sdk_path = sdk_path + r"\EcoChemie.Autolab.Sdk.dll"
        extension_path = sdk_path + r"\EcoChemie.Autolab.SDK.Extensions.dll"

        try:
            clr.AddReference(autolab_sdk_path)
            clr.AddReference(extension_path)

            global Instrument
            global InstrumentExtensions
            from EcoChemie.Autolab.Sdk import Instrument
            from EcoChemie.Autolab.SDK.Extensions import InstrumentExtensions

        except:
            # TODO: Handle import error
            debug(
                "Autolab: Cannot import libraries. "
                "Ensure the Nova SDK is installed and the .ini file is set up correctly.",
            )
            return False

        return True

    def get_adk_path(self) -> str:
        """Read the ini file and set the adk path."""
        try:
            ini_data = self.get_configoptions("Autolab HardwareSetup")
            adk_path = ini_data["adk_path"]
        except KeyError:
            debug("Autolab: No adk_path found in ini file.")
            return ""

        if Path(adk_path).exists() is False:
            msg = "Autolab: Invalid adk_path. Ensure the .ini file is set up correctly."
            raise Exception(msg)

        return adk_path

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency in Hz."""
        self.Fra.Frequency = frequency

    def set_dc_bias(self, dc_bias: float) -> None:
        """Set the DC bias in V."""
        self.Ei.Setpoint = dc_bias

    def set_ac_voltage(self, ac_voltage: float) -> None:
        """Set the AC voltage level in V."""
        self.Fra.Amplitude = ac_voltage

    def set_speed(self, speed: str) -> None:
        """Set the speed of the measurement."""
        speed = getattr(self.Ei.EIBandwidth, speed)
        self.Ei.Bandwidth = speed

    def set_measure_range(self, measure_range: str) -> None:
        """Set the measurement range from the given ranges of format CR08_100mA."""
        measure_range = getattr(self.Ei.EICurrentRange, measure_range)
        self.Ei.CurrentRange = measure_range

    def handle_set_value(self, mode: str, value: float) -> None:
        """Depending on the mode, set the value."""
        if mode == "Voltage bias in V":
            self.set_dc_bias(value)

        elif mode == "Voltage level in V":
            self.set_ac_voltage(value)

        elif mode == "Frequency in Hz":
            self.set_frequency(value)

    def measure_resistance_reactance(self) -> tuple[float, float]:
        """Measure the resistance R and reactance X.

        The manual describes the following measurement values:
        Ztotal = Fra.Modulus[0]
        Phase = Fra.Phase[0]
        Resistance R: Zreal = Fra.Real[0]
        Reactance X: Zimag = Fra.Imaginary[0]
        """
        resistance = self.Fra.Real[0]
        reactance = self.Fra.Imaginary[0]
        return resistance, reactance

    def measure_dc_bias(self) -> float:
        """Returns the applied DC bias in V. Currently, it returns the set DC bias."""
        return self.Ei.Setpoint

    def measure_frequency(self) -> float:
        """Return the applied frequency in Hz. Currently, it returns the set frequency."""
        # TODO: try frequency = self.Fra.AppliedFrequency[0]
        return self.Fra.Frequency
