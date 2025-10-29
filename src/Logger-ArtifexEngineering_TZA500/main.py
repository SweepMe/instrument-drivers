# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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

# Contribution: The initial version of this driver was created by Christian Neumann / Artifex Engineering


# SweepMe! driver
# * Module: Logger
# * Instrument: Artifex Engineering TZA500

from pysweepme import EmptyDevice

import ftd2xx
import math
import sys
from time import sleep


class Device(EmptyDevice):
    def __init__(self):
        super().__init__()

        self.shortname = "TZA500"
        self.variables = []
        self.units = []
        self.port_manager = False

        self.port: str = ""
        self.port_serial: str = ""
        self.driver_name: str = "TZA500"
        self.instance_key: str = ""
        self.device = None

        self.gain_steps: dict = {
            "x1": "V1",
            "x10": "V2",
            "x100": "V3",
            "x1000": "V4",
            "x10000": "V5",
            "x100000": "V6",
            "Auto": "auto-gain"
        }
        self.gain_step_commands = {v: k for k, v in self.gain_steps.items() if v != "auto-gain"}

        self.bandwith_steps: dict = {
            "10 kHz": "B1",
            "1 kHz": "B2",
            "100 Hz": "B3",
            "10 Hz": "B4"
        }
        self.bandwith_step_commands = {v: k for k, v in self.bandwith_steps.items()}

        self._units: list = [
            "Nanoampere (nA)",
            "Microampere (µA)",
            "Milliampere (mA)",
            "Ampere (A)",
            "Nanowatts (nW)",
            "Microwatts (µW)",
            "Milliwatts (mW)",
            "Watts (W)"
        ]
        self._initial_auto_zero = [
            "None",
            "Auto zero",
            "Auto zero reset"
        ]
        self.sensitivity: float = 1.0
        self.autogain_gain: int = None
        self.gain: str = self.gain_steps["x1"]
        self.max_gain: int = 6

        self.bandwith: str = ""
        self.initial_auto_zero: str = ""
        self.invert_input_polarity: bool = False

        self.tza_comm_max_retries: int = 800

        self.tza_fw: str = ""
        self.tza_serial: str = ""
        self.tza_date_of_manufacturing: str = ""

        self.tza_detector_serial: str = ""
    
    @staticmethod
    def find_ports() -> list[str]:
        """ Return list of serial numbers """
        tza500_found = []

        if sys.platform != "win32":
            ftd2xx.setVIDPID(0x0403, 0x9a69) # for linux and macOS

        numDevs = ftd2xx.createDeviceInfoList()

        for i in range(0, numDevs):
            dev = ftd2xx.getDeviceInfoDetail(i)
            if "TZA500" in dev["description"].decode(errors="ignore"):
                tza500_found.append("{} - {}".format(dev["description"].decode(errors="ignore"), dev["serial"].decode(errors="ignore")))

        return tza500_found
    
    def update_gui_parameters(self, parameters: dict) -> dict:
        unit: str = parameters.get("Unit", "" if len(self.units) <= 0 else self.units[0])
        gui_parameters = {
            "Unit": self._units,
            "Gain": list(self.gain_steps.keys()),
            "Bandwith": list(self.bandwith_steps.keys()),
            "Initial (auto zero)": self._initial_auto_zero,
            "Invert input polarity": self.invert_input_polarity,
        }
        if unit in ["Nanowatts (nW)", "Microwatts (µW)", "Milliwatts (mW)", "Watts (W)"]:
            gui_parameters["Sensitivity"] = self.sensitivity

        return gui_parameters
    
    def apply_gui_parameters(self, parameters: dict) -> None:
        self.port = parameters["Port"]
        
        self.variables = ["Power"]
        self.units = [parameters["Unit"][parameters["Unit"].find('(')+1:parameters["Unit"].find(')')]]  # get only unit between brackets
        self.gain = self.gain_steps[parameters["Gain"]]
        self.bandwith = self.bandwith_steps[parameters["Bandwith"]]
        self.initial_auto_zero = parameters["Initial (auto zero)"]
        self.invert_input_polarity = bool(parameters["Invert input polarity"])
        if "Sensitivity" in parameters.keys():
            self.sensitivity = float(parameters["Sensitivity"])
    
    def connect(self) -> None:
        """ Connect to TZA500 """
        if self.port == "":
            raise Exception("No port selected.")
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
                self.device.setDataCharacteristics(8, 0, 0)  # 8 data bits, 1 stop bit, no parity
                self.device.setFlowControl(0, 0, 0)  # no flow control
                self.device.setTimeouts(1000, 0)
                self.device.setChars(126, 1, 0, 0)
                self.device.resetDevice()
                self.device.purge()
            except ftd2xx.DeviceError as e:
                msg = f"Cannot open FTD Device with serial number {port_byte}. Available devices: {ftd2xx.listDevices()}"
                raise Exception(msg) from e
            
            self.device_communication[self.instance_key] = self.device

            self._tza_send("$U")
            if self._tza_recv() != "U OK":
                self.disconnect()
                raise Exception("Error while cinnection to TZA500!")

    def disconnect(self) -> None:
        if self.instance_key not in self.device_communication:
            self.device = None
            return

        if self.device is not None:
            self.device.close()
            self.device = None

        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)
    
    def initialize(self) -> None:
        info = self.tza_get_info()
        info = info.splitlines()

        self.tza_fw = "" if info[0].find("FW") == -1 else info[0][info[0].find("FW")+2:]  # get TZA500 Firmware version

        self.tza_serial = info[1][8:]  # get TZA500 serial number
        self.tza_date_of_manufacturing = info[2][23:]  # get TZA500 date of Manufacturing

    def configure(self) -> None:
        self.tza_set_auto_zero_reset()
        self.autogain_gain = int(self.gain_steps[self.tza_get_gain()][1:])  # set current gain value for autogain
        
        if not self.tza_set_polarity(self.invert_input_polarity):
            raise Exception("Error while setting polarity.")

        if not self.gain == "auto-gain":  # set gain if auto-gain is not chosen
            if not self.tza_set_gain(self.gain):
                raise Exception("Error while setting Gain!")
        
        if not self.tza_set_bandwith(self.bandwith):
            raise Exception("Error while setting bandwith.")
        
        if self.initial_auto_zero == "Auto zero":
            if not self.tza_set_auto_zero():
                raise Exception("Error while setting auto zero.")
        elif self.initial_auto_zero == "Auto zero reset":
            if not self.tza_set_auto_zero_reset():
                raise Exception("Error while setting auto zero reset.")

    def measure(self) -> None:
        self.result = self.tza_get_measurement()

    def call(self) -> list:
        return [self.result]

    def tza_autogain(self, tmp_amplitude: str, recursion: int, last_operation = None) -> str:
        """
        This function automatically adjusts the gain by checking whether the
        measured value is too high or too low and then setting a new gain until
        the measured value is within a valid range.
        """
        if recursion >= 6:
            return tmp_amplitude
        
        if self.autogain_gain is None:
            self.autogain_gain = int(self.gain_steps[self.tza_get_gain()][1:])  # get gain as int if not already set

        amplitude = tmp_amplitude[:-2].replace(",", ".")
        amplitude = float(amplitude)

        level = 0.0

        # To calculate if the gain needs to be moved up or down:
        # The maximum output value in percent of each gain level is represented by the numbers (122.85, 12.285, ...)
        #
        # 1. Convert the measure amplitude into percent:
        #    if gain 1: amplitude / 122.85
        #    if gain 2: amplitude / 12.285
        #    if gain 3: amplitude / 1.2285
        #    if gain 4: amplitude / 122.85
        #    if gain 5: amplitude / 12.285
        #    if gain 6: amplitude / 1.2285
        # 2. If the value in percent is above 90 and the set gain level is greater than 1, set the new gain to gain - 1.
        #    If the value in percent is below 8 and the set gain level is lower than 5, set new gain to gain + 1

        if self.autogain_gain == 1:
            level = amplitude / 122.85
        elif self.autogain_gain == 2:
            level = amplitude / 12.285
        elif self.autogain_gain == 3:
            level = amplitude / 1.2285
        elif self.autogain_gain == 4:
            level = amplitude / 122.85 # This is not a typo
        elif self.autogain_gain == 5:
            level = amplitude / 12.285 # This is not a typo
        elif self.autogain_gain == 6:
            level = amplitude / 1.2285 # This is not a typo

        if level > 90.0 and self.autogain_gain > 1:
            self.autogain_gain -= 1
            self.tza_set_gain("V{}".format(self.autogain_gain))  # set new gain
            return self.tza_autogain(self.tza_get_single_measure(), recursion + 1, 1)  # return new measurement or re-adjust gain
        elif level < 8.0 and self.autogain_gain < self.max_gain:
            if last_operation == 1:
                recursion = 6
            self.autogain_gain += 1
            self.tza_set_gain("V{}".format(self.autogain_gain))  # set new gain
            return self.tza_autogain(self.tza_get_single_measure(), recursion + 1, 2)  # return new measurement or re-adjust gain
        else:
            return tmp_amplitude

    def _tza_send(self, msg: str):
        if self.device is None:
            raise Exception("send error: port not open.")
        
        self.device.write(msg.encode())
    
    def _tza_recv(self) -> str:
        if self.device is None:
            raise Exception("recive error: port not open.")
        msg = b""
        i = 0
        while i < self.tza_comm_max_retries:
            if self.device.getQueueStatus() > 0:  # check if bytes in buffer
                msg = self.device.read(self.device.getQueueStatus())  # read entire buffer
                while not msg.endswith(b'\r'):  # append buffer until '\r' is found
                    msg = msg + self.device.read(self.device.getQueueStatus())
                
                return msg.decode(errors="ignore").replace("\r", '').strip()
            sleep(0.01)
            i += 1
        raise TimeoutError("No Valid Data received.")
    
    def tza_get_info(self) -> str:
        self._tza_send("$I")
        return self._tza_recv()

    def tza_get_gain(self) -> str:
        self._tza_send("V?")
        gain = self._tza_recv()

        if gain in self.gain_step_commands.keys():
            return self.gain_step_commands[gain]
        return ""
    
    def tza_set_gain(self, gain: str) -> bool:
        gain = str(gain)
        if gain not in self.gain_step_commands.keys():
            raise Exception("Invalid gain. choose one from the pre-defined gains.")
        self._tza_send(gain)
        recv = self._tza_recv()
        if self.initial_auto_zero == "Auto zero":
            sleep(0.2)
        if recv != gain + " OK":
            return False
        return True
    
    def tza_get_bandwith(self) -> str:
        self._tza_send("B?")
        bandwith = self._tza_recv()

        if bandwith in self.bandwith_step_commands.keys():
            return self.bandwith_step_commands[bandwith]
        return ""

    def tza_set_bandwith(self, bandwith: str) -> bool:
        bandwith = str(bandwith)
        if bandwith not in self.bandwith_step_commands.keys():
            raise Exception("Invalid bandwith. choose one from the pre-defined bandwiths.")
        self._tza_send(bandwith)
        recv = self._tza_recv()
        if recv != bandwith + " OK":
            return False
        return True

    def tza_polarity_is_inverted(self) -> bool:
        self._tza_send("$F")
        recv = self._tza_recv()
        
        if recv == "F0":
            return False
        elif recv == "F1":
            return True
        else:
            raise Exception("Input polarity could not be set.")
        
    def tza_set_polarity(self, inverted: bool) -> bool:
        inverted = bool(inverted)
        polarity_command = "N" if inverted == False else "C"

        self._tza_send("${}".format(polarity_command))
        
        recv = self._tza_recv()
        if recv != polarity_command + " OK":
            return False
        return True

    def tza_set_auto_zero(self) -> bool:
        self._tza_send("$A")
        
        recv = self._tza_recv()
        if recv.count("Gain: ") > 0:
            self.max_gain = int(recv[-1])
            sleep(0.2)
            return True
        elif recv.count("A OK") > 0:
            self.max_gain = 6
            sleep(0.5)
            return True
        return False

    def tza_set_auto_zero_reset(self) -> bool:
        self._tza_send("$R")
        
        recv = self._tza_recv()
        if recv != "R OK":
            return False
        self.max_gain = 6
        sleep(0.05)
        return True

    def tza_get_single_measure(self) -> str:
        """ Return an measurement result in the format: I1,0nA or I1,0uA"""
        self._tza_send("$E")
        return self._tza_recv()[1:].strip()  # remove 'I' prefix from response

    def tza_get_measurement(self) -> float:
        amplitude = self.tza_get_single_measure()
        if self.gain == "auto-gain":  # adjust gain if auto-gain is chosen
            amplitude = self.tza_autogain(amplitude, 0)
        unit = amplitude[amplitude.find("A")-1:]  # get unit from last two bytes of the response

        amplitude = amplitude[:-2].replace(",", ".")
        amplitude = float(amplitude)

        if unit == "uA":
            amplitude *= 1000  # convert µA to nA

        sensitivity = 1.0
        if self.units[0] not in ["nA", "µA", "mA", "A"]:
            sensitivity = self.sensitivity
        
        amplitude = amplitude / sensitivity
        
        if self.units[0].startswith("n"):
            amplitude = round(amplitude, 3)
        elif self.units[0].startswith("µ"):
            amplitude /= 1000 # nano to micro
            amplitude = round(amplitude, 6)
        elif self.units[0].startswith("m"):
            amplitude /= 1000000 # nano to milli
            amplitude = round(amplitude, 9)
        else:
            amplitude /= 1000000000 # for A and W
            amplitude = round(amplitude, 12)

        return amplitude