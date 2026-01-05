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
        self.sweepmode: str = "Amplitude in V"  # SweepMode selection
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
        self.sync_enabled: bool = False
        self.sync_source: str = "S1"
        self.sync_phase: float = 0.0
        self.current_protect: float = None  # Current protection level in mA (DC limit), None: Not in use
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
            "SweepMode": ["Amplitude in V", "Offset in V", "Frequency in Hz"]}
        sweep_mode = parameters.get("SweepMode")
        if sweep_mode != "Amplitude in V":
            gui_parameters["Amplitude in V"] = 0.0

        # Source shapes
        self.shapes = {
            "Sine": "SINusoid",
            "Triangle": "TRIangle",
            "Square": "SQUAre",
        }
        if sweep_mode == "Amplitude in V":
            self.shapes["DC"] = "DC"  # DC mode is not meaningful for offset- or frequency-sweeps.

        gui_parameters["Shape"] = list(self.shapes.keys())
        gui_parameters["Range mode"] = ["Auto", "Manual"]

        # shape-dependent fields
        shape = parameters.get("Shape")
        if shape and shape != "DC":
            if sweep_mode != "Offset in V":
                gui_parameters["Offset in V"] = 0.0
            if sweep_mode != "Frequency in Hz" and not self.sync_enabled:
                gui_parameters["Frequency in Hz"] = 11.0
            if shape in ["Square", "Triangle"]:
                gui_parameters["Duty"] = 0.5  # 0.0 - 1.0 (0.001 - 0.999 recommended)

        meas_range = parameters.get("Range mode")
        if meas_range == "Manual":
            # allow user to set DC and AC ranges independently
            gui_parameters["Manual DC range limit"] = list(self.range_limits.keys())
            if parameters.get("Shape") != "DC":
                gui_parameters["Manual AC range limit"] = list(self.range_limits.keys())
        gui_parameters[" "] = None  # Empty line 1
        gui_parameters["Optional advanced settings"] = None
        gui_parameters["Current protection in mA"] = 100.0
        gui_parameters["High output limit in V"] = 10.0
        gui_parameters["Low output limit in V"] = -10.0
        if shape != "DC":
            gui_parameters["Sync"] = False
            if parameters.get("Sync"):
                gui_parameters["Sync source"] = ["S1", "S2", "S3"]
                gui_parameters["Sync phase in degree"] = 0.0
        gui_parameters["Turn off LED"] = False

        return gui_parameters

    def apply_gui_parameters(self, parameter):
        # Basic parameters
        channel = parameter.get("Channel")
        if channel.strip().lower() in ["s1", "s2", "s3"]:
            self.slot = channel[1]  # e.g. "1 for "S1"
        else:
            self.slot = ""  # default
        self.port_string = parameter["Port"]
        self.sweepmode = parameter.get("SweepMode")
        if self.sweepmode != "Amplitude in V":
            self.amplitude = float(parameter["Amplitude in V"])

        self.shape_set = parameter["Shape"]
        try:
            self.shape_scpi = self.shapes[self.shape_set]
        except KeyError:
            self.shape_scpi = "DC"
        self.range_mode = parameter["Range mode"]
        if parameter.get("Manual DC range limit"):
            self.dc_range_limit = self.range_limits[parameter["Manual DC range limit"]]
        if parameter.get("Manual AC range limit"):
            self.ac_range_limit = self.range_limits[parameter["Manual AC range limit"]]

        # Frequency and duty (only valid for non-DC shapes)
        if self.shape_set != "DC":
            try:
                self.freq = float(parameter["Frequency in Hz"])
            except (KeyError, ValueError):
                self.freq = 0
            try:
                self.offset = float(parameter["Offset in V"])
            except (KeyError, ValueError):
                self.offset = 0.0
            if self.shape_set in ["Square", "Triangle"]:
                try:
                    self.duty = float(parameter["Duty"])
                except (KeyError, ValueError):
                    self.duty = 0.5

        # Advanced
        self.current_protect = parameter.get("Current protection in mA", None)
        self.vlim_high = parameter.get("High output limit in V", None)
        if self.vlim_high:
            self.vlim_high = float(self.vlim_high)
        self.vlim_low = parameter.get("Low output limit in V", None)
        if self.vlim_low:
            self.vlim_low = float(self.vlim_low)
        # Sync
        if self.shape_set != "DC":
            self.sync_enabled = parameter.get("Sync", False)
            if self.sync_enabled:
                try:
                    self.sync_source = parameter["Sync source"]
                except KeyError:
                    self.sync_source = "S0"
                try:
                    self.sync_phase = float(parameter["Sync phase in degree"])
                except (KeyError, ValueError):
                    self.sync_phase = 0.0
        else:
            # force sync off for DC shape
            self.sync_enabled = False

        # Dark mode
        self.dark = parameter.get("Turn off LED", False)

        self.shortname = "VS-10 @ S" + self.slot

        # GUI variables
        if self.shape_set == "DC":
            self.variables = ["Voltage"]
            self.units = ["V"]
        elif self.shape_set == "Sine":
            self.variables = ["Voltage RMS", "Voltage Peak", "Frequency", "Offset"]
            self.units = ["V", "V", "Hz", "V"]
        else:
            self.variables = ["Voltage Peak", "Frequency", "Offset"]
            self.units = ["V", "Hz", "V"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        # validate limits and device identity
        self.check_device()
        # Reset to module defaults
        self.port.write(f"SOURce{self.slot}:PRESet")

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
        # Sync
        self.set_sync()
        # Current protection and voltage limits (must be set after shape/amplitude so they apply to configured values)
        self.set_voltage_limits(self.vlim_low, self.vlim_high)
        self.set_current_protection(self.current_protect)
        # Dark mode setting
        self.set_dark()

        # Amplitude, Frequency and Offset
        if self.sweepmode.startswith("Amplitude"):
            self.set_amplitude(0)  # Safe starting condition, sweep-value will be set in apply
        else:
            self.set_amplitude(self.amplitude)
        if self.sweepmode.startswith("Offset"):
            self.set_offset(0)  # Safe starting condition, sweep-value will be set in apply
        else:
            self.set_offset(self.offset)
        if self.sweepmode != "Frequency in Hz" and self.shape_set != "DC" and not self.sync_enabled:
            self.set_frequency(self.freq)

    def poweron(self):
        # Turn on output
        self.port.write(f"SOURce{self.slot}:STATe 1")

    """ the following functions are called for each measurement point """

    def apply(self):
        """Only called if the sweep value changes: Sets a new value to the device."""
        if self.sweepmode.startswith("Amplitude"):
            self.set_amplitude(float(self.value))
        elif self.sweepmode.startswith("Frequency"):
            self.set_frequency(float(self.value))
        elif self.sweepmode.startswith("Offset"):
            self.set_offset(float(self.value))

    def read_result(self):
        # Return last applied voltage as the measurement; read back from instrument to be accurate
        # Query the actual applied voltage (SOURce#:VOLTage:LEVel:AMPLitude:PEAK?)
        self.port.write(f"SOURce{self.slot}:VOLTage:LEVel:AMPLitude:PEAK?")
        try:
            self.peak_read = float(self.port.read())
        except (ValueError, TypeError):
            self.peak_read = float('nan')
        if self.shape_set != "DC":
            self.port.write(f"SOURce{self.slot}:VOLTage:LEVel:OFFSet?")
            try:
                self.offset_read = float(self.port.read())
            except (ValueError, TypeError):
                self.offset_read = float('nan')
            if self.sync_enabled:
                self.port.write(f"SOURce{self.sync_source[1]}:FREQuency?")  # Frequency VS-10 = Frequency sync source
            else:
                self.port.write(f"SOURce{self.slot}:FREQuency?")
            try:
                self.freq_read = float(self.port.read())
            except (ValueError, TypeError):
                self.freq_read = float('nan')
            if self.shape_set == "Sine":
                self.port.write(f"SOURce{self.slot}:VOLTage:LEVel:AMPLitude:RMS?")
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
        # Turn off output
        self.port.write(f"SOURce{self.slot}:STATe 0")

    """ wrapped functions """

    def set_amplitude(self, amplitude: float):
        """Set source amplitude (peak)."""
        if self.vlim_low:
            if self.vlim_low > (-abs(amplitude) + self.offset):
                raise ValueError("Output (= Amplitude + Offset) must be within the limits you set.")
        if self.vlim_high:
            if self.vlim_high < (abs(amplitude) + self.offset):
                raise ValueError("Output (= Amplitude + Offset) must be within the limits you set.")
        self.port.write(f"SOURce{self.slot}:VOLTage:LEVel:AMPLitude:PEAK {amplitude}")

    def set_offset(self, offset: float):
        """Set voltage offset."""
        self.port.write(f"SOURce{self.slot}:VOLTage:LEVel:OFFSet {offset}")

    def set_shape(self, scpi_shape: str):
        """Set the source shape (DC, SINusoid, TRIangle, SQUAre)."""
        if scpi_shape:
            self.port.write(f"SOURce{self.slot}:FUNCtion:SHAPe {scpi_shape}")
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
            self.port.write(f"SOURce{self.slot}:FREQuency:FIXed {frequency}")

    def set_duty(self, duty: float):
        """Set duty cycle for Triangle and Square shapes. Allowed 0.0-1.0; M81 supports 0.001-0.999 increments."""
        if not (0.0 <= duty <= 1.0):
            raise ValueError("Duty must be between 0.0 and 1.0.")
        # M81 supports 0.001..0.999 but allows 0 and 1 (become DC).
        self.port.write(f"SOURce{self.slot}:DCYCle {duty}")

    def set_ranging(self, mode: str, dc_limit: Optional[float], ac_limit: Optional[float]):
        """Set range mode and manual limits for DC and AC. Uses:
           SOURce#:VOLTage:RANGe:AUTO
           SOURce#:VOLTage:RANGe:DC
           SOURce#:VOLTage:RANGe:AC
        """
        if mode == "Manual":
            # Disable auto
            self.port.write(f"SOURce{self.slot}:VOLTage:RANGe:AUTO 0")
            self.port.write(f"SOURce{self.slot}:VOLTage:RANGe:DC {dc_limit}")
            # For AC, only set if shape is not DC
            if self.shape_set != "DC":
                if ac_limit is None:
                    raise ValueError("Manual AC range limit not provided for AC shape.")
                self.port.write(f"SOURce{self.slot}:VOLTage:RANGe:AC {ac_limit}")
        else:
            # Auto ranges
            self.port.write(f"SOURce{self.slot}:VOLTage:RANGe:AUTO 1")

    def set_sync(self):
        # Sync only valid for non-DC shapes (per manual)
        if self.shape_set != "DC":
            self.port.write(f"SOURce{self.slot}:SYNChronize:STATe {'1' if self.sync_enabled else '0'}")
            if self.sync_enabled:
                if self.sweepmode == "Frequency in Hz":
                    raise ValueError("Frequency sweep is not possible while device is in sync mode.")
                if self.sync_source == f"S{self.slot}":
                    raise ValueError("Source can not be synced to itself.")
                # Sync source and phase
                self.port.write(f"SOURce{self.slot}:SYNChronize:SOURce {self.sync_source}")
                # phase in degrees
                if not (-360 <= self.sync_phase <= 360):
                    raise ValueError("Sync phase must be between -360 and +360 degrees.")
                self.port.write(f"SOURce{self.slot}:SYNChronize:PHASe {self.sync_phase}")
        else:
            # ensure sync disabled for DC
            self.port.write(f"SOURce{self.slot}:SYNChronize:STATe 0")

    def set_current_protection(self, current_protection: float):
        """Set DC current protection level (SOURce#:CURRent:PROTection)."""
        if current_protection:  # If field is empty, level is NoneType and nothing is set.
            level = float(current_protection)
            if not (0 <= level <= 100):
                raise ValueError("Current protection level must be between 0 and 100 mA.")
            level = level / 1000  # Level is set in the GUI in mA, convert to A
            self.port.write(f"SOURce{self.slot}:CURRent:PROTection {level}")

    def set_voltage_limits(self, low: float, high: float):
        """Set software high/low voltage output limits:
           SOURce#:VOLTage:LIMit:LOW
           SOURce#:VOLTage:LIMit:HIGH
        """
        if low:
            if low < -10.0:
                raise ValueError("Lower voltage limit must not exceed -10 V.")
        if high:
            if high > 10.0:
                raise ValueError("Higher voltage limit must not exceed 10 V.")
        if high and low:
            if high <= low:
                raise ValueError("Higher voltage limit must be above lower limit.")
        if low:  # If field is empty, level is NoneType and nothing is set. (Preset: -10 V)
            self.port.write(f"SOURce{self.slot}:VOLTage:LIMit:LOW {low}")
        if high:  # If field is empty, level is NoneType and nothing is set. (Preset: +10 V)
            self.port.write(f"SOURce{self.slot}:VOLTage:LIMit:HIGH {high}")

    def set_dark(self):
        self.port.write(f"SOURce{self.slot}:DMODe {'1' if self.dark else '0'}")

    def check_device(self):
        """Check connected device is a VS-10 module."""
        model = self.port.query(f"SOURce{self.slot}:MODel?")
        if not "VS-10" in model:
            raise ValueError(
                f"Device connected on channel S{self.slot} does not match this driver. Found: '{model}'"
            )
