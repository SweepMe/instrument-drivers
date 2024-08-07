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

from __future__ import annotations

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver class for Keysight E498xA LCRmeter."""

    def __init__(self) -> None:
        """Initialize driver parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "E489xA"

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_properties = {
            "timeout": 20,
        }

        # Parameters to restore the users device setting
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
        self.vals_to_restore: dict = {}

        self.sweepmode: str = "None"
        self.stepmode: str = "None"

        self.sweepmode_commands = {
            "None": "None",
            "Frequency in Hz": "FREQ",
            "Voltage bias in V": "BIAS:VOLT",
            "Current bias in A": "BIAS:CURR",
            "Voltage RMS in V": "VOLT",
        }

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

        # List Mode
        self.use_list_sweep: bool = False
        self.list_sweep_values: np.ndarray = np.array([])

        self.list_sweep_holdtime: float = 0.0
        self.list_sweep_delaytime: float = 0.0

        # Measured values
        self.variables: list[str] = []
        self.units: list[str] = []

        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data

        self.value_1: float | list[float] = 0.0
        self.value_2: float | list[float] = 0.0
        self.measured_frequency: float | list[float] = 0.0
        self.bias: float | list[float] = 0.0
        self.time_stamps: list[float] = []

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set standard GUI parameter."""
        return {
            "Average": ["1", "2", "4", "8", "16", "32", "64"],
            "SweepMode": list(self.sweepmode_commands),
            "SweepValue": ["List"],
            "StepMode":  list(self.sweepmode_commands),
            "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
            "ValueRMS": 0.02,
            "ValueTypeBias": ["Voltage bias in V:", "Current bias in A:"],
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "OperatingMode": list(self.operating_modes),
            "ALC": ["Off", "On"],
            "Integration": ["Short", "Medium", "Long"],
            "Trigger": ["Software", "Internal", "External"],
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Step width:", "Points (lin.):", "Points (log.):"],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDual": False,
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

        # List Mode
        if parameter["SweepValue"] == "List sweep":
            self.use_list_sweep = True
            self.handle_list_sweep_parameter(parameter)

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

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        list_sweep_type = parameter["ListSweepType"]

        if list_sweep_type == "Sweep":
            # Create the list sweep values
            start = float(parameter["ListSweepStart"])
            end = float(parameter["ListSweepEnd"])

            step_points_type = parameter["ListSweepStepPointsType"]
            step_points_value = float(parameter["ListSweepStepPointsValue"])

            if step_points_type.startswith("Step width"):
                list_sweep_values = np.arange(start, end, step_points_value)
                # include end value
                self.list_sweep_values = np.append(list_sweep_values, end)

            elif step_points_type.startswith("Points (lin.)"):
                self.list_sweep_values = np.linspace(start, end, int(step_points_value))

            elif step_points_type.startswith("Points (log.)"):
                self.list_sweep_values = np.logspace(np.log10(start), np.log10(end), int(step_points_value))

            else:
                msg = f"Unknown step points type: {step_points_type}"
                raise ValueError(msg)

        elif list_sweep_type == "Custom":
            custom_values = parameter["ListSweepCustomValues"]
            self.list_sweep_values = [float(value) for value in custom_values.split(",")]

        else:
            msg = f"Unknown list sweep type: {list_sweep_type}"
            raise ValueError(msg)

        # Add the returning values in reverse order to the list
        if parameter["ListSweepDual"]:
            self.list_sweep_values = np.append(self.list_sweep_values, self.list_sweep_values[::-1])

        # Add time staps to return values
        self.variables.append("Time stamp")
        self.units.append("s")
        self.plottype.append(True)
        self.savetype.append(True)

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
        elif self.trigger_type == "Internal":
            self.port.write("TRIG:SOUR INT")
        elif self.trigger_type == "External":
            self.port.write("TRIG:SOUR EXT")
        else:
            self.port.write("TRIG:SOUR INT")  # default will be internal trigger, i.e. continuous trigger

        if self.use_list_sweep:
            self.set_list_mode()
        else:
            # Set the display page to measurement in case a list sweep was used before
            self.port.write("DISP:PAGE MEAS")

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
        if self.sweepmode != "None" and not self.use_list_sweep:
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
        if self.use_list_sweep:
            if self.sweepmode.startswith("Frequency"):
                self.list_sweep_frequency(self.list_sweep_values.tolist())

            elif self.sweepmode.startswith("Voltage bias"):
                self.list_sweep_bias_voltage(self.list_sweep_values.tolist())

            elif self.sweepmode.startswith("Current bias"):
                self.list_sweep_bias_current(self.list_sweep_values.tolist())

            elif self.sweepmode.startswith("Voltage RMS in V"):
                self.list_sweep_ac_voltage(self.list_sweep_values.tolist())

        if self.trigger_type == "Software":
            # only in case of Software trigger as it will be otherwise created internally or externally
            self.port.write("TRIG:IMM")

        # use the next two lines to check whether the last operation is completed,
        # *OPC? returns 1 whenever the last operation is completed and otherwise stop the further procedure.
        # actually needed if the trigger is set to TRIG:SOUR INT, otherwise there will be missing data
        self.port.write("*OPC?")
        self.port.read()  # reading out the answer of the previous *OPC?

    def request_result(self) -> None:
        """Request the measured values for R+X (depending on measurement mode), F, and bias."""
        if self.use_list_sweep:
            # Request measured values and list sweep values
            # The device cannot handle more than two requests for list values.
            # Therefore, time stamps and bias are requested in the read_results step
            request_command = f"FETC?;LIST:{self.sweepmode_commands[self.sweepmode]}?"
            self.port.write(request_command)
        else:
            # Request measured values, frequency, and bias
            # TODO: Question Axel: Why always bias volt?
            self.port.write(f"FETC?;FREQ?;BIAS:{self.bias_mode}?")

    def read_result(self) -> None:
        """Read the measured values for R+X (depending on measurement mode), F, and bias."""
        if self.use_list_sweep:
            answer = self.port.read().split(";")

            # Measured Values R+X
            value_list = answer[0].split(",")
            reshaped_values = np.array(value_list).reshape(-1, 4)
            self.value_1 = reshaped_values[:, 0].astype(float).tolist()
            self.value_2 = reshaped_values[:, 1].astype(float).tolist()

            # List Sweep Values
            if self.sweepmode.startswith("Frequency"):
                self.measured_frequency = [float(frequency) for frequency in answer[1].split(",")]

                self.port.write("BIAS:VOLT?")
                self.bias = float(self.port.read())
            else:
                self.bias = [float(bias) for bias in answer[1].split(",")]

                self.port.write("FREQ?")
                self.measured_frequency = float(self.port.read())

            # Time Stamps
            self.port.write("LIST:SEQ:TST:DATA?")
            answer = self.port.read()
            self.time_stamps = [float(time_stamp) for time_stamp in answer.split(",")]

        else:
            answer = self.port.read().split(";")
            self.value_1, self.value_2 = map(float, answer[0].split(",")[0:2])
            self.measured_frequency = float(answer[1])
            self.bias = float(answer[2])

    def call(self) -> list:
        """Return measured values for R+X (depending on measurement mode), F, and bias."""
        if self.use_list_sweep:
            result = [self.value_1, self.value_2, self.measured_frequency, self.bias, self.time_stamps]
        else:
            result = [self.value_1, self.value_2, self.measured_frequency, self.bias]

        return result

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

    """ List Sweep Functions """

    def set_list_mode(self) -> None:
        """Set the list mode to sequence, where one trigger makes all sweep point measurements.

        The alternative is step mode, where one trigger makes one sweep point measurement. This is not needed, as
        the SweepMe! step mode already implements this without needing the list mode.
        """
        # Show the list page to enable the list mode
        self.port.write("DISP:PAGE LIST")

        # TODO: Check Clear the list sweep setup
        # self.port.write("LIST:CLE:ALL")

        # Set sequential list sweep
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

    def list_sweep_frequency(self, values: list) -> None:
        """Create a list sweep for frequency in Hz."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:FREQ {value_string}")

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

    """ Currently unused Wrapped functions """

    def list_sweep_current(self, values: list) -> None:
        """Create a list sweep for current."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:CURR {value_string}")

    def list_sweep_dc_source(self, values: list) -> None:
        """Create a list sweep for DC source."""
        value_string = self.create_value_string(values)
        self.port.write(f"LIST:DCS:VOLT {value_string}")

    def get_list_timestamps(self) -> list:
        """Get the timestamps of the list sweep."""
        self.port.write("LIST:SEQ:TST:DATA?")
        return self.port.read().split(",")
