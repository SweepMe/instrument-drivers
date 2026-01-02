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
# * Module: LockIn
# * Instrument: LakeShore M81 CM-10

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!
import time

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

        # Current range limits for the CM-10 in A
        self.range_limits = {
            "Auto": 0.0,  # 0 stands for automatic
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

        # Low/High pass corner frequency options for the CM-10 in Hz
        self.cutoff_frequencies = {
            "None": "NONE",
            "10 Hz": "F10",
            "30 Hz": "F30",
            "100 Hz": "F100",
            "300 Hz": "F300",
            "1 kHz": "F1000",
            "3 kHz": "F3000",
            "10 kHz": "F10000",
        }

        # Rolloffs for high and low pass filters for the CM-10
        self.filter_rolloffs = {
            "6 dB/oct": 6
            , "12 dB/oct": 12}

        # Filter optimization modes for the CM-10
        self.filter_optimizations = {
            "None (Low and high pass input filters off)": "",
            "Lowest noise": "NOISe",
            "Highest reserve": "REServe",
        }

        # Measurement Parameters
        self.slot: str = ""
        self.port_string: str = ""
        self.range: float = 0.0
        self.use_bias: bool = False
        self.bias_voltage: float = 0.0
        self.current: float = float('nan')
        self.lia_ref: str = ""
        self.lia_lowpass: bool = False
        self.lia_harm: int = 1
        self.lia_tc: float = 0.1
        self.lia_rolloff: int = 6
        self.lia_avg_ref_cycles: int = 0
        self.lia_auto_phase: bool = True
        self.lia_ref_phase_shift: float = 0.0
        self.filter_on: bool = False
        self.filter_type: str = "NOISe"
        self.low_filter_cornerf: str = "NONE"
        self.low_filter_rolloff: int = 6
        self.high_filter_cornerf: str = "NONE"
        self.high_filter_rolloff: int = 6
        self.high_digital_filter: bool = True
        self.freq_range_threshold: float = 0.1
        self.darkmode: bool = False
        # Result parameters:
        self.x_lia: float = 0.0
        self.y_lia: float = 0.0
        self.r_lia: float = 0.0
        self.th_lia: float = 0.0
        self.freq_lia: float = 0.0
        self.dc: float = 0.0

    def set_GUIparameter(self):

        GUIparameter = {
            # "SweepMode": ["None", "Time constant in s"], # Currently no sweepmode implemented. Unclear which parameter to sweep.
            "Channel": ["M1", "M2", "M3"],
            "Source": ["S1", "S2", "S3", "Reference In"],
            "Sensitivity": list(self.range_limits.keys()),
            "TimeConstant": ["Traditional low pass output filter OFF", "0.0 (edit)"],
            #"WaitTimeConstants": ["Auto", "0 (edit)"],  #Not used because M81 returns "settled" boolean
            "Slope": ["6 dB/oct (output filter)", "12 dB/oct (output filter)",
                      "18 dB/oct (output filter)", "24 dB/oct (output filter)"],
            "Reserve": list(self.filter_optimizations.keys()),
            "Averaging reference cycles": 0,
            "HighPassFilter": ["None"] + [x + ", " + y for x in
                                          list(self.cutoff_frequencies.keys())[1:]
                                          for y in self.filter_rolloffs.keys()],
            "LowPassFilter": ["None"] + [x + ", " + y for x in
                                         reversed(list(self.cutoff_frequencies.keys())[1:])
                                         for y in self.filter_rolloffs.keys()],
            "Filter1": ["High pass digital filter ON", "High pass digital filter OFF"],
            "BiasVoltage": "",
            "Lock-In harmonic": 1,
            "Reference phase shift in degrees": ["Auto", "0.0 (edit)"],
            "Frequency range threshold factor of -3 dB": 0.1,
            "" : None,  # Empty line 0
            "Turn off LED": False,
        }

        return GUIparameter

    def get_GUIparameter(self, parameter):
        channel = parameter.get("Channel")
        if channel.strip().lower() in  ["m1", "m2", "m3"]:
            self.slot = channel[1]  # e.g. "1 for "M1"
        else:
            self.slot = ""  # default
        self.port_string = parameter.get("Port")
        self.range = self.range_limits[parameter.get("Sensitivity","Auto")]
        self.lia_ref = parameter.get("Source", "Reference In")
        self.lia_avg_ref_cycles = parameter.get("Averaging reference cycles", 0)

        # Traditional low pass output filter
        self.lia_tc = parameter.get("TimeConstant", "")
        try:
            self.lia_tc = float(self.lia_tc.split(" ")[0])
            self.lia_lowpass = True
            self.lia_rolloff = int(parameter.get("Slope", "0").split(" ")[0])
        except ValueError:
            self.lia_lowpass = False

        # Bias Voltage
        self.bias_voltage = parameter.get("BiasVoltage")
        if self.bias_voltage:
            self.use_bias = True
        else:
            self.use_bias = False

        # Output filters
        self.filter_type = self.filter_optimizations.get(parameter.get("Reserve"))
        if self.filter_type:
            self.filter_on = True
            low = parameter.get("LowPassFilter").split(",")
            self.low_filter_cornerf = self.cutoff_frequencies[low[0].strip()]
            if len(low) > 1:
                self.low_filter_rolloff = self.filter_rolloffs[low[1].strip()]
            high = parameter.get("HighPassFilter").split(",")
            self.high_filter_cornerf = self.cutoff_frequencies[high[0].strip()]
            if len(high) > 1:
                self.high_filter_rolloff = self.filter_rolloffs[high[1].strip()]
        else:
            self.filter_on = False

        # Digital filter
        self.high_digital_filter = (True if "ON" in parameter.get("Filter1") else False)

        # Reference wave
        self.lia_harm = parameter.get("Lock-In harmonic", 0)
        self.lia_ref_phase_shift = parameter.get("Reference phase shift in degrees", "Auto")

        self.freq_range_threshold = parameter.get("Frequency range threshold factor of -3 dB", 0.1)
        self.darkmode = parameter.get("Turn off LED", False)

        self.shortname = "CM-10 @ M" + self.slot

        self.variables = ["X", "Y", "Magnitude", "Phase", "Frequency", "Lock-In DC"]
        self.units = ["A", "A", "A", "°", "Hz", "A"]
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
        self.set_mode()
        self.set_range()
        self.set_lockin_settings()
        self.set_advanced_settings()
        # Bias voltage must be set after filter settings or a warning will appear on the touch panel.
        self.set_bias(self.use_bias, self.bias_voltage)

    """ the following functions are called for each measurement point """

    def measure(self):
        # Use Fetch to get X and Y (latest settled values).
        self.port.write(f"FETCh:MULTiple? "
                        f"MX,{self.slot},"
                        f"MY,{self.slot},"
                        f"MR,{self.slot},"
                        f"MTHeta,{self.slot},"
                        f"MRFRequency,{self.slot},"
                        f"MSETtling,{self.slot}"
                        )

    def read_result(self):
        t_start = time.monotonic()
        resp = self.port.read().split(",")
        if len(resp) == 6:  # Catch cases where results of both queries get mixed up.
            if not bool(int(resp[5])):  # If settling ist not True, the result is settled
                self.x_lia = self.lia_convert(resp[0])  # X
                self.y_lia = self.lia_convert(resp[1])  # Y
                self.r_lia = self.lia_convert(resp[2])  # Magnitude
                self.th_lia = self.lia_convert(resp[3])  # Phase
                self.freq_lia = self.lia_convert(resp[4])  # Frequency

                # Fetch DC separately, because it doesn't support FETCh:MULTIple
                self.port.write(f"FETCh:SENSe{self.slot}:LIA:DC?")
                dc_resp = self.port.read().split(",")
                if len(dc_resp) == 1:  # Catch cases where results of both queries get mixed up.
                    self.dc = self.lia_convert(dc_resp[0])
                else:
                    self.dc = float("nan")
            else:
                time.sleep(0.05)
                self.measure()
        else:
            self.read_result()
        if time.monotonic() - t_start > self.port_properties.get("timeout"):
            raise RuntimeError(f'Lock-in did not settle within timeout of {self.port_properties.get("timeout")} seconds.')


    def call(self):
        return [self.x_lia, self.y_lia, self.r_lia, self.th_lia, self.freq_lia, self.dc]


    """ wrapped functions """

    def set_mode(self):
        mode = "LIA"
        self.port.write(f'SENSe{self.slot}:MODE {mode}')

    def set_range(self):
        if self.range:
            if self.filter_on and self.filter_type == "REServe":
                if self.range == 0.1:  # CM-10 does not allow this combination. It would quietly reduce the range.
                    raise ValueError("100 mA range cannot be used with filter optimization 'highest reserve'.")
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe:AUTO 0')
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe {self.range}')
        else:
            self.port.write(f'SENSe{self.slot}:CURRent:RANGe:AUTO 1')

    def set_bias(self, enabled, voltage):
        self.port.write(f'SENSe{self.slot}:BIAS:STATe {"1" if enabled else "0"}')
        if enabled:
            try:
                self.bias_voltage = float(self.bias_voltage)
            except (ValueError, TypeError):
                raise ValueError("Provide float value for the bias voltage or leave empty for no voltage bias.")
            if voltage == 0:
                self.port.write(f'SENSe{self.slot}:BIAS:VOLTage 0')
            else:
                if self.filter_on and self.filter_type == "NOISe":
                    raise ValueError("Bias voltage > 0 cannot be used with 'Lowest noise' filter optimization.")
                self.port.write(f'SENSe{self.slot}:BIAS:VOLTage {voltage}')


    def check_device(self):
        model = self.port.query(f'SENSe{self.slot}:MODel?')
        if not "CM-10" in model:
            raise ValueError(
                f"Device connected on channel M{self.slot} does not match this driver. "
                f"Found: '{model}'"
            )

    def set_lockin_settings(self):
        """Wrapper function to set configurations specific to Lock-In Amplifier (LIA) mode."""
        # Reference source
        if not self.lia_ref in ["S1", "S2", "S3"]:
            if self.lia_ref.lower().startswith("reference"):
                self.lia_ref = "RIN"  # External Reference Source
            else:
                raise ValueError(f"No valid reference source selected: {self.lia_ref}.")
        self.port.write(f"SENSe{self.slot}:LIA:RSOurce {self.lia_ref}")

        # Reference harmonic
        try:
            self.lia_harm = int(self.lia_harm)
        except(ValueError, TypeError):
            raise ValueError("Please enter a valid positive integer value for the reference harmonic.")
        if self.lia_harm < 1:
            raise ValueError("Lock-In harmonic must be >= 1")
        self.port.write(f"SENSe{self.slot}:LIA:DHARmonic {self.lia_harm}")

        # Set PSD averaging filter
        try:
            self.lia_avg_ref_cycles = int(self.lia_avg_ref_cycles)
        except (ValueError, TypeError):
            raise ValueError("Please enter an integer number of averaging reference cycles. "
                             "'0' disables the PSD output filter.")
        if self.lia_avg_ref_cycles == 0:
            self.port.write(f'SENSe{self.slot}:LIA:AVERage 0') #Disable averaging filter
        else:
            if not (1000000 >= self.lia_avg_ref_cycles >= 1):
                raise ValueError("Number of reference cycles must be >= 1 and <= 1,000,000.")
            self.port.write(f'SENSe{self.slot}:LIA:AVERage 1')  # Disable averaging filter
            self.port.write(f"SENSe{self.slot}:LIA:REFerence:CYCLes {self.lia_avg_ref_cycles}")

        # Time constant and rolloff for traditional lowpass filter
        # Enable/Disable Lowpass filter
        self.port.write(f'SENSe{self.slot}:LIA:LPASs {"1" if self.lia_lowpass else "0"}')
        if self.lia_lowpass:
            if not (10000 >= self.lia_tc >= 0.0001):
                raise ValueError("Lock-In time constant must be >= 0.0001 s and <= 10,000 s.")
            self.port.write(f"SENSe{self.slot}:LIA:TIMEconstant {self.lia_tc}")
            self.port.write(f"SENSe{self.slot}:LIA:ROLLoff R{self.lia_rolloff}")
        # Phase shift to lock-in reference source
        if self.lia_ref_phase_shift == "Auto":
            self.port.write(f"SENSe{self.slot}:LIA:DPHase:AUTO")
        else:
            try:
                self.lia_ref_phase_shift = float(self.lia_ref_phase_shift)
                if not (360 >= self.lia_ref_phase_shift >= -360):
                    raise ValueError("Phase shift given as a float that is out of range (+-360°).")
            except (ValueError, TypeError) as e:
                raise ValueError('Reference phase shift must be a float between -360 and +360 degrees or "Auto".') \
                    from e
            self.port.write(f"SENSe{self.slot}:LIA:DPHase {self.lia_ref_phase_shift}")

    def set_advanced_settings(self):
        # Filters
        if self.filter_on:
            self.set_filters()
        else:
            self.port.write(f'SENSe{self.slot}:FILTer:STATe 0')
        self.port.write(f'SENSe{self.slot}:DMODe {"1" if self.darkmode else "0"}')
        self.port.write(f'SENSe{self.slot}:DIGital:FILTer:HPASs {"1" if self.high_digital_filter else "0"}')
        # Threshold
        try:
            self.freq_range_threshold = float(self.freq_range_threshold)
            if not 0.0 <= self.freq_range_threshold <= 3.0:
                raise ValueError("Frequency range threshold is not within range (0.0 to 3.0)."
                                 "Threshold value is normalized to the -3 dB bandwith of the range.")
        except(ValueError, TypeError) as e:
            raise ValueError("Please enter correct value for frequency range threshold.") from e
        self.port.write(f'SENSe{self.slot}:FRTHreshold {self.freq_range_threshold}')

    def set_filters(self):
        self.port.write(f'SENSe{self.slot}:FILTer:STATe 1')
        self.port.write(f'SENSe{self.slot}:FILTer:OPTimization {self.filter_type}')
        self.port.write(f'SENSe{self.slot}:FILTer:LPASs:FREQuency {self.low_filter_cornerf}')
        self.port.write(f'SENSe{self.slot}:FILTer:LPASs:ATTenuation R{self.low_filter_rolloff}')
        self.port.write(f'SENSe{self.slot}:FILTer:HPASs:FREQuency {self.high_filter_cornerf}')
        self.port.write(f'SENSe{self.slot}:FILTer:HPASs:ATTenuation R{self.high_filter_rolloff}')

    @staticmethod
    def lia_convert(value_str: str) -> float:
        """
        Convert M81 LIA sentinel values into Python float equivalents.

        M81 special values:
        - +9.90e37 : measurement overload
        - +9.91e37 : PLL unlocked / invalid measurement
        """
        try:
            val = float(value_str)
        except ValueError:
            return float('nan')

        # Special value M81: Overload → +inf
        if val == 9.90e37:
            return float('inf')

        # Special value M81: PLL unlocked → NaN
        if val == 9.91e37:
            return float('nan')

        return val
