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

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice

autolab_sdk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\EcoChemie.Autolab.Sdk.dll"
import_failed = False
try:
    clr.AddReference(autolab_sdk_path)
    from EcoChemie.Autolab.Sdk import Instrument
except:
    # TODO: Handle import error
    import_failed = True


class Device(EmptyDevice):
    """Device class for the Metrohm Autolab PGSTAT used as LCRmeter."""

    description = "Metrohm Autolab PGSTAT"

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["|Z|", "Phase", "Frequency", "Voltage bias"]
        self.units = ["", "", "Hz", "V"]  # TODO: Check units
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
        self.identifier: str = ""
        self.port_string: str = ""

        # Device Parameter
        self.autolab = None
        self.adx_path = ""
        self.hardware_setup_file = ""
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
            "1000A": "CR00_1000A",
            "100A": "CR01_100A",
            "80A": "CR02_80A",
            "50A": "CR03_50A",
            "40A": "CR04_40A",
            "20A": "CR05_20A",
            "10A": "CR06_10A",
            "1A": "CR07_1A",
            "100mA": "CR08_100mA",
            "10mA": "CR09_10mA",
            "1mA": "CR10_1mA",
            "100uA": "CR11_100uA",
            "10uA": "CR12_10uA",
            "1uA": "CR13_1uA",
            "100nA": "CR14_100nA",
            "10nA": "CR15_10nA",
            "1nA": "CR16_1nA",
            "100pA": "CR17_100pA",
            "10pA": "CR18_10pA",
            "1pA": "CR19_1pA",
    }

        # Measured Values
        self.resistance: float = 0.0
        self.reactance: float = 0.0
        self.measured_frequency: float = 0.0
        self.measured_dc_bias: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "ValueRMS": 0.02,
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            # "Integration": list(self.speeds),
            "Trigger": ["Internal"],
            # "TriggerDelay": "0.1",
            "Range": list(self.measurement_ranges),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.ac_amplitude = float(parameter["ValueRMS"])
        self.dc_bias = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.measure_range = self.measurement_ranges[parameter["Range"]]

        # Wavetype, IntegrationCycles and Time?, eiBandwidth, enable input?

        self.adx_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.x"
        self.hardware_setup_file = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.AUT83940.xml"

    def connect(self) -> None:
        """Connect to the Metrohm Autolab LCRmeter."""
        if import_failed:
            msg = "Could not import required libraries."
            raise ImportError(msg)

        self.autolab = Instrument()
        self.autolab.AutolabConnection.EmbeddedExeFileToStart = self.adx_path
        self.autolab.set_HardwareSetupFile(self.hardware_setup_file)

        print("Connecting to Autolab...")
        self.autolab.Connect()
        print("Connected to Autolab.")
        self.Fra = self.autolab.Fra
        self.Ei = self.autolab.Ei

    def disconnect(self) -> None:
        """Disconnect from the Metrohm Autolab LCRmeter."""
        self.autolab.Disconnect()

    def initialize(self) -> None:
        """Initialize the Metrohm Autolab LCRmeter."""

    def deinitialize(self) -> None:
        """Reset device and close connection."""

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""
        self.set_frequency(self.frequency)
        # self.set_delay(self.trigger_delay)

        self.set_dc_bias(self.dc_bias)
        self.set_ac_voltage(self.ac_amplitude)

        # self.set_measure_range(self.measure_range)
        self.set_measure_range(1337)

        self.Ei.EnableDsgInput = True
        self.Ei.CellOnOff = self.Ei.EICellOnOff.On

        # Optional?
        self.Fra.WaveType = self.Fra.WaveType.Sine
        self.Fra.MinimumIntegrationCycles = 1
        self.Fra.MinimumIntegrationTime = 0.125

        self.Ei.Bandwidth = self.Ei.EIBandwidth.High_Speed

        # Must have. Did not find the corresponding Fra.End()
        # maybe Fra.Finalize()?
        self.Fra.Start()

    def unconfigure(self) -> None:
        """Reset device."""
        # TODO: Set everything to 0
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
        """Retrieve Impedance results from device."""
        # What about measurement modes?
        self.resistance, self.reactance = self.measure_modulu_and_phase()

        self.measured_frequency = self.measure_frequency()
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """

    """ here wrapped functions start """

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency in Hz."""
        self.Fra.Frequency = frequency

    def set_dc_bias(self, dc_bias: float) -> None:
        """Set the DC bias in V."""
        # TODO: Is this the correct parameter?
        self.Ei.Setpoint = dc_bias

    def set_ac_voltage(self, ac_voltage: float) -> None:
        """Set the AC voltage level in V."""
        self.Fra.Amplitude = ac_voltage

    def set_measure_range(self, measure_range: str) -> None:
        """Set the measurement range."""
        # TODO: Get the stuff
        # measure_range = getattr(self.Ei.EICurrentRange, measure_range)
        self.Ei.CurrenRange = self.Ei.EICurrentRange.CR08_100mA

    def handle_set_value(self, mode: str, value: float) -> None:
        """Depending on the mode, set the value."""
        if mode == "Voltage bias in V":
            self.set_dc_bias(value)

        elif mode == "Voltage level in V":
            self.set_ac_voltage(value)

        elif mode == "Frequency in Hz":
            self.set_frequency(value)

    def measure_modulu_and_phase(self) -> tuple[float, float]:
        """Measure the modulus and phase."""
        # TODO: Is this the correct impedance value?. Check units
        modulus = self.Fra.Modulus[0]
        phase = self.Fra.Phase[0]
        return modulus, phase

    def measure_dc_bias(self) -> float:
        """Returns the DC bias in V."""
        return self.Ei.Setpoint

    def measure_frequency(self) -> float:
        """Measure the frequency in Hz."""
        # TODO: Is it possible to get the frequency from the device?
        return self.Fra.Frequency
