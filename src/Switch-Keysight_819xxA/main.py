# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH
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


# SweepMe! device class
# Type: Switch
# Device: Keysight 819xxA


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    description = """
    <p>Driver for a compact tunable laser source from Keysight for the 816xB family of main frames.<br /> <br />For other modules like power meters and attenuators, please have a look at the other drivers.<br /> <br /><strong>Usage:</strong></p>
    <ul>
    <li>If SweepMode is Wavelength or Power, the corresponding option of the Parameters section of this driver will be neglected.</li>
    <li>Select in which slot the laser is installed.</li>
    <li>Channel has to be used if an installed module has more than one functional unit per slot.</li>
    </ul>
                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keysight 819xxA"

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP"]
        self.port_properties = {
                                  "timeout": 5,
                                }

        # conversion dictionary between user selection and programming command units
        self.power_units = {
            "dBm": "DBM",  # default
            "W": "W",
            "mW": "W",  # There are only DBM and W as power units, so that mW must also set W as unit
            # "µW": "UW",
            # "mW": "MW",
            # "nW": "NW",
            # "pW": "PW",
        }

        # conversion dictionary between user selection and programming command units
        self.wavelength_units = {
            "nm": "NM",
            "µm": "UM",
            "mm": "MM",
            "m": "M",
            "pm": "PM",
        }

        # conversion dictionary between user selection of wavelength units and conversion factors to m
        self.wavelength_conversion = {
            "nm": 1e-9,
            "µm": 1e-6,
            "mm": 1e-3,
            "m": 1e0,
            "pm": 1e-12,
        }

    def set_GUIparameter(self):

        gui_parameter = {
                        "SweepMode": ["Wavelength", "Power", "None"],
                        "Slot": "1",
                        # "Channel": ["1"],
                        "Wavelength unit": list(self.wavelength_units.keys()),
                        "Wavelength": "1550",  # default unit nm
                        "Power unit": list(self.power_units.keys()),
                        "Power": "0.0",  # 0.0 dBm (default unit) = 1 mW
                        # "": None,  # empty line
                        # "List sweep": None,  # subsection
                        # "Wavelength start in nm": "1350",
                        # "Wavelength end in nm": "1500",
                        # "Wavelength step in nm": "10",
                        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.sweepmode = parameter["SweepMode"]

        self.source_slot = int(parameter["Slot"])
        # self.channel = int(parameter["Channel"])

        self.wavelength_unit = parameter["Wavelength unit"]
        self.wavelength_str = parameter["Wavelength"]
        self.power_unit = parameter["Power unit"]
        self.power_str = parameter["Power"]

        self.variables = ["Wavelength", "Power"]
        self.units = [self.wavelength_unit, self.power_unit]
        self.plottype = [True, True]
        self.savetype = [True, True]

    """ here, semantic standard functions start """

    def initialize(self):

        # identification = self.get_identification()
        # print("Identification:", identification)

        # TODO: reset and clear status only needs to be done once for the main frame
        self.reset()
        self.clear_status()

    def deinitialize(self):
        pass

    def poweron(self):
        self.switch_laser_on()

    def poweroff(self):
        self.switch_laser_off()

    def configure(self):

        self.set_power_unit(self.power_units[self.power_unit])

        power_unit = self.get_power_unit()
        # print("Power unit of 819xxA laser:", power_unit)

        self.wl_min = self.get_wavelength_min()
        self.wl_max = self.get_wavelength_max()
        # print("Wavelength range 819xxA:", self.wl_min, self.wl_max)
        
        self.power_min = self.get_power_min()
        self.power_max = self.get_power_max()
        # print("Power range 819xxA:", self.power_min, self.power_max)

        self.wavelength_value = float(self.wavelength_str)
        self.power_value = float(self.power_str)

        if self.power_unit == "mW":
            self.power_value = self.power_value / 1000.0  # conversion from mW to W

        if not self.sweepmode.startswith("Power"):
            self.set_power(self.power_value)

        if not self.sweepmode.startswith("Wavelength"):
            self.set_wavelength(self.wavelength_value, self.wavelength_units[self.wavelength_unit])

        error_message = self.get_error_message()
        if not "No error" in error_message:
            debug(error_message)

    def unconfigure(self):
    
        error_message = self.get_error_message()
        if not "No error" in error_message:
            debug(error_message)

    def apply(self):

        if self.sweepmode.startswith("Wavelength"):
            self.set_wavelength(self.value, self.wavelength_units[self.wavelength_unit])

        elif self.sweepmode.startswith("Power"):
            if self.self.power_unit == "mW":
                self.value = self.value / 1000.0  # conversion from mW to W
            self.set_power(self.value)

        error_message = self.get_error_message()
        if not "No error" in error_message:
            debug(error_message)

    def reach(self):
        # Let's make sure the wavelength is set before we continue
        self.port.write("*OPC?")  # is operation completed query
        self.port.read()

    def measure(self):

        self.wl_meas = self.get_wavelength(self.wavelength_unit)
        self.power_meas = self.get_power()

        # In case of "mW", the power is measured in W and we have to convert it here
        if self.power_unit == "mW":
            self.power_meas = self.power_meas * 1000.0  # changing from W to mW

        #print("Error message after measure:", self.get_error_message())

    def call(self):
        return [self.wl_meas, self.power_meas]

    """ here, python functions start that wrap the communication commands """

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        self.port.write("*RST")

    def clear_status(self):
        self.port.write("*CLS")

    def get_wavelength_min(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:WAV? MIN" % int(slot))
        return float(self.port.read())

    def get_wavelength_max(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:WAV? MAX" % int(slot))
        return float(self.port.read())

    def get_wavelength(self, unit=None, slot=None):

        if slot is None:
            slot = self.source_slot

        if unit is None:
            unit = self.wavelength_unit

        self.port.write("SOUR%i:CHAN1:WAV?" % int(slot))
        value = float(self.port.read())/self.wavelength_conversion[unit]
        return value

    def set_wavelength(self, wavelength, unit, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:WAV %1.3f%s" % (int(slot), float(wavelength), str(unit).upper()))

    def get_power_unit(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW:UNIT?" % (int(slot)))
        answer = self.port.read()
        return answer

    def set_power_unit(self, unit, slot=None):

        """
        Arguments:
            unit: "DBM" or 0
                  "W" or 1
            slot: Integer of the slot index starting from 1
        """

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW:UNIT %s" % (int(slot), str(unit).upper()))

    def get_power(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW?" % int(slot))
        return float(self.port.read())

    def set_power(self, power, slot=None):

        if slot is None:
            slot = self.source_slot

        power = float(power)

        if power < self.power_min:
            power = self.power_min
            debug("Keysight 819xxA -> Power (%1.3f) must be greater than minimum power (%1.3f)." % (power, self.power_min))
        elif power > self.power_max:
            power = self.power_max
            debug("Keysight 819xxA -> Power (%1.3f) must be smaller than power max (%1.3f)." % (power, self.power_max))

        self.port.write("SOUR%i:CHAN1:POW %1.3f" % (int(slot), power))

    def get_power_default(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW? DEF" % int(slot))
        return float(self.port.read())

    def get_power_min(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW? MIN" % int(slot))
        return float(self.port.read())

    def get_power_max(self, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW? MAX" % int(slot))
        return float(self.port.read())

    def switch_laser(self, state, slot=None):

        if slot is None:
            slot = self.source_slot

        self.port.write("SOUR%i:CHAN1:POW:STATE %i" % (int(slot), int(state)))

    def switch_laser_on(self, slot=None):

        self.switch_laser(1, slot)

    def switch_laser_off(self, slot=None):

        self.switch_laser(0, slot)

    def get_error_message(self):

        self.port.write("SYST:ERR?")
        return self.port.read()
