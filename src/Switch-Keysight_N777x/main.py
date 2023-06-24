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

# import time

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!
# from pysweepme.ErrorMessage import error
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

# from error_codes_N777x import ERROR_CODES


class Device(EmptyDevice):

    description = """
                <h3>Driver for the Keysight N777x Tuneable Laser</h3>
                <p>The driver supports wavelength and power sweeps in various units<br></p>
                <p><FONT COLOR="#ff0000"> <b>Safety Warning</b>: the user is responsible for the
                 safe operation of the laser and checking that the laser is in a safe state after
                 each SweepMe! run finishes.</p>
                <p>&nbsp;</p>
                """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "N777x"  # short name will be shown in the sequencer
        self.variables = ["Wavelength", "Power"]
        self.units = ["nm", "W"]  # will be overwritten in get_GUIparameter
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Port configuration
        self.port_manager = True
        self.port_types = ["GPIB", "USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 10,
            "EOL": '\n',
        }

        # tracking & init
        self.wln = None
        self.wln_from_inst = None
        self.power_level = None
        self.power_from_inst = None
        self.pow_max = None
        self.pow_min = None
        self.wln_max = None
        self.wln_min = None
        self.power_conversion = 1
        self.wln_conversion = 1
        self.power_unit = None
        self.wln_unit = None
        self.sweepmode = "None"
        self.port_string = ""

        self.allowed_power_units = {
            "dBm": "DBM",  # default
            "W": "W",
            "mW": "W",  # instrument doesnt directly support mW
        }

        # conversion factors for wavelength (to get commands capitalize)
        self.wavelength_conversions = {
            "nm": 1e-9,
            "µm": 1e-6,
            "mm": 1e-3,
            "m": 1e0,
            "pm": 1e-12,
        }

    def set_GUIparameter(self):
        """this is used to generate the switch UI"""

        gui_parameter = {
            "Power level": "0.0",  # default is 0 dBm = 1 mW
            "Power unit": list(self.allowed_power_units.keys()),
            "Wavelength": "1550.0",
            "Wavelength unit": list(self.wavelength_conversions.keys()),
            "SweepMode": ["None", "Wavelength", "Power"]
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):
        """get user options"""

        self.sweepmode: str = parameter["SweepMode"]
        self.port_string = parameter["Port"]  # auto used by port manager

        self.power_level = float(parameter["Power level"])
        self.wln = float(parameter["Wavelength"])
        self.power_unit = parameter["Power unit"]
        self.power_conversion = 1e-3 if self.power_unit == "mW" else 1
        self.wln_unit = parameter["Wavelength unit"]
        self.wln_conversion = self.wavelength_conversions[self.wln_unit]

        self.units = [self.wln_unit, self.power_unit]

    def initialize(self):
        """ perform initialisation steps needed only once per entire measurement"""

        self.reset()
        self.clear_status()
        id_ = self.get_identification()
        # print(f"N777x id: {id_}")

        self.set_power_units(self.power_unit)
        self.get_power_range()
        self.get_wavelength_range()

        is_key_ok = self.check_key_turned()
        if not is_key_ok:
            raise ValueError("LASER KEY IS IN OFF STATE")

    def deinitialize(self):
        """ called last time the instrument is used by sequencer (exit of last branch with inst)"""
        errors = self.check_errors()
        if errors:
            print("Errors for laser after measurement: ", errors)

    def configure(self):
        """configure for branch"""

        if self.sweepmode != "Power":
            self.set_power(power_level=self.power_level * self.power_conversion)
        elif self.sweepmode != "Wavelength":
            self.set_wavelength(wln=self.wln * self.wln_conversion)

    def poweron(self):
        # called if the measurement procedure enters a branch of the sequencer
        # and the module has not been used in the previous branch
        self.set_laser_on()

    def poweroff(self):
        """ called if branch is exited and module is not in next branch"""

        self.set_laser_off()

    def apply(self):
        """ 'apply' is used to set the new setvalue that is always available as 'self.value'
            and is only called if the setvalue has changed """

        value = float(self.value)

        if self.sweepmode == "Wavelength":
            self.set_wavelength(value * self.wln_conversion)
        elif self.sweepmode == "Power":
            self.set_power(power_level=value * self.power_conversion)

    def measure(self):

        self.wln_from_inst = self.get_wavelength()
        self.power_from_inst = self.get_power()

    def call(self):
        """
        mandatory function that must be used to return as many values as defined in self.variables
        This function can only be omitted if no variables are defined in self.variables.
        """
        return [
            self.wln_from_inst / self.wln_conversion, self.power_from_inst / self.power_conversion
        ]

    # wrapped communication commands below

    def get_identification(self):

        return self.query_port("*IDN?")

    def reset(self):
        self.port.write("*RST")

    def clear_status(self):
        self.port.write("*CLS")

    def get_power(self) -> float:
        """returns the power in W or dB"""

        result = self.query_port("sour0:pow?")
        return float(result)

    def get_power_range(self):
        """save the power range in mW as self.pow_min"""

        self.pow_min = float(self.query_port(":sour0:pow? min"))
        self.pow_max = float(self.query_port(":sour0:pow? max"))

    def set_power_units(self, unit="W"):
        if unit.lower() not in ["w", "dbm"]:
            raise ValueError("Valid power units are W and DBM")
        self.port.write(f":sour0:pow:unit {unit}")

    def get_power_units(self):
        self.query_port(":sour0:pow:unit?")

    def set_power(self, power_level: float) -> None:
        """set the power in self.power_unit s"""

        if not self.pow_max >= power_level >= self.pow_min:
            raise ValueError(f"Invalid power {power_level:.3f} not in range"
                             f" [{self.pow_min:.3f},{self.pow_max:.3f}] {self.power_unit}")

        self.port.write(f"sour0:pow {power_level}")
        self.power_level = power_level

    def set_wavelength(self, wln: float):
        """ set the laser wln in m"""
        wln = float(wln)
        if not self.wln_max >= wln >= self.wln_min:
            err_msg = f"Invalid wln {wln:.1f}m not in instrument range"
            err_msg += f"[{self.wln_min:.1f}m ,{self.wln_max:.1f}m]"
            raise ValueError(err_msg)

        self.port.write(f":sour0:wav {wln}")
        self.query_port("*OPC?")

        self.wln = wln

    def get_wavelength(self) -> float:
        """get the laser wln in meters"""
        result = self.query_port(":sour0:wav?")  # meters
        return float(result)

    def get_wavelength_range(self) -> None:
        """get the allowed laser wln range in meters"""

        self.wln_min = float(self.query_port(":sour0:wav? min"))
        self.wln_max = float(self.query_port(":sour0:wav? max"))

        return self.wln_min, self.wln_max

    def turn_key(self, onoff=0, password=1234):
        """ DANGER this changes the lock.
        Inputs: onoff: 1 for ON 0 for OFF"""
        self.port.write(f":LOCK {onoff},{password}")

    def check_key_turned(self):
        """check laser safety key turned"""
        result = self.query_port(":LOCK?")
        return bool(result)

    def set_laser_on(self):
        """switch laser on"""

        self.port.write("SOUR0:POW:STATE 1")

    def set_laser_off(self):
        """switch laser off"""

        self.port.write("SOUR0:POW:STATE 0")

    def is_laser_on(self):
        return int(self.query_port("SOUR0:POW:STATE?"))

    def check_errors(self) -> str:
        """ get error list if any and parse it based on manual"""

        err_count = int(self.query_port(":SYSTem:ERRor:COUNt?"))
        if err_count == 0:
            return

        errors = []
        for _ in range(err_count):
            err = self.query_port("SYST:ERR?")
            if not err.startswith("0"):
                errors.append(err)

        return ",".join(errors)

    # def close_shutter(self):

    #     self.set_shutter_state(open_=False)

    # def open_shutter(self, check_laser_on=True):

    #     self.set_shutter_state(open_=True)
    #     if check_laser_on:
    #         laser_on = self.get_laser_status()
    #         if not laser_on:
    #             raise Exception("Laser is not on")

    # def toggle_shutter(self):

    #     state = self.get_shutter_state()
    #     self.set_shutter_state(not state)

    def query_port(self, query="") -> str:
        """wrap the write+read as query command"""
        self.port.write(query)
        return self.port.read()
