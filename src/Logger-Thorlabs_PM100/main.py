# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Type: Logger
# Device: Template


import typing

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!

from pysweepme.ErrorMessage import debug


class Device(EmptyDevice):
    """ SweepMe! Logger Instrument driver for the PM100 Thorlabs USB power meter. """
    description = """
        <h3>Thorlabs PM100 power meter driver</h3>
        <p>&nbsp;</p>
        <p><strong>Models</strong></p>
        <p>PM100D, PM100A, PM100USB</p>
        <p>&nbsp;</p>
        <p><strong>Requirements</strong></p>
        <ul>
        <li>Installation of a VISA runtime to enable communication via USBTMC</li>
        <li>Power meter must be recognized as "USB Test and Measurement Device (IVI)" in Window device manager.</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Usage</strong></p>
        <ul>
        <li>So far, only power sensors are supported.</li>
        <li>Use the correct line frequency to get more accurate results.</li>
        <li>To change the correction wavelength, one can use the parameter syntax {...}</li>
        <li>In case you have thermo sensor, you can set acceleration on/off and choose a 
        time constant of your sensor.&nbsp;</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues</strong></p>
        <ul>
        <li>If the software Thorlabs Optical Power Monitor (OPM) is used, a hardware driver from Thorlabs is 
        typically installed that comes with a newer TLPM hardware driver. However, in order to use our SweepMe! 
        instrument driver you need to switch to the former hardware driver that supports communication via VISA 
        runtime and USBTMC. The installation of OPM comes with a tool called 'Driver Switcher' that you can use 
        to change the driver without using the Windows Device manager. Afterwards a yellow triangle in OPM indicates 
        the use of the VISA related driver.</li>
        <li>In case of thermo sensors and use of acceleration, the first reading can lead to a value larger than 1e37 
        that indicates an improper measurement. Therefore, this SweepMe! driver acquires the power multiple times to 
        get a good reading. Still it can happen, that a reading is not possible. In this case, the driver returns 
        float('nan') and throws a message at the Debug widget.</li>
        </ul>
        <p>&nbsp;</p>
    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Thorlabs PM100"  # short name will be shown in the sequencer

        self.port_manager = True
        self.port_types = ["USBTMC"]
        self.port_properties = {
            "timeout": 10,  # in seconds
            "clear": False,  # there are problems if the port of the PM100 is cleared
        }

        self._target_wavelength = None  # correction wavelength from user interface
        self._correction_wavelength = None  # correction wavelength from user interface
        self._meas_power = None

        self._inst_wavelength = None  # correction wavelength from instrument
        self._flags = None

        # could be useful in future to support also other sensors
        self.modes = {
            "Power in mW": "POW",
            "Power in W": "POW",            
            "Power in dBm": "POW",
        }

    def set_GUIparameter(self):

        gui_parameter = {
            "Mode": list(self.modes.keys()),
            "Correction wavelength in nm": "880",  # using string to make this field work with parameter syntax
            "Averages": 1,
            "Line frequency in Hz": [50, 60],
            "": None,  # empty line
            "Thermo sensor": None,  # section heading
            "Acceleration": False,
            "Time constant in s": 1.1,  # an arbitrary value that needs to be adapted by the user to the thermo sensor
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.mode_str = parameter["Mode"]
        self._target_wavelength = parameter["Correction wavelength in nm"]
        self._num_averages = parameter["Averages"]
        self.line_frequency = parameter["Line frequency in Hz"]
        self.port_string = parameter["Port"]  # auto used by port manager

        self.use_thermo_sensor_acceleration = parameter["Acceleration"]
        self.thermo_sensor_time_constant = parameter["Time constant in s"]

        # Creating variables and units
        variable, unit = self.mode_str.split(" in ")
        self.variables = [variable, "Correction wavelength"]
        self.units = [unit, "nm"]
        self.plottype = [True, True]
        self.savetype = [True, True]

    def initialize(self):

        # No reset at the beginning as done usually
        # A reset causes problems with thermo sensors during startup because thermo sensors need time
        # until proper values can be returned as they need to accumulate data.

        identifier = self.get_identification()
        # print("PM100 ID:", identifier)

        self.set_line_frequency(float(self.line_frequency))

        self.sensor_status = self.get_sensor_status()
        # print(self.sensor_status)

        # instrument could be made more generic by adapting to sensor (energy/power)
        if not (self.sensor_status["Flags"]["Is power sensor"] and self.sensor_status["Flags"]["Wavelength settable"]):
            raise AttributeError("PM100 sensor not compatible with instrument driver")

        self.get_correction_wavelength_range()
        
    def deinitialize(self):
        # used to switch back from remote to local
        self.port.port.control_ren(6)
    
    def configure(self):
        # called if the measurement procedure enters a branch of the sequencer
        # and the module has not been used in the previous branch

        self._target_wavelength = float(self._target_wavelength)  # conversion to µm
        self._num_averages = int(self._num_averages)

        if self._num_averages < 1:
            raise ValueError("Please use averages of 1 or higher.")
            self._num_averages = 1

        # Unit
        if "W" in self.units[0]:
            self.set_power_unit("W")
        else:
            self.set_power_unit("dBm")

        # Mode
        self.set_mode(self.modes[self.mode_str])
        # mode = self.get_mode()
        # print("Mode:", mode)

        # Autorange
        self.set_autorange(on=True)

        # Average
        self.set_average_count(self._num_averages)

        # Correction wavelength
        self.set_correction_wavelength(self._target_wavelength)
        self.verify_wavelength(self._target_wavelength)

        # Thermo sensor acceleration
        self.set_thermopile_acceleration(self.use_thermo_sensor_acceleration)

        # Thermo sensor time constant
        self.set_thermopile_time_constant(float(self.thermo_sensor_time_constant))

        # any beam diameter parameters etc here!

    def reconfigure(self, parameters, keys):
        """ 'reconfigure' is called whenever parameters of the GUI change by
         using the {...}-parameter system """

        if "Correction wavelength in nm" in keys:
            self._target_wavelength = float(parameters["Correction wavelength in nm"])
            self.set_correction_wavelength(self._target_wavelength)
            self.verify_wavelength(self._target_wavelength)

    def measure(self):

        # several retries to read a good value
        # in case of thermo sensors with acceleration the first values can be above 1E37
        for i in range(5):
            self._meas_power = self.read_power()
            if self._meas_power < 1e37:
                break

        if self._meas_power > 1e37:
            debug("PM100: Unable to read correct sensor value, received %1.2e." % self._meas_power)
            # Deactivate Thermo sensor acceleration to fix this error           
            # self.set_thermopile_acceleration(False)
            self._meas_power = float('nan')  # NaN is shown as missing data in Plot and data files

        if self.units[0] == "mW":
            self._meas_power *= 1000.0  # conversion from W to mW

    def call(self):
        """
        mandatory function that must be used to return as many values as defined in self.variables
        This function can only be omitted if no variables are defined in self.variables.
        """

        return [self._meas_power, self._correction_wavelength]

    def get_sensor_status(self):

        sensor_info = self.get_sensor_info()

        # manual: <name>, <sn>, <cal_msg>, <type>, <subtype>, <flags>
        name, serial_n, cal_info, sens_type, sub_type, flags = sensor_info.split(",")
        # sensor_info = f"Sensor: {name}, Serial number: {serial_n}, Calibration: {cal_info}, Type: {sens_type}"

        flags_dict = {}
        flags = int(flags)
        flags_dict["Is power sensor"] = flags & 1 != 0
        flags_dict["Is energy sensor"] = flags & 2 != 0
        # flags_dict["_1"] = flags & 4 != 0  # Undefined bit
        # flags_dict["_2"] = flags & 8 != 0  # Undefined bit
        flags_dict["Response settable"] = flags & 16 != 0
        flags_dict["Wavelength settable"] = flags & 32 != 0
        flags_dict["Tau settable"] = flags & 64 != 0
        # flags_dict["_3"] = flags & 128 != 0  # Undefined bit
        flags_dict["Has temperature sensor"] = flags & 256 != 0

        sensor_status = {
            "Name": name,
            "Serial number": serial_n,
            "Calibration": cal_info,
            "Sensor type": sens_type,
            "Sub type": sub_type,
            "Flags": flags_dict,
        }

        return sensor_status

    def verify_wavelength(self, target_wavelength):

        reached = round(target_wavelength, 1) == round(self.get_correction_wavelength(), 1)
        if not reached:
            err = f"Wavelength {target_wavelength} not reached properly set ({self.get_correction_wavelength()})"
            raise Warning(err)

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def get_scpi_standard(self):

        self.port.write("SYST:VERS?")
        return self.port.read()

    def reset(self):

        self.port.write("*RST")

    def get_sensor_info(self):

        self.port.write("SYST:SENS:IDN?")
        answer = self.port.read()
        return answer

    def set_line_frequency(self, frequency):

        frequency = int(float(frequency))

        if frequency not in [50, 60]:
            raise ValueError("Line frequency must be either 50 Hz or 60 Hz.")

        self.port.write("SYST:LFR %i" % int(frequency))

    def get_line_frequency(self):

        self.port.write("SYST:LFR?")
        answer = int(self.port.read())
        return answer

    def set_mode(self, mode):

        self.port.write("CONF:%s" % mode)

    def get_mode(self):

        self.port.write("CONF?")
        return self.port.read()

    def set_correction_wavelength(self, target_wavelength: float) -> None:
        """set the wavelength for power correction"""

        self.port.write(f"SENS:CORR:WAV {target_wavelength}")
        self._correction_wavelength = target_wavelength

    def get_correction_wavelength(self) -> float:
        """ get the current correction wavelength
            store it in memory and return it"""

        self.port.write("SENS:CORR:WAV?")
        wln = self.port.read()
        self._inst_wavelength = float(wln)
        return float(wln)

    def get_correction_wavelength_range(self) -> None:
        """ get the range for which correction exists"""
        self.port.write("SENS:CORR:WAV? MIN")
        min_wln = float(self.port.read())

        self.port.write("SENS:CORR:WAV? MAX")
        max_wln = float(self.port.read())
        self.correction_wavelength_range = [min_wln, max_wln]

    def set_power_unit(self, unit):

        unit = str(unit).upper()

        if unit not in ["W", "DBM"]:
            raise ValueError("Uni must be either 'W' or 'DBM'")

        self.port.write("SENSE:POWER:UNIT %s" % unit)

    def read_power(self, wavelength=None) -> float:
        """ read power value from instrument"""

        if wavelength:
            self.set_correction_wavelength(wavelength)

        self.port.write("MEAS:POW?")
        self._meas_power = float(self.port.read())

        return self._meas_power

    def set_average_count(self, num_avg: int):

        self.port.write(f"SENS:AVER:COUN {num_avg}")

    def get_average_count(self) -> int:

        self.port.write("SENS:AVER:COUN?")
        return int(self.port.read())

    def set_autorange(self, on: bool):
        """auto ranging mode for power"""
        self.port.write(f"SENS:POW:RANG:AUTO {int(on)}")

    def get_power_range(self) -> float:
        """get the power range"""
        self.port.write("SENS:POW:RANGe?")
        power_range = self.port.read()
        # print("Meas range was:", power_range)
        return float(power_range)

    def set_thermopile_acceleration(self, state):
        """
        set the state of the thermopile acceleration

        Args:
            state: str, bool -> "ON"|"1"|True or "OFF"|"0"|False
        """

        state = int(state)
        if state == "0" or state is False:
            state = "OFF"
        if state == "1" or state is True:
            state = "ON"

        self.port.write("INP:THER:ACC %s" % state)

    def set_thermopile_time_constant(self, time_constant):
        """
        set the time constant of the thermopile

        Args:
            time_constant: float, value in the range 0-63
        """

        self.port.write("INP:THER:TAU %1.1f" % time_constant)

    def set_sensor_adapter_type(self, adapter_type):
        """
        sets the custom sensor input adapter type
        Args:
            adapter_type: PHOTodiode| THERmal | PYRo

        Returns:

        """

        self.port.write("INP:ADAP:TYPE %s" % adapter_type)


if __name__ == "__main__":

    pm100 = Device()
