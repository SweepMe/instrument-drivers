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
# * Module: SMU
# * Instrument: LakeShore M81 VS-10 + CM-10

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

        self.source_range_limits = {
            "Auto": 0,
            "10 V": 10.0,
            "1 V": 1.0,
            "100 mV": 0.1,
            "10 mV": 0.01,
        }

        # Current range limits for the CM-10 in A
        self.current_range_limits = {
            "Auto": 0,
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

        self.speed_nplcs = {
            "Fast (0.1 NPLC)": 0.1,
            "Medium (1.0 NPLC)": 1.0,
            "Slow (10.0 NPLC)": 10.0,
        }

        # Common parameters
        # Source slot
        self.sslot: str = "S0"
        self.mslot: str = "M0"
        self.port_string: str = ""
        self.dark: bool = False

        # Source parameters
        self.range_source: float = 0
        self.current_protect: float = 0.1  # A
        self.vlim_high: float = 10.0
        self.vlim_low: float = -10.0

        # Measure internal parameters (CM-10 style)
        self.nplc: float = 0.1
        self.range_current: float = 0

        # Readback storage
        self.volt_read: float = float('nan')

        # Measurement storage
        self.current: float = float('nan')

    # ---------------- GUI parameter builders ----------------
    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "Source channel": ["S1", "S2", "S3"],
            "Measure channel": ["M1", "M2", "M3"],
            "SweepMode": ["Voltage (V)"],
            "Compliance": 0.1,  # Compliance called "Current protection" in VS-10
            "Speed": list(self.speed_nplcs.keys()),
            "RangeVoltage": list(self.source_range_limits.keys()),
            "Range": list(self.current_range_limits.keys()),
            # Voltage limits
            "High voltage output limit (V)": 10.0,
            "Low voltage output limit (V)": -10.0,
            # Dark mode
            "Turn off LEDs": False,
        }
        return gui_parameters

    def apply_gui_parameters(self, parameter):
        # Source / measure channel mapping
        self.sslot = parameter["Source channel"]  # e.g. "S1"
        self.mslot = parameter["Measure channel"]  # e.g. "M1"
        self.port_string = parameter["Port"]
        self.range_source = self.source_range_limits[parameter["RangeVoltage"]]
        self.range_current = self.current_range_limits[parameter["Range"]]
        try:
            self.current_protect = float(parameter["Compliance"])
        except (KeyError, TypeError):
            self.current_protect = 0.1

        try:
            self.vlim_high = float(parameter["High voltage output limit (V)"])
            self.vlim_low = float(parameter["Low voltage output limit (V)"])
        except (KeyError, TypeError):
            self.vlim_high = 0.0
            self.vlim_low = 0.0

        try:
            self.nplc = float(self.speed_nplcs[parameter["Speed"]])
        except KeyError:
            self.nplc = 0.0

        self.dark = parameter.get("Turn off LEDs", False)

        # Short name and GUI variables
        self.shortname = f"SMU VS-10 S{self.sslot[1]} / CM-10 M{self.mslot[1]}"
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

    # ---------------- SweepMe semantic functions ----------------
    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        # Check that both modules are present
        self.check_device()
        # Reset both source and measure modules
        self.port.write(f"SOURce{self.sslot[1]}:PRESet")
        self.port.write(f"SENSe{self.mslot[1]}:PRESet")

    def deinitialize(self):
        pass

    def configure(self):
        # Configure source first: ranges & waveform
        self.set_ranging_source(self.range_source)
        # amplitude/offset
        self.set_amplitude(0)  # Safe starting value
        self.set_dark_mode()
        self.set_voltage_limits(self.vlim_low, self.vlim_high)
        # Source protection
        self.set_current_protection(self.current_protect)
        # Configure measure module
        self.set_range_measure(self.range_current)
        self.set_nplc()

    def poweron(self):
        # Start / enable source output
        self.set_output(True)

    def apply(self):
        """Only called if the sweep value changes: Sets a new value to the device."""
        self.set_amplitude(float(self.value))

    def read_result(self):
        # trigger read of measure module (READ for DC)
        self.port.write(f"READ:SENS{self.mslot[1]}:DC?")
        try:
            res = self.port.read()
            self.current = float(res)
        except KeyError:
            self.current = float('nan')

        # read applied voltage
        self.port.write(f"SOURce{self.sslot[1]}:VOLTage:LEVel:AMPLitude:PEAK?")
        try:
            self.volt_read = float(self.port.read())
        except (KeyError, TypeError):
            self.volt_read = float('nan')

    def call(self):
        # Return values in order defined by self.variables
        # DC or default single current reading + applied voltage
        return [self.volt_read, self.current]

    def poweroff(self):
        # turn off source
        self.set_output(False)

    # ---------------- Source (VS-10) wrapper functions ----------------
    def set_amplitude(self, amplitude: float):
        """Set source amplitude (peak)."""
        # check voltage limits
        if not (self.vlim_low <= amplitude <= self.vlim_high):
            raise ValueError("Voltage must be within the limits you set.")
        self.port.write(f"SOURce{self.sslot[1]}:VOLTage:LEVel:AMPLitude:PEAK {amplitude}")

    def set_ranging_source(self, range_set: float):
        """Set range mode and manual limits for the source."""
        if range_set == 0:  # 0 means Auto-range
            self.port.write(f"SOURce{self.sslot[1]}:VOLTage:RANGe:AUTO 1")
        else:
            self.port.write(f"SOURce{self.sslot[1]}:VOLTage:RANGe:AUTO 0")
            self.port.write(f"SOURce{self.sslot[1]}:VOLTage:RANGe:DC {range_set}")

    def set_dark_mode(self):
        self.port.write(f"SOURce{self.sslot[1]}:DMODe {'1' if self.dark else '0'}")

    def set_current_protection(self, level: float):
        """Set DC current protection level (SOURce#:CURRent:PROTection)."""
        if level <= 0:
            raise ValueError("Current protection level must be positive (in A).")
        self.current_protect = level
        self.port.write(f"SOURce{self.sslot[1]}:CURRent:PROTection {level}")

    def set_voltage_limits(self, low: float, high: float):
        """Set software high/low voltage output limits."""
        if not (-10.0 <= low < high <= 10.0):
            raise ValueError("Voltage limits must not exceed +-10 V "
                             "and the low limit needs be smaller than the high one.")
        self.port.write(f"SOURce{self.sslot[1]}:VOLTage:LIMit:LOW {self.vlim_low}")
        self.port.write(f"SOURce{self.sslot[1]}:VOLTage:LIMit:HIGH {self.vlim_high}")

    def set_output(self, enabled: bool):
        """Enable or disable the source output (SOURce#:STATe)."""
        self.port.write(f"SOURce{self.sslot[1]}:STATe {'1' if enabled else '0'}")

    # ---------------- Measure (CM-10) wrapper functions ----------------
    def set_range_measure(self, range_set):
        # measure_limit is in A
        if range_set == 0:
            self.port.write(f"SENSe{self.mslot[1]}:CURRent:RANGe:AUTO 1")
        else:
            self.port.write(f"SENSe{self.mslot[1]}:CURRent:RANGe:AUTO 0")
            self.port.write(f"SENSe{self.mslot[1]}:CURRent:RANGe {range_set}")

    def set_nplc(self):
        self.port.write(f"SENSe{self.mslot[1]}:NPLCycles {self.nplc}")

    def check_device(self):
        # Verify both modules are present and of the expected type
        model_s = self.port.query(f"SOURce{self.sslot[1]}:MODel?")
        model_m = self.port.query(f"SENSe{self.mslot[1]}:MODel?")
        if "VS-10" not in model_s:
            raise ValueError(f"Source on channel {self.sslot} is not a VS-10. Found: '{model_s}'")
        if '"CM-10"' not in model_m and "CM-10" not in model_m:
            raise ValueError(f"Measure on channel {self.mslot} is not a CM-10. Found: '{model_m}'")
