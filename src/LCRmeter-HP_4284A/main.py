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
# * Instrument: Hewlett Packard LCRmeter 4284A

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver class for the HP 4284A LCRmeter."""
    def __init__(self) -> None:
        """Initialize the driver parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "HP4284A"

        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "timeout": 20,
        }

        self.commands_to_restore = [
            "FUNC:IMP",                 # Operating mode
            "FUNC:IMP:RANG:AUTO",       # Auto range on/off
            "DISP:LINE",                # Display line
            # "VOLT",                     # Oscillator strength
            # "CURR",                     # current oscillator
            # "BIAS:VOLT",                # bias level
            "APER",                     # average
            "FREQ",                     # Frequency
            "AMPL:ALC",                 # Automatic level control
            "CORR:LENG",                # Correction length
            "FUNC:IMP:RANG",            # Range value -> must be last and
        ]
        self.vals_to_restore: dict = {}

        self.sweepmode: str = "None"
        self.stepmode: str = "None"

        # Bias
        self.bias_modes_variables = {"VOLT": "Voltage bias", "CURR": "Current bias"}
        self.bias_modes_units = {"VOLT": "V", "CURR": "A"}
        self.bias_mode: str = "VOLT"
        self.bias_type: str = ""  # GUI Input string
        self.bias_value: float = 0

        self.rms_type: str = ""
        self.rms_value: float = 0.0

        self.alc: bool = False
        self.integration: str = ""
        self.average: int = 1
        self.frequency: float = 1000.0
        self.trigger_type: str = "Software"

        # Operating mode
        self.operating_modes = {
            "R-X": "RX",
            "Cp-D": "CPD",
            "Cp-Gp": "CPG",
            "Cs-Rs": "CSRS",
        }
        self.operating_mode: str = "R-X"

        # Measured values
        self.variables: list = []
        self.units: list = []

        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data

        self.value_1: float = 0.0
        self.value_2: float = 0.0
        self.measured_frequency: float = 0.0
        self.bias: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set standard GUI parameter."""
        return {
            "Average": ["1", "2", "4", "8", "16", "32", "64"],
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A", "Voltage RMS in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A", "Voltage RMS in V"],
            "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
            "ValueRMS": 0.02,
            "ValueTypeBias": ["Voltage bias in V:", "Current bias in A:"],
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "OperatingMode": list(self.operating_modes.keys()),
            "ALC": ["Off", "On"],
            "Integration": ["Short", "Medium", "Long"],
            "Trigger": ["Software", "Internal", "External"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get the user settings."""
        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.rms_type = parameter["ValueTypeRMS"]
        self.rms_value = float(parameter["ValueRMS"])

        self.bias_type = parameter["ValueTypeBias"]
        self.bias_value = float(parameter["ValueBias"])

        self.alc = parameter["ALC"]
        self.integration = parameter["Integration"]
        self.average = int(parameter["Average"])
        self.frequency = float(parameter["Frequency"])

        self.operating_mode = parameter["OperatingMode"]

        self.handle_bias_mode()
        self.handle_operating_mode(self.operating_mode)

        self.trigger_type = parameter["Trigger"]

    def handle_bias_mode(self) -> None:
        """Choose the bias mode from sweepmode, stepmode, or ValueTypeBias."""
        if self.sweepmode.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.sweepmode.startswith("Current"):
            self.bias_mode = "CURR"

        elif self.stepmode.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.stepmode.startswith("Current"):
            self.bias_mode = "CURR"

        elif self.bias_type.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.bias_type.startswith("Current"):
            self.bias_mode = "CURR"

        else:
            self.bias_mode = "VOLT"

    def handle_operating_mode(self, mode: str) -> None:
        """Set the return variables and units for the chosen operating mode."""
        if mode == "R-X":
            self.variables = ["R", "X", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["Ohm", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]

        elif mode == "Cp-D":
            self.variables = ["Cp", "D", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "", "Hz", self.bias_modes_units[self.bias_mode]]

        elif mode == "Cp-Gp":
            self.variables = ["Cp", "Gp", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "S", "Hz", self.bias_modes_units[self.bias_mode]]

        elif mode == "Cs-Rs":
            self.variables = ["Cs", "Rs", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]

    def initialize(self) -> None:
        """Initialize the device."""
        # store the users device setting
        self.vals_to_restore = {}
        for cmd in self.commands_to_restore:
            self.port.write(cmd + "?")
            answer = self.port.read()
            self.vals_to_restore[cmd] = answer

        # no reset anymore as the device starts with an oscillator amplitude of 1V
        # which can influence sensitive devices.
        # self.port.write("*RST") #  reset configuration

        self.port.write("*CLS")  # clear memory

        # self.port.write("DISP:LINE \"Remote control by SweepMe!\"")

    def deinitialize(self) -> None:
        """Restore the users device setting."""
        for cmd in self.commands_to_restore:
            self.port.write(cmd + " " + self.vals_to_restore[cmd])

    def configure(self) -> None:
        """Configure the device with the user settings."""
        self.set_integration(self.integration, self.average)

        # No Cable correction
        self.port.write("CORR:LENG %iM" % 0)  # cable correction set to 0m

        # ALC
        if self.alc == "On":
            self.port.write("AMPL:ALC ON")
        elif self.alc == "Off":
            self.port.write("AMPL:ALC OFF")

        # Set the operating mode and the return variables
        self.port.write("FUNC:IMP %s" % self.operating_modes[self.operating_mode])

        # Auto range
        self.port.write("FUNC:IMP:RANG:AUTO ON")

        # Standard frequency
        self.port.write("FREQ %1.5eHZ" % self.frequency)

        # Standard bias
        self.port.write("BIAS:%s %1.3e" % (self.bias_mode, self.bias_value))

        # Oscillator signal
        if self.rms_type.startswith("Voltage RMS"):
            self.port.write("VOLT %s MV" % (self.rms_value * 1000.0))
        elif self.rms_type.startswith("Current RMS"):
            self.port.write("CURR %s MA" % (self.rms_value * 1000.0))

        # Trigger
        if self.trigger_type == "Software":
            self.port.write("TRIG:SOUR BUS")
            self.port.write("INIT:CONT OFF")
        elif self.trigger_type == "Internal":
            self.port.write("TRIG:SOUR INT")
            self.port.write("INIT:CONT ON")
        elif self.trigger_type == "External":
            self.port.write("TRIG:SOUR EXT")
            self.port.write("INIT:CONT OFF")
        else:
            self.port.write("TRIG:SOUR INT")  # default will be internal trigger, i.e. continuous trigger
            self.port.write("INIT:CONT ON")

    def unconfigure(self) -> None:
        """Turn off bias, amplitude control, and trigger."""
        self.port.write("ABOR")  # abort any running command

        self.port.write("BIAS:VOLT 0V")
        self.port.write("AMPL:ALC OFF")  # TODO: it is overwritten by the user setting in deinitialize
        # self.port.write("FREQ 1000HZ")
        self.port.write("VOLT 20 MV")
        # self.port.write("FUNC:IMP CPD") 

        self.port.write("TRIG:SOUR INT")  # makes sure the trigger runs again
        self.port.write("INIT:CONT ON")  # starting internal trigger

        # Don't ask me why, but asking any value makes sure that the commands above are correctly set
        # or shown on the display
        # self.port.write("*IDN?")
        # self.port.read()

    def poweron(self) -> None:
        """Switch on the DC bias."""
        self.port.write("BIAS:STAT 1")

    def poweroff(self) -> None:
        """Switch off the DC bias."""
        self.port.write("BIAS:STAT 0")

    def apply(self):
        """Set the device to the sweep and/or step value."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

    def handle_set_value(self, mode: str, value: float) -> None:
        """Set value for sweep or step mode."""
        if mode.startswith("Voltage bias"):
            self.set_bias_voltage(value)

        if mode.startswith("Current bias"):
            self.set_bias_current(value)

        elif self.sweepmode.startswith("Voltage RMS"):
            self.set_voltage(value * 1000.0)

        elif self.sweepmode.startswith("Current RMS"):
            self.set_current(value * 1000.0)

        elif mode.startswith("Frequency"):
            self.set_frequency(value)

    def measure(self) -> None:
        """Start the measurement."""
        # trigger
        if self.trigger_type == "Software":
            # only in case of Software trigger as it will be otherwise created internally or externally
            self.port.write("TRIG:IMM")

        # use the next two lines to check whether the last operation is completed,
        # *OPC? returns 1 whenever the last operation is completed and otherwise stop the further procedure.
        # actually needed if the trigger is set to TRIG:SOUR INT, otherwise there will be missing data
        self.port.write("*OPC?")
        self.port.read()  # reading out the answer of the previous *OPC?

    def request_result(self) -> None:
        """Request the measured values for R, X, F, and bias."""
        self.port.write("FETC?;FREQ?;BIAS:%s?" % self.bias_mode)

    def read_result(self) -> None:
        """Read the measured values for R+X (depending on measurement mode), F, and bias."""
        answer = self.port.read().split(";")

        self.value_1, self.value_2 = map(float, answer[0].split(",")[0:2])
        self.measured_frequency = float(answer[1])
        self.bias = float(answer[2])

    def call(self) -> list:
        """Return measured values for R+X (depending on measurement mode), F, and bias."""
        return [self.value_1, self.value_2, self.measured_frequency, self.bias]

    """ Wrapped Functions """

    def set_integration(self, integration: str, average: int) -> None:
        """Set the integration mode."""
        integration_dict = {"Short": "SHOR", "Medium": "MED", "Long": "LONG"}
        integration_string = integration_dict[integration]

        self.port.write("APER %s,%i" % (integration_string, average))

    def set_bias_voltage(self, value: float) -> None:
        """Set the bias voltage of the device in V."""
        self.port.write(f"BIAS:VOLT {value:1.5e}V")

    def set_bias_current(self, value: float) -> None:
        """Set the bias current of the device in A."""
        self.port.write(f"BIAS:CURR {value:1.5e}A")

    def set_voltage(self, value: float) -> None:
        """Set the voltage of the device in mV."""
        self.port.write(f"VOLT {value} MV")

    def set_current(self, value: float) -> None:
        """Set the current of the device in mA."""
        self.port.write(f"CURR {value} MA")

    def set_frequency(self, value: float) -> None:
        """Set the frequency of the device in Hz."""
        self.port.write(f"FREQ {value:1.5e}HZ")
