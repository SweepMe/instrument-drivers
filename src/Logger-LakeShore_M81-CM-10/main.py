# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: LakeShore M81 CM-10

from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    def __init__(self):
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP", "SOCKET"]

        self.port_properties = {
            "baudrate": 921600,
            "EOL": "\n",
            "timeout": 15,
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "SOCKET_EOLwrite": "\n",
            "SOCKET_EOLread": "\n",
        }
        # Possible measurement modes for Logger
        self.modes = {
            "DC": "DC",
            "AC": "RMS",
            # "Lock-In": "LIA", #  Lock-In mode can be accessed through Lock-In device driver for M81 CM-10
        }

        # Current range limits for the CM-10 in A
        self.range_limits = {
            "Auto": 0,  # 0 means auto-range
            "100 mA": 100e-3,
            "10 mA": 10e-3,
            "1 mA": 1e-3,
            "100 µA": 100e-6,
            "10 µA": 10e-6,
            "1 µA": 1e-6,
            "100 nA": 100e-9,
            "10 nA": 10e-9,
            "1 nA": 1e-9,
        }

        # Low pass corner frequency options for the CM-10 in Hz
        self.cornerf_options = {
            "None": "NONE",
            "10 Hz": "F10",
            "30 Hz": "F30",
            "100 Hz": "F100",
            "300 Hz": "F300",
            "1 kHz": "F1000",
            "3 kHz": "F3000",
            "10 kHz": "F10000",
        }

        # Filter optimization modes for the CM-10
        self.filter_types = {
            "Lowest noise": "NOISe",
            "Highest reserve": "REServe",
        }

        # Measurement Parameters
        self.slot: str = ""
        self.port_string: str = ""
        self.nplc: float = 0.1
        self.mode_set: str = ""
        self.mode_read: str = ""
        self.limit: float = 1e-9
        self.use_bias: bool = False
        self.bias_voltage: float = 0.0
        self.current: float = float('nan')
        self.filter_on: bool = False
        self.filter_type: str = "NOISe"
        self.low_filter_cornerf: str = "NONE"
        self.low_filter_rolloff: int = 6
        self.high_filter_cornerf: str = "NONE"
        self.high_filter_rolloff: int = 6
        self.darkmode: bool = False

    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "Channel": ["M1", "M2", "M3"],
            "Mode": list(self.modes.keys()),
            "Range limit": list(self.range_limits.keys()),
            "Averaging time (NPLC)": 0.1,
            "Enable bias voltage": False,
        }
        if parameters.get("Enable bias voltage"):
            gui_parameters["Bias voltage in V"] = 0.0

        gui_parameters["   "] = None  # Empty line 3
        gui_parameters["Analog input filter"] = False
        if parameters.get("Analog input filter"):
            gui_parameters["Filter optimization"] = list(self.filter_types.keys())
            gui_parameters["Low pass corner frequency"] = list(self.cornerf_options.keys())
            gui_parameters["Low pass rolloff"] = ["6 dB/oct", "12 dB/oct"]
            if self.mode_set == "AC":
                gui_parameters["High pass corner frequency"] = list(self.cornerf_options.keys())
                gui_parameters["High pass rolloff"] = ["6 dB/oct", "12 dB/oct"]
            gui_parameters["    "] = None  # Empty line 4
        gui_parameters["Turn off LED"] = False
        return gui_parameters

    def apply_gui_parameters(self, parameter):
        channel = parameter.get("Channel")
        if channel.strip().lower() in  ["m1", "m2", "m3"]:
            self.slot = channel[1]  # e.g. "1 for "M1"
        else:
            self.slot = ""  # default
        self.port_string = parameter.get("Port")
        self.mode_set = parameter.get("Mode")
        self.mode_read = self.modes.get(self.mode_set)
        self.limit = self.range_limits.get(parameter.get("Range limit"))
        self.nplc = parameter.get("Averaging time (NPLC)")
        self.filter_on = parameter.get("Analog input filter", False)
        self.darkmode = parameter.get("Turn off LED", False)
        if self.filter_on:
            self.filter_type = self.filter_types.get(parameter.get("Filter optimization"),"")
            self.low_filter_cornerf = self.cornerf_options.get(parameter.get("Low pass corner frequency"),"")
            self.low_filter_rolloff = int(parameter.get("Low pass rolloff", "0").split(" ")[0])
            if self.mode_set == "AC":
                self.high_filter_cornerf = self.cornerf_options.get(parameter.get("High pass corner frequency"),"")
                self.high_filter_rolloff = int(parameter.get("High pass rolloff", "0").split(" ")[0])

        self.use_bias = bool(parameter.get("Enable bias voltage"))
        if self.use_bias:
            self.bias_voltage = float(parameter.get("Bias voltage in V", -1.0))

        self.shortname = "CM-10 M@ " + self.slot

        self.variables = ["Current " + self.mode_read]
        self.units = ["A"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        if not self.slot:
            raise ValueError("Please give a correct channel number (M1, M2 or M3).")
        self.check_device()
        self.port.write(f'SENSe{self.slot}:PRESet')

    def deinitialize(self):
        pass

    """ the following functions are called if a new branch is entered
     and the module was not part of the previous branch """

    def configure(self):
        self.set_mode(self.mode_set)
        self.set_range(self.limit)
        self.set_nplc(self.nplc)
        self.set_advanced_settings()
        # Bias voltage must be set after filter settings or a warning will appear on the touch panel.
        self.set_bias(self.use_bias, self.bias_voltage)

    """ the following functions are called for each measurement point """

    def measure(self):
        self.port.write(f"READ:SENS{self.slot}:{self.mode_read}?")

    def read_result(self):
        res = self.port.read()  # returns one-dimensional current value
        self.current = float(res)

    def call(self):
        return self.current

    """ wrapped functions """

    def set_mode(self, mode):
        self.port.write(f'SENSe{self.slot}:MODE {mode}')

    def set_range(self, limit):
        if limit == 0:  # auto-range mode
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe:AUTO 1')
        else:
            if self.filter_on and self.filter_type == "REServe":
                if self.limit == 0.1:  # CM-10 does not allow this combination. It would quietly reduce the range.
                    raise ValueError("100 mA range cannot be used with filter optimization 'highest reserve'.")
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe:AUTO 0')
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe {limit}')


    def set_nplc(self, nplc):
        nplc = float(nplc)
        if not (600 >= nplc >= 0.01):
            raise ValueError("NPLC must be between 0.01 and 600.00.")
        self.port.write(f'SENSe{self.slot}:NPLCycles {nplc}')

    def set_bias(self, enabled, voltage):
        self.port.write(f'SENSe{self.slot}:BIAS:STATe {"1" if enabled else "0"}')
        if enabled:
            if abs(voltage) > 0:
                if self.filter_on and self.filter_type == "NOISe":
                    raise ValueError("Bias voltage > 0 cannot be used with 'Lowest noise' filter optimization.")
                self.port.write(f'SENSe{self.slot}:BIAS:VOLTage {voltage}')
            elif voltage == 0:
                self.port.write(f'SENSe{self.slot}:BIAS:VOLTage 0')
            else:
                raise ValueError("Bias voltage is enabled, but no value has been given. "
                                 "Set a value in Volts or disable bias voltage.")

    def check_device(self):
        model = self.port.query(f'SENSe{self.slot}:MODel?')
        if not "CM-10" in model:
            raise ValueError(
                f"Device connected on channel M{self.slot} does not match this driver. "
                f"Found: '{model}'"
            )

    def set_advanced_settings(self):
        if self.filter_on:
            self.set_filters()
        else:
            self.port.write(f'SENSe{self.slot}:FILTer:STATe 0')
        self.port.write(f'SENSe{self.slot}:DMODe {"1" if self.darkmode else "0"}')

    def set_filters(self):
        self.port.write(f'SENSe{self.slot}:FILTer:STATe 1')
        self.port.write(f'SENSe{self.slot}:FILTer:OPTimization {self.filter_type}')
        self.port.write(f'SENSe{self.slot}:FILTer:LPASs:FREQuency {self.low_filter_cornerf}')
        self.port.write(f'SENSe{self.slot}:FILTer:LPASs:ATTenuation R{self.low_filter_rolloff}')
        if self.mode_set == "AC":
            self.port.write(f'SENSe{self.slot}:FILTer:HPASs:FREQuency {self.high_filter_cornerf}')
            self.port.write(f'SENSe{self.slot}:FILTer:HPASs:ATTenuation R{self.high_filter_rolloff}')


