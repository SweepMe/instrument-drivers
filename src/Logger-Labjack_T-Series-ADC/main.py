# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! device class
# Type: Switch
# Device: Labjack T-series

import imp
import os

# adding the libs folder to path is needed so that the BaseClass can find the labjack ljm package
from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

main_path = os.path.dirname(os.path.abspath(__file__))
driver_name = os.path.basename(main_path)

# We assign a module name that depends on the driver name to make sure each driver imports its own version
# of the Base class as this reduces friction when SweepMe! labjack drivers use different versions of the base class.
Labjack_T_Series_BaseClass = imp.load_source(driver_name + ".BaseClass",
                                             main_path + os.sep + "Labjack_T_Series_BaseClass.py")

html_docu = imp.load_source(driver_name + ".html_docu", main_path + os.sep + "html_docu.py")

import numpy as np


class Device(Labjack_T_Series_BaseClass.LabjackBaseClass):
    """The class that will be used by the switch module to control the instrument.
        Only semantic functions are called by SweepMe!"""

    description = html_docu.html_driver_descript

    def __init__(self):
        super().__init__()

        self.shortname = "Labjack Tx ADC"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        self.parameters = {}
        self.output_highs = []
        self.output_lows = []
        self.results = np.array([])

    def set_GUIparameter(self):

        gui_parameter = {
            "Digital": None,
            "Digital read pins": "EIO0, FIO4",
            "": None,
            "Analog": None,
            "Analog read pins": "AIN1, AIN2",
            "Extended AIN mode": list(Labjack_T_Series_BaseClass.ljm_constants.ADC_EF_FUNCTIONS.keys()),
            "EF config string": ""
        }

        # "Prevent overwrite of Output by read/analogue"
        return gui_parameter

    def get_GUIparameter(self, parameter):
        """ parse and store GUI options"""

        port_string = parameter["Port"]  # "TX:SN"
        try:
            serial_number = int(port_string.split(":SN")[-1])
        except ValueError:
            serial_number = None
        self.parameters["serial number"] = serial_number

        self.user_params = parameter  # stash
        self.parse_GUIparameter()

    def parse_GUIparameter(self):
        """parse params"""

        parameter = self.user_params

        t_series_model = parameter["Port"].split(":SN")[0]

        # pins
        pins_analog_in: str = parameter["Analog read pins"]
        pins_digital_in: str = parameter["Digital read pins"]
        self.analog_in = pins_analog_in.replace(" ", "").split(",")
        self.digital_in = pins_digital_in.replace(" ", "").split(",")
        if self.digital_in == [""]:
            self.digital_in = []
        if self.analog_in == [""]:
            self.analog_in = []

        # EF mode
        self.ef_mode: str = parameter["Extended AIN mode"]
        self.adc_ef_mode = Labjack_T_Series_BaseClass.ljm_constants.ADC_EF_FUNCTIONS[self.ef_mode]

        # validation
        if self.ef_mode.startswith("Thermocouple type") and not t_series_model.find("T7") >= 0:
            raise ValueError("Thermocouple measurements are only available with T7 models")

        # apply EF settings to returns
        variables, units = self.adc_ef_mode.return_names, self.adc_ef_mode.units
        AIN_variables = [ch_name + " " + var for ch_name in self.analog_in for var in variables]
        self.variables = AIN_variables + self.digital_in
        AIN_units = [unit for unit in units for ch_name in self.analog_in]
        self.units = AIN_units + [""] * len(self.digital_in)

        # Parse EF CONFIG
        if self.adc_ef_mode.index != 0:
            ef_config_string: str = parameter["EF config string"]
            ef_config_list = ef_config_string.replace(" ", "").split(",")
            try:
                self.ef_config = dict([tuple(x.split(":")) for x in ef_config_list])
            except ValueError as exc:
                if str(exc).startswith("dictionary update sequence element #0") and len(
                        ef_config_list) == 1:
                    self.ef_config = {}
                else:
                    raise exc

            allowed = ["A", 'B', 'C', 'D', 'E', 'F', 'G']
            keys = list(self.ef_config.keys())
            
            if any(key not in allowed for key in keys):
                raise ValueError(f"EF config keys must be in {allowed}")
            values = [float(x) if x else None for x in self.ef_config.values()]
            self.ef_config = dict(zip(keys, values))
        else:
            self.ef_config = {}

        # temperature units
        if self.ef_mode.startswith("Therm") or self.ef_mode.startswith("RTD"):
            if "A" in self.ef_config:
                temp_units = {0.0: "K", 1.0: "°C", 2.0: "°F"}
                temp_unit = temp_units[self.ef_config["A"]]
                self.units = [unit if unit != "K" else temp_unit for unit in self.units]
            else:
                self.ef_config.update({"A": 0})

    def initialize(self):

        # check no conflicts between DIG and Analog (relevant for T4 flex pins)
        # (NB pins can have two names)
        digital_pin_names_to_numbers = Labjack_T_Series_BaseClass.ljm_constants.DIO_PINS[self.dev_type]
        pin_names = self.analog_in + self.digital_in
        pin_numbers = [
            digital_pin_names_to_numbers[pin] for pin in pin_names if pin in digital_pin_names_to_numbers
        ]
        non_unique = set([x for x in pin_numbers if pin_numbers.count(x) > 1])
        if non_unique:
            pin_names = [
                f"pin {k} (index {v})" for k, v in digital_pin_names_to_numbers.items()
                if v in non_unique
            ]
            raise ValueError(f"Following pins set to both dig and analogue: {pin_names}")

    def configure(self):

        # for the T4 some pins are multi role. Need to be set to Analog
        if self.dev_type == "T4":
            flex_pin_names = Labjack_T_Series_BaseClass.ljm_constants.FLEX_PINS_T4
            flex_analog = [pin_name for pin_name in self.analog_in if pin_name in flex_pin_names]
            flex_digital = [pin_name for pin_name in self.digital_in if pin_name in flex_pin_names]
            if flex_analog:
                self.set_flex_pins_to_analog(flex_analog, set_digital=False)
            if flex_digital:
                self.set_flex_pins_to_analog(flex_digital, set_digital=True)

        self.set_digital_IO(pins_names_inputs=self.digital_in, pin_names_high=[], pin_names_low=[])

        if self.analog_in:
            self.set_adc_extended_function(self.analog_in, self.adc_ef_mode.index)

        # for standard functions skip advanced config
        if self.adc_ef_mode.index == 0:
            return

        config_commands, values = [], []
        for key, item in self.ef_config.items():
            if not item:
                continue
            for ch_name in self.analog_in:
                config_commands += [f"{ch_name}_EF_CONFIG_{key}"]
                values += [float(item)]
            self.write_names(commands=config_commands, values=values)

    def measure(self):

        if self.adc_ef_mode.index == 0:
            self.results = self.read_pins(pin_names=self.analog_in + self.digital_in,
                                          auto_switch_to_input=True)
        else:
            abc = self.adc_ef_mode.read_channels  # eg ["A","B"]
            retrieve_commands = [
                f"{ch_name}_EF_READ_{letter}" for ch_name in self.analog_in for letter in abc
            ]

            if retrieve_commands:
                analog_results = self.read_names(names_list=retrieve_commands)
            else:
                analog_results = np.array([])
            digital_results = self.read_pins(pin_names=self.digital_in, auto_switch_to_input=True)
            if any(digital_results):
                digital_results = np.array([int(x) for x in digital_results])
            self.results = np.hstack([analog_results, digital_results])

    def call(self) -> list:
        """
        """
        return list(self.results)


