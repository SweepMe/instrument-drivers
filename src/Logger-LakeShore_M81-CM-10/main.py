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

        # Possible measurement modes
        self.modes = {
            "DC": "DC",
            "AC": "RMS",
            "Lock-In": "LIA",
        }

        # Current range limits for the CM-10 in A
        self.range_limits = {
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
        self.slot: str = "M0"
        self.port_string: str = ""
        self.nplc: float = 0.1
        self.mode_set: str = ""
        self.mode_read: str = ""
        self.range_mode: str = ""
        self.limit: float = 1e-9
        self.use_bias: bool = False
        self.bias_voltage: float = 0.0
        self.current: float = float('nan')
        self.lia_result: tuple = (float('nan'), float('nan'), float('nan'), float('nan'))
        self.lia_ref: str = "S0"
        self.lia_lowpass: bool = False
        self.lia_harm: int = 1
        self.lia_tc: float = 0.1
        self.lia_rolloff: int = 6
        self.lia_avg_filters: bool = False
        self.lia_avg_ref_cycles: int = 0
        self.lia_auto_phase: bool = True
        self.lia_ref_phase_shift: float = 0.0
        self.advanced: bool = False
        self.filter_on: bool = False
        self.filter_type: str = "NOISe"
        self.low_filter_cornerf: str = "NONE"
        self.low_filter_rolloff: int = 6
        self.high_filter_cornerf: str = "NONE"
        self.high_filter_rolloff: int = 6
        self.high_digital_filter: bool = True
        self.freq_range_threshold: float = 0.1
        self.darkmode: bool = False

    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "Channel": ["M1", "M2", "M3"],
            "Mode": list(self.modes.keys()),
        }
        mode = parameters.get("Mode")
        if mode == "Lock-In":
            gui_parameters["Lock-In reference source"] = ["S1", "S2", "S3"]
            gui_parameters["Lock-In averaging filter"] = False
            if parameters.get("Lock-In averaging filter"):
                gui_parameters["Averaging reference cycles"] = 1
            gui_parameters["Lock-In low-pass filter"] = False
            if parameters.get("Lock-In low-pass filter"):
                gui_parameters["Low-pass Time Constant (s)"] = 0.1
                gui_parameters["Low-pass rolloff"] = ["6 dB/oct", "12 dB/oct", "18 dB/oct", "24 dB/oct"]
            gui_parameters["Lock-In harmonic"] = 1
            gui_parameters["Auto reference phase shift"] = True
            if not parameters.get("Auto reference phase shift"):
                gui_parameters["Reference phase shift (degree)"] = 0.0
            gui_parameters[""] = None  # Empty line 0

        gui_parameters["Range mode"] = ["Auto", "Manual"]
        meas_range = parameters.get("Range mode")
        if meas_range == "Manual":
            gui_parameters["Manual range limit"] = list(self.range_limits.keys())

        if not mode == "Lock-In":
            gui_parameters[" "] = None  # Empty line 1
            gui_parameters["Averaging time (NPLC)"] = 0.1
        gui_parameters["  "] = None  # Empty line 2
        gui_parameters["Enable bias voltage"] = False

        if parameters.get("Enable bias voltage"):
            gui_parameters["Bias voltage in V"] = 0.0

        gui_parameters["   "] = None  # Empty line 3
        gui_parameters["Advanced settings"] = False
        if parameters.get("Advanced settings"):
            gui_parameters["Analog input filter"] = False
            if parameters.get("Analog input filter"):
                gui_parameters["Filter optimization"] = list(self.filter_types.keys())
                if mode == "Lock-In":
                    gui_parameters["High pass corner frequency"] = list(self.cornerf_options.keys())
                    gui_parameters["High pass rolloff"] = ["6 dB/oct", "12 dB/oct"]
                gui_parameters["Low pass corner frequency"] = list(self.cornerf_options.keys())
                gui_parameters["Low pass rolloff"] = ["6 dB/oct", "12 dB/oct"]
                gui_parameters["    "] = None  # Empty line 4
            if mode == "Lock-In":
                gui_parameters["High pass digital filter"] = True
                gui_parameters["Frequency range threshold"] = 0.1
                gui_parameters["     "] = None  # Empty line 5
            gui_parameters["Turn off LED"] = False

        return gui_parameters

    def apply_gui_parameters(self, parameter):
        self.slot = parameter["Channel"]
        self.port_string = parameter["Port"]
        self.mode_set = parameter["Mode"]
        self.mode_read = self.modes[self.mode_set]
        self.range_mode = parameter["Range mode"]
        self.advanced = parameter["Advanced settings"]
        if parameter.get("Manual range limit"):
            self.limit = self.range_limits[parameter["Manual range limit"]]

        try:
            self.nplc = float(parameter["Averaging time (NPLC)"])
        except ValueError:  # Do not fail, if parameter is not yet loaded or empty
            self.nplc = 0.1

        if self.mode_set == "Lock-In":
            try:
                self.lia_ref = parameter["Lock-In reference source"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.lia_ref = "S0"
            try:
                self.lia_avg_filters = parameter["Lock-In averaging filter"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.lia_avg_filters = False
            if self.lia_avg_filters:
                try:
                    self.lia_avg_ref_cycles = int(parameter["Averaging reference cycles"])
                except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                    self.lia_avg_ref_cycles = 0
            try:
                self.lia_lowpass = parameter["Lock-In low-pass filter"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.lia_lowpass = False
            if self.lia_lowpass:
                try:
                    self.lia_rolloff = int(parameter["Low-pass rolloff"].split(" ")[0])
                except KeyError:  # Do not fail, if parameter is not yet loaded
                    self.lia_rolloff = 0
                try:
                    self.lia_tc = float(parameter["Low-pass Time Constant (s)"])
                except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                    self.lia_tc = 0.0
            try:
                self.lia_harm = int(parameter["Lock-In harmonic"])
            except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                self.lia_harm = 0
            try:
                self.lia_auto_phase = parameter["Auto reference phase shift"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.lia_auto_phase = True
            if not self.lia_auto_phase:
                try:
                    self.lia_ref_phase_shift = float(parameter["Reference phase shift (degree)"])
                except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                    self.lia_ref_phase_shift = 400  # Out of bound value to throw error during configure

        if self.advanced:
            try:
                self.filter_on = parameter["Analog input filter"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.filter_on = False
            try:
                self.darkmode = parameter["Turn off LED"]
            except KeyError:  # Do not fail, if parameter is not yet loaded
                self.darkmode = False
            if self.mode_set == "Lock-In":
                try:
                    self.high_digital_filter = parameter["High pass digital filter"]
                except KeyError:  # Do not fail, if parameter is not yet loaded
                    self.high_digital_filter = True
                try:
                    self.freq_range_threshold = parameter["Frequency range threshold"]
                except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                    self.freq_range_threshold = 0.1

            if self.filter_on:
                try:
                    self.filter_type = self.filter_types[parameter["Filter optimization"]]
                except KeyError:  # Do not fail, if parameter is not yet loaded
                    self.filter_type = ""
                try:
                    self.low_filter_cornerf = self.cornerf_options[parameter["Low pass corner frequency"]]
                except KeyError:  # Do not fail, if parameter is not yet loaded
                    self.low_filter_cornerf = ""
                try:
                    self.low_filter_rolloff = int(parameter["Low pass rolloff"].split(" ")[0])
                except KeyError:  # Do not fail, if parameter is not yet loaded
                    self.low_filter_rolloff = 0
                if self.mode_set == "Lock-In":
                    try:
                        self.high_filter_cornerf = self.cornerf_options[parameter["High pass corner frequency"]]
                    except KeyError:  # Do not fail, if parameter is not yet loaded
                        self.high_filter_cornerf = ""
                    try:
                        self.high_filter_rolloff = int(parameter["High pass rolloff"].split(" ")[0])
                    except KeyError:  # Do not fail, if parameter is not yet loaded
                        self.high_filter_rolloff = 0

        self.use_bias = bool(parameter["Enable bias voltage"])
        if self.use_bias:
            try:
                self.bias_voltage = float(parameter["Bias voltage in V"])
            except (KeyError, ValueError):  # Do not fail, if parameter is not yet loaded or empty
                self.bias_voltage = -1.0

        self.shortname = "CM-10 @ " + self.slot

        if self.mode_set == "Lock-In":
            self.variables = ["X", "Y", "Frequency", "Lock-In DC"]
            self.units = ["A", "A", "Hz", "A"]
        else:
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
        self.check_device()
        self.port.write(f'SENSe{self.slot[1]}:PRESet')

    def deinitialize(self):
        pass

    """ the following functions are called if a new branch is entered
     and the module was not part of the previous branch """

    def configure(self):
        self.set_mode(self.mode_set)
        self.set_range(self.limit)
        self.set_nplc(self.nplc)
        if self.mode_set == "Lock-In":
            self.set_lockin_settings()
        if self.advanced:
            self.set_advanced_settings()
        # Bias voltage must be set after filter settings or a warning will appear on the touch panel.
        self.set_bias(self.use_bias, self.bias_voltage)

    """ the following functions are called for each measurement point """

    def measure(self):
        # For Lock-In mode do not start a READ:SENSE read (which waits NPLC).
        # Instead fetch the latest settled LIA values in read_result() using FETCh queries.
        if not self.mode_set == "Lock-In":
            self.port.write(f"READ:SENS{self.slot[1]}:{self.mode_read}?")

    def read_result(self):
        if self.mode_set == "Lock-In":
            self.lia_result = self.read_lia()
        else:
            res = self.port.read()  # returns one-dimensional current value
            self.current = float(res)

    def call(self):
        if self.mode_set == "Lock-In":
            return [self.lia_result[0], self.lia_result[1], self.lia_result[2], self.lia_result[3]]
        else:
            return [self.current]

    """ wrapped functions """

    def set_mode(self, mode):
        if mode == "Lock-In":
            mode = "LIA"
        self.port.write(f'SENSe{self.slot[1]}:MODE {mode}')

    def set_range(self, limit):
        if self.range_mode == "Manual":
            if self.filter_on and self.filter_type == "REServe":
                if self.limit == 0.1:  # CM-10 does not allow this combination. It would quietly reduce the range.
                    raise ValueError("100 mA range cannot be used with filter optimization 'highest reserve'.")
            self.port.write(f'SENSe{self.slot[1]}:CURRent:RANGe:AUTO 0')
            self.port.write(f'SENSe{self.slot[1]}:CURRent:RANGe {limit}')
        else:
            self.port.write(f'SENSe{self.slot[1]}:CURRent:RANGe:AUTO 1')

    def set_nplc(self, nplc):
        if not (600 >= nplc >= 0.01):
            raise ValueError("NPLC must be between 0.01 and 600.00.")
        self.port.write(f'SENSe{self.slot[1]}:NPLCycles {nplc}')

    def set_bias(self, enabled, voltage):
        self.port.write(f'SENSe{self.slot[1]}:BIAS:STATe {"1" if enabled else "0"}')
        if enabled:
            if abs(voltage) > 0:
                if self.filter_on and self.filter_type == "NOISe":
                    raise ValueError("Bias voltage > 0 cannot be used with 'Lowest noise' filter optimization.")
                self.port.write(f'SENSe{self.slot[1]}:BIAS:VOLTage {voltage}')
            elif voltage == 0:
                self.port.write(f'SENSe{self.slot[1]}:BIAS:VOLTage 0')
            else:
                raise ValueError("Bias voltage is enabled, but no value has been given. "
                                 "Set a value in Volts or disable bias voltage.")

    def check_device(self):
        model = self.port.query(f'SENSe{self.slot[1]}:MODel?')
        if not "CM-10" in model:
            raise ValueError(
                f"Device connected on channel {self.slot} does not match this driver. "
                f"Found: '{model}'"
            )

    def set_lockin_settings(self):
        """Wrapper function to set configurations for Lock-In Amplifier (LIA) mode."""
        if self.lia_harm < 1:
            raise ValueError("Lock-In harmonic must be >= 1")
        # Reference source
        self.port.write(f"SENSe{self.slot[1]}:LIA:RSOurce {self.lia_ref}")
        # Enable/Disable averaging filter
        self.port.write(f'SENSe{self.slot[1]}:LIA:AVERage {"1" if self.lia_avg_filters else "0"}')
        # Reference harmonic
        self.port.write(f"SENSe{self.slot[1]}:LIA:DHARmonic {self.lia_harm}")
        # Enable/Disable Lowpass filter
        self.port.write(f'SENSe{self.slot[1]}:LIA:LPASs {"1" if self.lia_lowpass else "0"}')
        # Number of averaging cycles
        if self.lia_avg_filters:
            if not (1000000 >= self.lia_avg_ref_cycles >= 1):
                raise ValueError("Number of reference cycles must be >= 1 and <= 1,000,000.")
            self.port.write(f"SENSe{self.slot[1]}:LIA:REFerence:CYCLes {self.lia_avg_ref_cycles}")
        # Time constant and rolloff for lowpass filter
        if self.lia_lowpass:
            if not (10000 >= self.lia_tc >= 0.0001):
                raise ValueError("Lock-In time constant must be >= 0.0001 s and <= 10,000 s.")
            self.port.write(f"SENSe{self.slot[1]}:LIA:TIMEconstant {self.lia_tc}")
            self.port.write(f"SENSe{self.slot[1]}:LIA:ROLLoff R{self.lia_rolloff}")
        # Phase shift to lock-in reference source
        if self.lia_auto_phase:
            self.port.write(f"SENSe{self.slot[1]}:LIA:DPHase:AUTO")
        else:
            if not (360 >= self.lia_ref_phase_shift >= -360):
                raise ValueError("Phase shift must be between -360 and +360 degrees.")
            self.port.write(f"SENSe{self.slot[1]}:LIA:DPHase {self.lia_ref_phase_shift}")

    def set_advanced_settings(self):
        if self.filter_on:
            self.set_filters()
        else:
            self.port.write(f'SENSe{self.slot[1]}:FILTer:STATe 0')
        self.port.write(f'SENSe{self.slot[1]}:DMODe {"1" if self.darkmode else "0"}')
        if self.mode_set == "Lock-In":
            self.port.write(f'SENSe{self.slot[1]}:DIGital:FILTer:HPASs {"1" if self.high_digital_filter else "0"}')
            self.port.write(f'SENSe{self.slot[1]}:FRTHreshold {self.freq_range_threshold}')

    def set_filters(self):
        self.port.write(f'SENSe{self.slot[1]}:FILTer:STATe 1')
        self.port.write(f'SENSe{self.slot[1]}:FILTer:OPTimization {self.filter_type}')
        self.port.write(f'SENSe{self.slot[1]}:FILTer:LPASs:FREQuency {self.low_filter_cornerf}')
        self.port.write(f'SENSe{self.slot[1]}:FILTer:LPASs:ATTenuation R{self.low_filter_rolloff}')
        if self.mode_set == "Lock-In":
            self.port.write(f'SENSe{self.slot[1]}:FILTer:HPASs:FREQuency {self.high_filter_cornerf}')
            self.port.write(f'SENSe{self.slot[1]}:FILTer:HPASs:ATTenuation R{self.high_filter_rolloff}')

    def read_lia(self):
        # Use Fetch to get X and Y (latest settled values).
        self.port.write(f"FETCh:MULTiple? MX,{self.slot[1]},MY,{self.slot[1]}")
        resp = self.port.read().split(",")
        x_lia = self.lia_convert(resp[0])
        y_lia = self.lia_convert(resp[1])

        # Fetch frequency separately, because it doesn't support FETCh:MULTIple
        self.port.write(f"FETCh:SENSe{self.slot[1]}:LIA:FREQuency?")
        freq = self.lia_convert(self.port.read())

        # Fetch DC separately, because it doesn't support FETCh:MULTIple
        self.port.write(f"FETCh:SENSe{self.slot[1]}:LIA:DC?")
        dc = self.lia_convert(self.port.read())

        return x_lia, y_lia, freq, dc

    @staticmethod
    def lia_convert(value_str: str) -> float:
        """Convert M81 LIA sentinel values into Python float equivalents."""
        try:
            val = float(value_str)
        except ValueError:
            return float('nan')

        # Special value M81: Overload → +inf
        if abs(val - 9.90e37) < 1e33:
            return float('inf')

        # Special value M81: PLL unlocked → NaN
        if abs(val - 9.91e37) < 1e33:
            return float('nan')

        return val

