# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 Artifex Engineering GmbH & Co KG.
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

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! device class
# Device: Artifex Engineering OPM150

from pysweepme import EmptyDevice

import ftd2xx
import math
import sys
from time import sleep

class Device(EmptyDevice):
    def __init__(self):
        super().__init__()

        self.shortname = "OPM150"
        self.variables = []
        self.units = []
        self.port_manager = False


        self.port: str = ""
        self.port_serial: str = ""
        self.driver_name: str = "OPM150"
        self.instance_key: str = ""
        self.device = None

        self.gain_steps: dict = {"x1": "V1", "x10": "V2", "x100": "V3", "x1000": "V4", "x10000": "V5", "auto-gain": "auto-gain"}
        self.gain_step_commands = {"V1": "x1", "V2": "x10", "V3": "x100", "V4": "x1000", "V5": "x10000"}
        self._units: list = ["Nanoampere (nA)", "Microampere (µA)", "Milliampere (mA)", "Ampere (A)", "Nanowatts (nW)", "Microwatts (µW)", "Milliwatts (mW)", "Watts (W)", "Watts per square centimeter (nW/cm²)", "Watts per square centimeter (µW/cm²)", "Watts per square centimeter (mW/cm²)", "Watts per square centimeter (W/cm²)", "Decibel-milliwatt (dBm)"]
        self.sensitivity: float = 1.0
        self.wavelength:str = "660"
        self.autogain_gain: int = None
        self.gain: str = self.gain_steps["x1"]
        self.filter: float = 1.0
        self.aperture: float = 7.0

        self.opm_comm_max_retries: int = 800

        self.opm_fw:str = None
        self.opm_serial: str = None
        self.opm_date_of_manufacturing: str = None
        self.opm_is_100khz: bool = False

        self.opm_detector_serial: str = None
        self.opm_detector_min_wavelength: str = None
        self.opm_detector_max_wavelength: str = None
        self.opm_detector_integrating_sphere: bool = False
    
    @staticmethod
    def find_ports() -> list[str]:
        """ Return list of serial numbers """
        opm150_found = []

        if sys.platform != "win32":
            ftd2xx.setVIDPID(0x0403, 0x9a69) # for linux and macOS

        numDevs = ftd2xx.createDeviceInfoList()

        for i in range(0, numDevs):
            dev = ftd2xx.getDeviceInfoDetail(i)
            if "OPM150" in dev["description"].decode(errors="ignore"):
                opm150_found.append("{} - {}".format(dev["description"].decode(errors="ignore"), dev["serial"].decode(errors="ignore")))

        return opm150_found
    
    def update_gui_parameters(self, parameters: dict) -> dict:
        unit: str = parameters.get("Unit", "" if len(self.units) <= 0 else self.units[0])
        gui_parameters = {
            "Unit": self._units,
            "Wavelength": self.wavelength,
            "Gain": list(self.gain_steps.keys()),
            "Filter": self.filter
        }
        if unit in ["Watts per square centimeter (nW/cm²)", "Watts per square centimeter (µW/cm²)", "Watts per square centimeter (mW/cm²)", "Watts per square centimeter (W/cm²)"]:
            gui_parameters["Aperture"] = self.aperture

        return gui_parameters
    
    def apply_gui_parameters(self, parameters: dict) -> None:
        self.port = parameters["Port"]
        
        self.variables = ["Power"]
        self.units = [parameters["Unit"][parameters["Unit"].find('(')+1:parameters["Unit"].find(')')]] # get only unit between brackets
        self.wavelength = parameters["Wavelength"]
        self.gain = self.gain_steps[parameters["Gain"]]
        self.filter = float(parameters["Filter"])
        if "Aperture" in parameters.keys():
            self.aperture = float(parameters["Aperture"])
    
    def connect(self) -> None:
        """ Connect to OPM150 """
        # Set serial number of port as key
        self.port_serial = self.port.split("- ")[1]
        self.instance_key = f"{self.driver_name}_{self.port_serial}"

        # If the device is already instantiated by another driver, use the existing instance
        if self.instance_key in self.device_communication:
            self.device = self.device_communication[self.instance_key]
        else:
            # Open device
            port_byte = self.port_serial.encode()
            try:
                self.device = ftd2xx.openEx(port_byte)
                self.device.setBaudRate(115200)
                self.device.setDataCharacteristics(8, 0, 0) # 8 data bits, 1 stop bit, no parity
                self.device.setFlowControl(0, 0, 0) # no flow control
                self.device.setTimeouts(1000, 0)
                self.device.setChars(126, 1, 0, 0)
                self.device.resetDevice()
                self.device.purge()
            except ftd2xx.ftd2xx.DeviceError as e:
                msg = f"Cannot open FTD Device with serial number {port_byte}. Available devices: {ftd2xx.listDevices()}"
                raise Exception(msg) from e

            self.device_communication[self.instance_key] = self.device
    
    def initialize(self) -> None:
        info = self.opm_get_info()
        info = info.splitlines()

        info_detector_min_wavelength_offset = info[3].find("nm") # detector min wavelength end position
        info_detector_max_wavelength_offset_1 = info[3].find("-")+2 # detector max wavelength start position
        info_detector_max_wavelength_offset_2 = info[3].find("nm", info_detector_min_wavelength_offset+2) # detector max wavelength end position

        self.opm_fw = info[0][info[0].find("FW")+2:] # get OPM150 Firmware version
        if info[0].count("100kHz") > 0: # check if "100kHz" in Identifier String
            self.opm_is_100khz = True
        self.opm_serial = info[1][8:] # get OPM150 serial number
        self.opm_date_of_manufacturing = info[2][23:] # get OPM150 date of Manufacturing

        self.opm_detector_serial = info[3][10:16] # get detector serial number
        self.opm_detector_min_wavelength = info[3][17:info_detector_min_wavelength_offset] # get detector min wavelength
        self.opm_detector_max_wavelength = info[3][info_detector_max_wavelength_offset_1:info_detector_max_wavelength_offset_2] # get detector max wavelength

        if self.opm_detector_serial[:1] in ["U", "V", "W", "X"]: # check if detector is integrating sphere and adjust paramters
            self.opm_detector_integrating_sphere = True
            opm_detector_power_multiplier = 10**-int(self.opm_detector_serial[1:2])
            self.sensitivity = self.sensitivity * opm_detector_power_multiplier
        
        self.autogain_gain = int(self.gain_steps[self.opm_get_gain()][1:]) # set current gain value for autogain
    
    def configure(self) -> None:
        self.opm_set_wavelength(self.wavelength) # set chosen wavelength

        if not self.gain == "auto-gain": # set gain if auto-gain is not chosen
            if not self.opm_set_gain(self.gain):
                raise Exception("Error while setting Gain!")
    
    def reconfigure(self, parameters = {}, keys = []):
        self.update_gui_parameters(parameters)
        self.initialize()
    
    def opm_autogain(self, tmp_amplitude: str) -> str:
        """
        This function automatically adjusts the gain by checking whether the
        measured value is too high or too low and then setting a new gain until
        the measured value is within a valid range.
        """
        if self.autogain_gain is None:
            self.autogain_gain = int(self.gain_steps[self.opm_get_gain()][1:]) # get gain as int if not already set

        amplitude = tmp_amplitude[:-2].replace(",", ".")
        amplitude = float(amplitude)

        level = 0.0

        if self.autogain_gain == 1:
            level = amplitude / 122.85
        elif self.autogain_gain == 2:
            level = amplitude / 12.285
        elif self.autogain_gain == 3:
            level = amplitude / 1.2285
        elif self.autogain_gain == 4:
            level = amplitude / 122.85
        elif self.autogain_gain == 5:
            level = amplitude / 12.285
        
        if self.opm_is_100khz:
            level *= 3
        
        if level > 90.0 and self.autogain_gain > 1:
            self.autogain_gain -= 1
            self.opm_set_gain("V{}".format(self.autogain_gain)) # set new gain
            return self.opm_autogain(self.opm_get_single_measure()) # return new measurement or re-adjust gain
        elif level < 8.0 and self.autogain_gain < 5:
            self.autogain_gain += 1
            self.opm_set_gain("V{}".format(self.autogain_gain)) # set new gain
            return self.opm_autogain(self.opm_get_single_measure()) # return new measurement or re-adjust gain
        else:
            return tmp_amplitude
            
    def call(self) -> list:
        return [self.opm_get_measuement()]
    
    def disconnect(self) -> None:
        if self.instance_key not in self.device_communication:
            self.device = None
            return
        
        if self.device is not None:
            self.device.close()
            self.device = None

        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)
    
    def _opm_send(self, msg: str):
        if self.device is None:
            raise Exception("send error: port not open.")
        
        self.device.write(msg.encode())
    
    def _opm_recv(self) -> str:
        if self.device is None:
            raise Exception("recive error: port not open.")
        msg = b""
        i = 0
        while i < self.opm_comm_max_retries:
            if self.device.getQueueStatus() > 0:# check if bytes in buffer
                msg = self.device.read(self.device.getQueueStatus()) # read entire buffer
                while not msg.endswith(b'\r'): # append buffer until '\r' is found
                    msg = msg + self.device.read(self.device.getQueueStatus())

                if "DET ERR" in msg.decode(errors="ignore"):
                    raise Exception("No detector connected")
                elif "PWR ERR" in msg.decode(errors="ignore"):
                    raise Exception("OPM doesn't get enough power")
                
                return msg.decode(errors="ignore").replace("\r", '').strip()
            sleep(0.01)
            i += 1
        raise TimeoutError("No Valid Data received")
    
    def opm_get_info(self) -> str:
        self._opm_send("$I")
        return self._opm_recv()

    def opm_get_gain(self) -> str:
        self._opm_send("V?")
        received = self._opm_recv()
        
        gain = received.splitlines()
        if gain[0] == "V? OK" and gain[1] in self.gain_step_commands.keys():
            return self.gain_step_commands[gain[1]]
        return ""
    
    def opm_set_gain(self, gain: str) -> bool:
        gain = str(gain)
        if gain not in self.gain_step_commands.keys():
            raise Exception("Invalid gain. choose one from the pre-defined gains.")
        self._opm_send(gain)
        recv = self._opm_recv()
        if recv != gain + " OK":
            return False
        return True
    
    def opm_set_wavelength(self, wavelength: str) -> None:
        self.wavelength = wavelength

        if len(wavelength) == 3:
            wavelength = "0" + wavelength # append 0 at beginning of wavelength if wavelength is not 4 bytes long
        self._opm_send("L")
        for i in wavelength:
            self._opm_send(i)
        self.sensitivity = float(self._opm_recv().replace(",", ".")[4:]) # retrive correction factor from OPM150

    def opm_get_single_measure(self) -> str:
        """ Return an measurement result in the format: I1,0nA or I1,0uA"""
        self._opm_send("$E")
        return self._opm_recv()[1:] # remove 'I' prefix from response

    def opm_get_measuement(self) -> float:
        amplitude = self.opm_get_single_measure()
        if self.gain == "auto-gain": # adjust gain if auto-gain is chosen
            amplitude = self.opm_autogain(amplitude)
        unit = amplitude[amplitude.find("A")-1:] # get unit from last two bytes of the response

        amplitude = amplitude[:-2].replace(",", ".")
        amplitude = float(amplitude)

        if unit == "uA":
            amplitude *= 1000 # convert µA to nA

        sensitivity = 1.0
        if self.units[0] not in ["nA", "µA", "mA", "A"]:
            sensitivity = self.sensitivity
        
        amplitude = amplitude / (sensitivity * self.filter)
        
        if self.units[0].startswith("n"):
            pass # amplitude already nano, no need to convert
        elif self.units[0].startswith("µ"):
            amplitude /= 1000 # nano to micro
        elif self.units[0].startswith("m"):
            amplitude /= 1000000 # nano to milli
        elif self.units[0] == "dBm":
            amplitude = 10 * math.log10(amplitude / 1000000)
        else:
            amplitude /= 1000000000 # for A and W
            
        if self.units[0] in ["nW/cm²", "µW/cm²", "mW/cm²", "W/cm²"]:
            amplitude = amplitude / (((self.aperture**2) / 400) * math.pi)

        amplitude = round(amplitude, 5)

        return amplitude