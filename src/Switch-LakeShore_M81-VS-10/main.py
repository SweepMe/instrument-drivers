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
# * Module: Switch
# * Instrument: LakeShore M81 VS-10

from pysweepme.EmptyDeviceClass import EmptyDevice
from typing import Optional

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

        # Source shapes (fill later)
        self.shapes = {}

        # Voltage ranges (V)
        self.range_limits = {
            "10 V": 10.0,
            "1 V": 1.0,
            "100 mV": 0.1,
            "10 mV": 0.01,
        }

        # Default GUI / internal parameters
        self.slot: str = "S0"             # Source slot naming, use e.g. "S1","S2","S3" in GUI
        self.port_string: str = ""
        self.sweepmode: str = "Amplitude (V)"  # SweepMode selection
        self.amplitude: float = 0.0       # source amplitude
        self.offset: float = 0.0          # DC offset (valid for all shapes)
        self.applied_voltage: float = float('nan')
        self.shape_set: str = ""        # User-readable shape string
        self.shape_scpi: str = ""       # SCPI token (SINusoid, TRIangle, SQUAre, DC)
        self.freq: float = 11.0           # Frequency in Hz (default per manual)
        self.duty: float = 0.5            # Duty (0.0 - 1.0) for square & triangle (0.001-0.999 valid)
        self.range_mode: str = "Auto"     # "Auto" or "Manual"
        self.dc_range_limit: float = 0.01 # default DC range (V) when manual selected
        self.ac_range_limit: float = 0.01 # default AC range (V) when manual selected
        self.advanced: bool = False
        self.sync_enabled: bool = False
        self.sync_source: str = "S1"
        self.sync_phase: float = 0.0
        self.current_protect: float = 100  # Current protection level in mA (DC limit), default 100 mA
        self.vlim_high: float = 10.0
        self.vlim_low: float = -10.0
        self.dark: bool = False
        self.rms_read: float = 0.0
        self.peak_read: float = 0.0
        self.offset_read: float = 0.0
        self.freq_read: float = 0.0

    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "Channel": ["S1", "S2", "S3"],
            "SweepMode": ["Amplitude (V)", "Offset (V)", "Frequency (Hz)"]}
        self.sweepmode = parameters.get("SweepMode")
        if self.sweepmode != "Amplitude (V)":
            gui_parameters["Amplitude (V)"] = 0.0

        # Source shapes
        if self.sweepmode == "Amplitude (V)":
            self.shapes["DC"] = "DC"  # DC mode is not meaningful for offset- or frequency-sweeps.
        self.shapes["Sine"] = "SINusoid"
        self.shapes["Triangle"] = "TRIangle"
        self.shapes["Square"] = "SQUAre"

        gui_parameters["Shape"] = list(self.shapes.keys())
        gui_parameters["Range Mode"] = ["Auto", "Manual"]

        # shape-dependent fields
        shape = parameters.get("Shape")
        if shape and shape != "DC":
            if self.sweepmode != "Offset (V)":
                gui_parameters["Offset (V)"] = 0.0
            if self.sweepmode != "Frequency (Hz)" and not self.sync_enabled:
                gui_parameters["Frequency (Hz)"] = 11.0
            if shape in ["Square", "Triangle"]:
                gui_parameters["Duty"] = 0.5  # 0.0 - 1.0 (0.001 - 0.999 recommended)

        meas_range = parameters.get("Range Mode")
        if meas_range == "Manual":
            # allow user to set DC and AC ranges independently
            gui_parameters["Manual DC range limit"] = list(self.range_limits.keys())
            if parameters.get("Shape") != "DC":
                gui_parameters["Manual AC range limit"] = list(self.range_limits.keys())
        gui_parameters[" "] = None  # Empty line 1
        gui_parameters["Advanced Settings"] = False
        if parameters.get("Advanced Settings"):
            gui_parameters["Current protection (mA)"] = 100.0
            gui_parameters["High voltage output limit (V)"] = 10.0
            gui_parameters["Low voltage output limit (V)"] = -10.0
            if shape != "DC":
                gui_parameters["Sync"] = False
                if parameters.get("Sync"):
                    gui_parameters["Sync Source"] = ["S1", "S2", "S3"]
                    gui_parameters["Sync Phase (deg)"] = 0.0
            gui_parameters["Turn off LED"] = False

        return gui_parameters

    def apply_gui_parameters(self, parameter):
        # Basic parameters
        self.slot = parameter["Channel"]
        self.port_string = parameter["Port"]
        if self.sweepmode != "Amplitude (V)":
            self.amplitude = float(parameter["Amplitude (V)"])

        self.shape_set = parameter["Shape"]
        try:
            self.shape_scpi = self.shapes[self.shape_set]
        except KeyError:
            self.shape_scpi = ""
        self.range_mode = parameter["Range Mode"]
        if parameter.get("Manual DC range limit"):
            self.dc_range_limit = self.range_limits[parameter["Manual DC range limit"]]
        if parameter.get("Manual AC range limit"):
            self.ac_range_limit = self.range_limits[parameter["Manual AC range limit"]]

        # Frequency and duty (only valid for non-DC shapes)
        if self.shape_set != "DC":
            try:
                self.freq = float(parameter["Frequency (Hz)"])
            except (KeyError, ValueError):
                self.freq = 0
            try:
                self.offset = float(parameter["Offset (V)"])
            except (KeyError, ValueError):
                self.offset = 0.0
            if self.shape_set in ["Square", "Triangle"]:
                try:
                    self.duty = float(parameter["Duty"])
                except (KeyError, ValueError):
                    self.duty = 0.5

        # Advanced
        self.advanced = parameter["Advanced Settings"]
        if self.advanced:
            try:
                self.current_protect = float(parameter["Current protection (mA)"])
            except (KeyError, ValueError):
                self.current_protect = 0.000001
            try:
                self.vlim_high = float(parameter["High voltage output limit (V)"])
                self.vlim_low = float(parameter["Low voltage output limit (V)"])
            except (KeyError, ValueError):
                self.vlim_high = 0
                self.vlim_low = 0

            # Sync
            if self.shape_set != "DC":
                try:
                    self.sync_enabled = parameter.get("Sync", False)
                except KeyError:
                    self.sync_enabled = False
                if self.sync_enabled:
                    try:
                        self.sync_source = parameter["Sync Source"]
                    except KeyError:
                        self.sync_source = "S0"
                    try:
                        self.sync_phase = float(parameter["Sync Phase (deg)"])
                    except (KeyError, ValueError):
                        self.sync_phase = 0.0
            else:
                # force sync off for DC shape
                self.sync_enabled = False

            # Dark mode
            self.dark = parameter.get("Turn off LED", False)

        self.shortname = "VS-10 @ " + self.slot

        # GUI variables
        if self.shape_set == "DC":
            self.variables = ["Voltage"]
            self.units = ["V"]
            self.plottype = [True]
            self.savetype = [True]
        elif self.shape_set == "Sine":
            self.variables = ["Voltage RMS", "Voltage Peak", "Frequency", "Offset"]
            self.units = ["V", "V", "Hz", "V"]
            self.plottype = [True, True, True, True]
            self.savetype = [True, True, True, True]
        else:
            self.variables = ["Voltage Peak", "Frequency", "Offset"]
            self.units = ["V", "Hz", "V"]
            self.plottype = [True, True, True]
            self.savetype = [True, True, True]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        # validate limits and device identity
        self.check_device()
        # Reset to module defaults
        self.port.write(f"SOURce{self.slot[1]}:PRESet")

    def deinitialize(self):
        pass

    """ the following functions are called if a new branch is entered
     and the module was not part of the previous branch """

    def configure(self):
        # Ranging: AC and DC ranges (Auto vs Manual)
        self.set_ranging(self.range_mode, self.dc_range_limit, self.ac_range_limit)

        # Voltage shape
        self.set_shape(self.shape_scpi)

        # Duty
        if self.shape_set in ["Square", "Triangle"]:
            self.set_duty(self.duty)

        # Advanced settings
        if self.advanced:
            self.set_advanced_settings()
            # Current protection and voltage limits (must be set after shape/amplitude so they apply to configured values)
            self.set_voltage_limits(self.vlim_low, self.vlim_high)
            self.set_current_protection(self.current_protect)

    """ the following functions are called for each measurement point """

    def start(self):
        # Amplitude, Frequency and Offset
        if self.sweepmode != "Amplitude (V)":
            self.set_amplitude(self.amplitude)
        if self.sweepmode != "Frequency (Hz)" and self.shape_set != "DC" and not self.sync_enabled:
            self.set_frequency(self.freq)
        if self.sweepmode != "Offset (V)":
            self.set_offset(self.offset)
        self.port.write(f"SOURce{self.slot[1]}:STATe 1")

    def apply(self):
        """Only called if the sweep value changes: Sets a new value to the device."""
        if self.sweepmode == "Amplitude (V)":
            self.set_amplitude(float(self.value))
        elif self.sweepmode == "Frequency (Hz)":
            self.set_frequency(float(self.value))
        elif self.sweepmode == "Offset (V)":
            self.set_offset(float(self.value))

    def read_result(self):
        # Return last applied voltage as the measurement; read back from instrument to be accurate
        # Query the actual applied voltage (SOURce#:VOLTage:LEVel:AMPLitude:PEAK?)
        self.port.write(f"SOURce{self.slot[1]}:VOLTage:LEVel:AMPLitude:PEAK?")
        try:
            self.peak_read = float(self.port.read())
        except (ValueError, TypeError):
            self.peak_read = float('nan')
        if self.shape_set != "DC":
            self.port.write(f"SOURce{self.slot[1]}:VOLTage:LEVel:OFFSet?")
            try:
                self.offset_read = float(self.port.read())
            except (ValueError, TypeError):
                self.offset_read = float('nan')
            if self.sync_enabled:
                self.port.write(f"SOURce{self.sync_source[1]}:FREQuency?")  # Frequency VS-10 = Frequency sync source
            else:
                self.port.write(f"SOURce{self.slot[1]}:FREQuency?")
            try:
                self.freq_read = float(self.port.read())
            except (ValueError, TypeError):
                self.freq_read = float('nan')
            if self.shape_set == "Sine":
                self.port.write(f"SOURce{self.slot[1]}:VOLTage:LEVel:AMPLitude:RMS?")
                try:
                    self.rms_read = float(self.port.read())
                except (ValueError, TypeError):
                    self.rms_read = float('nan')

    def call(self):
        if self.shape_set == "DC":
            return [self.peak_read]
        elif self.shape_set == "Sine":
            return [self.rms_read, self.peak_read, self.freq_read, self.offset_read]
        else:
            return [self.peak_read, self.freq_read, self.offset_read]

    def poweroff(self):
        self.port.write(f"SOURce{self.slot[1]}:STATe 0")

    """ wrapped functions """

    def set_amplitude(self, amplitude: float):
        """Set source amplitude (peak)."""
        if (self.vlim_low > (-abs(amplitude) + self.offset)) or (self.vlim_high < (abs(amplitude) + self.offset)):
            raise ValueError("Output (= Amplitude + Offset) must be within the limits you set.")
        self.amplitude = amplitude
        self.port.write(f"SOURce{self.slot[1]}:VOLTage:LEVel:AMPLitude:PEAK {amplitude}")

    def set_offset(self, offset: float):
        """Set voltage offset."""
        self.port.write(f"SOURce{self.slot[1]}:VOLTage:LEVel:OFFSet {offset}")

    def set_shape(self, scpi_shape: str):
        """Set the source shape (DC, SINusoid, TRIangle, SQUAre)."""
        if scpi_shape:
            self.port.write(f"SOURce{self.slot[1]}:FUNCtion:SHAPe {scpi_shape}")
        else:
            raise ValueError("Shape may not be empty.")

    def set_frequency(self, frequency: float):
        """Set excitation frequency (for non-DC shapes)."""
        if self.shape_set in ["Square", "Triangle"]:
            if not (0.0001 <= frequency <= 5000):
                raise ValueError("Frequency must be between 0.1 mHz and 5 kHz for triangle and square shapes.")
        else:
            if not (0.0001 <= frequency <= 100000):
                raise ValueError("Frequency must be between 0.1 mHz and 100 kHz for sine waves.")
        if not self.sync_enabled:  # Sync gets the frequency from another source.
            self.port.write(f"SOURce{self.slot[1]}:FREQuency:FIXed {self.freq}")

    def set_duty(self, duty: float):
        """Set duty cycle for Triangle and Square shapes. Allowed 0.0-1.0; M81 supports 0.001-0.999 increments."""
        if not (0.0 <= duty <= 1.0):
            raise ValueError("Duty must be between 0.0 and 1.0.")
        # M81 supports 0.001..0.999 but allows 0 and 1 (become DC).
        self.port.write(f"SOURce{self.slot[1]}:DCYCle {duty}")

    def set_ranging(self, mode: str, dc_limit: Optional[float], ac_limit: Optional[float]):
        """Set range mode and manual limits for DC and AC. Uses:
           SOURce#:VOLTage:RANGe:AUTO
           SOURce#:VOLTage:RANGe:DC
           SOURce#:VOLTage:RANGe:AC
        """
        if mode == "Manual":
            # Disable auto
            self.port.write(f"SOURce{self.slot[1]}:VOLTage:RANGe:AUTO 0")
            self.port.write(f"SOURce{self.slot[1]}:VOLTage:RANGe:DC {dc_limit}")
            # For AC, only set if shape is not DC
            if self.shape_set != "DC":
                if ac_limit is None:
                    raise ValueError("Manual AC range limit not provided for AC shape.")
                self.port.write(f"SOURce{self.slot[1]}:VOLTage:RANGe:AC {ac_limit}")
        else:
            # Auto ranges
            self.port.write(f"SOURce{self.slot[1]}:VOLTage:RANGe:AUTO 1")

    def set_advanced_settings(self):
        """Advanced settings: Sync, dark mode, etc."""
        # Sync only valid for non-DC shapes (per manual)
        if self.shape_set != "DC":
            self.port.write(f"SOURce{self.slot[1]}:SYNChronize:STATe {'1' if self.sync_enabled else '0'}")
            if self.sync_enabled:
                if self.sweepmode == "Frequency (Hz)":
                    raise ValueError("Frequency sweep is not possible while device is in sync mode.")
                if self.sync_source == self.slot:
                    raise ValueError("Source can not be synced to itself.")
                # Sync source and phase
                self.port.write(f"SOURce{self.slot[1]}:SYNChronize:SOURce {self.sync_source}")
                # phase in degrees
                if not (-360 <= self.sync_phase <= 360):
                    raise ValueError("Sync phase must be between -360 and +360 degrees.")
                self.port.write(f"SOURce{self.slot[1]}:SYNChronize:PHASe {self.sync_phase}")
        else:
            # ensure sync disabled for DC
            self.port.write(f"SOURce{self.slot[1]}:SYNChronize:STATe 0")

        # Dark mode setting if provided via GUI Advanced Settings
        self.port.write(f"SOURce{self.slot[1]}:DMODe {'1' if self.dark else '0'}")

    def set_current_protection(self, level: float):
        """Set DC current protection level (SOURce#:CURRent:PROTection)."""
        level = level/1000  # Level is set in the GUI in mA, convert to A
        if not (0 <= level <= 100):
            raise ValueError("Current protection level must be between 0 and 100 mA.")
        self.port.write(f"SOURce{self.slot[1]}:CURRent:PROTection {level}")

    def set_voltage_limits(self, low: float, high: float):
        """Set software high/low voltage output limits:
           SOURce#:VOLTage:LIMit:LOW
           SOURce#:VOLTage:LIMit:HIGH
        """
        if not (-10.0 <= low < high <= 10.0):
            raise ValueError("Voltage limits must not exceed +-10 V "
                             "and the low limit needs be smaller than the high one.")

        self.port.write(f"SOURce{self.slot[1]}:VOLTage:LIMit:LOW {low}")
        self.port.write(f"SOURce{self.slot[1]}:VOLTage:LIMit:HIGH {high}")

    def check_device(self):
        """Check connected device is a VS-10 module."""
        model = self.port.query(f"SOURce{self.slot[1]}:MODel?")
        if not "VS-10" in model:
            raise ValueError(
                f"Device connected on channel {self.slot} does not match this driver. Found: '{model}'"
            )
