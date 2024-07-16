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
# * Instrument: Keysight LCRmeter E498xA

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "E489xA"

        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_properties = {
            "timeout": 10,
        }

        self.operating_modes = {
            "R-X": "RX",
            "Cp-D": "CPD",
            "Cp-Gp": "CPG",
            "Cs-Rs": "CSRS",
        }

        self.commands_to_restore = [
            "FUNC:IMP",  # Operating mode
            "FUNC:IMP:RANG:AUTO",  # Auto range on/off
            "DISP:LINE",  # Display line
            # "VOLT",                     # Oscillator strength
            # "CURR",                     # current oscillator
            # "BIAS:VOLT",                # bias level
            "APER",  # average
            "FREQ",  # Frequency
            "AMPL:ALC",  # Automatic level control
            "CORR:LENG",  # Correction length
            "FUNC:IMP:RANG",  # Range value -> must be last and
        ]

    def set_GUIparameter(self) -> dict:
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


    def get_GUIparameter(self, parameter={}):
        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.ValueTypeRMS = parameter["ValueTypeRMS"]
        self.ValueRMS = float(parameter["ValueRMS"])

        self.ValueTypeBias = parameter["ValueTypeBias"]
        self.ValueBias = float(parameter["ValueBias"])

        self.ALC = parameter["ALC"]
        self.integration = parameter["Integration"]
        self.average = int(parameter["Average"])
        self.frequency = float(parameter["Frequency"])

        self.OperatingMode = parameter["OperatingMode"]

        if self.sweepmode.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.sweepmode.startswith("Current"):
            self.bias_mode = "CURR"

        elif self.stepmode.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.stepmode.startswith("Current"):
            self.bias_mode = "CURR"

        elif self.ValueTypeBias.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.ValueTypeBias.startswith("Current"):
            self.bias_mode = "CURR"

        else:
            self.bias_mode = "VOLT"

        self.bias_modes_variables = {"VOLT": "Voltage bias", "CURR": "Current bias"}
        self.bias_modes_units = {"VOLT": "V", "CURR": "A"}

        if self.OperatingMode == "R-X":
            self.variables = ["R", "X", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["Ohm", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]

        elif self.OperatingMode == "Cp-D":
            self.variables = ["Cp", "D", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "", "Hz", self.bias_modes_units[self.bias_mode]]

        elif self.OperatingMode == "Cp-Gp":
            self.variables = ["Cp", "Gp", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "S", "Hz", self.bias_modes_units[self.bias_mode]]

        elif self.OperatingMode == "Cs-Rs":
            self.variables = ["Cs", "Rs", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units = ["F", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]

        self.trigger_type = parameter["Trigger"]

    def initialize(self) -> None:
        """Initialize the device."""
        # store the users device setting
        self.vals_to_restore = {}
        for cmd in self.commands_to_restore:
            self.port.write(cmd + "?")
            answer = self.port.read()
            self.vals_to_restore[cmd] = answer

        # no reset anymore as the device starts with an oscillator amplitude of 1V which
        # can influence sensitive devices.
        # self.port.write("*RST")  # reset configuration

        self.port.write("*CLS")  # clear memory

    def deinitialize(self) -> None:
        """Restore the users device setting."""
        for cmd in self.commands_to_restore:
            self.port.write(cmd + " " + self.vals_to_restore[cmd])

    def configure(self) -> None:
        """Configure the device with the user settings."""
        # Integration and average
        if self.integration == "Short":
            self.integration_string = "SHOR"
        if self.integration == "Medium":
            self.integration_string = "MED"
        if self.integration == "Long":
            self.integration_string = "LONG"

        self.port.write("APER %s,%i" % (self.integration_string, self.average))

        # No Cable correction
        self.port.write("CORR:LENG %iM" % 0)  # cable correction set to 0m

        # ALC
        if self.ALC == "On":
            self.port.write("AMPL:ALC ON")
        elif self.ALC == "Off":
            self.port.write("AMPL:ALC OFF")

        # Measures real (R) and imaginary (X) part of the impedance
        self.port.write("FUNC:IMP %s" % self.operating_modes[self.OperatingMode])

        # Auto range
        self.port.write("FUNC:IMP:RANG:AUTO ON")

        # Standard frequency
        self.port.write("FREQ %1.5eHZ" % self.frequency)

        # Standard bias
        self.port.write("BIAS:%s %1.3e" % (self.bias_mode, self.ValueBias))

        # Oscillator signal
        if self.ValueTypeRMS.startswith("Voltage RMS"):
            self.port.write("VOLT %s MV" % (self.ValueRMS * 1000.0))
        elif self.ValueTypeRMS.startswith("Current RMS"):
            self.port.write("CURR %s MA" % (self.ValueRMS * 1000.0))

        # Trigger
        if self.trigger_type == "Software":
            self.port.write("TRIG:SOUR BUS")
        elif self.trigger_type == "Internal":
            self.port.write("TRIG:SOUR INT")
        elif self.trigger_type == "External":
            self.port.write("TRIG:SOUR EXT")
        else:
            self.port.write("TRIG:SOUR INT")  # default will be internal trigger, i.e. continuous trigger

        # Automatically wait for trigger
        self.port.write("INIT:CONT ON")

        # other option would be: self.port.write("INIT:CONT OFF")
        # in this case one has to use self.port.write("INIT:IMM") before every trigger
        # to set the device into 'wait-for-trigger' state

    def unconfigure(self) -> None:
        """Turn off bias, amplitude control, and trigger."""
        self.port.write("ABOR")  # abort any running command

        self.port.write("BIAS:VOLT 0V")
        self.port.write("AMPL:ALC OFF")  # TODO: it is overwritten by the user setting in deinitialize
        # self.port.write("FREQ 1000HZ")
        self.port.write("VOLT 20 MV")
        # self.port.write("FUNC:IMP CPD")

        self.port.write("TRIG:SOUR INT")
        self.port.write("INIT:CONT ON")

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

    def apply(self) -> None:
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
            self.set_current(value * 1000.)

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
        self.port.write("FETC?;FREQ?;BIAS:VOLT?")

    def read_result(self) -> None:
        """Read the measured values for R, X, F, and bias."""
        answer = self.port.read().split(";")

        self.R, self.X = map(float, answer[0].split(",")[0:2])
        self.F = float(answer[1])
        self.bias = float(answer[2])

    def call(self) -> list:
        """Return measured values for R, X, F, and bias."""
        return [self.R, self.X, self.F, self.bias]

    """ Wrapped Functions """

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

    """ List Sweep Functions """
#         max 201 points
# sweep frequency, signal level, dc bias, dc source
# sweep mode
# sweep parameter selection FREQ, VOLT, CURR A, BIAS V, BIAS A, DC SRC V
# SEQ mode to run all at once, step mode is the thing sweepme already does

    def set_list_mode(self) -> None:
        """Set the list mode to sequence, where one trigger makes all sweep point measurements.

        The alternative is step mode, where one trigger makes one sweep point measurement. This is not needed, as
        the SweepMe! step mode already implements this without needing the list mode.
        """
        self.port.write("LIST:MODE SEQ")
        # Clear the time stamp
        self.port.write("LIST:SEQ:TST:CLE")

    def list_sweep_bias_current(self, values: list) -> None:
        """Create a list sweep for bias current in A."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:BIAS:CURR {value_string}A")

    def list_sweep_bias_voltage(self, values: list) -> None:
        """Create a list sweep for bias voltage in V."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:BIAS:VOLT {value_string}V")

    def list_sweep_current(self, values: list) -> None:
        """Create a list sweep for current."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:CURR {value_string}")

    def list_sweep_frequency(self, values: list) -> None:
        """Create a list sweep for frequency in Hz."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:FREQ {value_string}")

    def list_sweep_dc_source(self, values: list) -> None:
        """Create a list sweep for DC source."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:DCS:VOLT {value_string}")

    def list_sweep_ac_voltage(self, values: list) -> None:
        """Create a list sweep for AC voltage."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:VOLT {value_string}")

    @staticmethod
    def create_value_string(values: list) -> str:
        """Create a string of values."""
        maximum_number_of_values = 201
        if len(values) > maximum_number_of_values:
            msg = f"The list sweep can only have a maximum of {maximum_number_of_values} values."
            raise ValueError(msg)

        return ",".join([f"{value:1.5e}" for value in values])

    def get_list_timestamps(self) -> list:
        """Get the timestamps of the list sweep."""
        # TODO: Might need to define return type and size
        self.port.write("LIST:SEQ:TST:DATA?")
        return self.port.read().split(",")


