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
# Type: Lockin
# Device: 7265DSP

import time
import numpy as np
from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """
    Driver for Ametek Signal Recovery DSP 7265 Lock-in Amplifier
    
    Provides control and communication with the 7265 Lock-in amplifier over COM or GPIB interfaces.
    """

    description = """
    <p><strong>Ametek Signal Recovery DSP 7265</strong><br /> <br /> Notes:</p>
    <ul>
    <li>Availability of AC gain range might depend on selected sensitivity value</li>
    <li>AC gain will not work correctly with Auto sensitivity.</li>
    <li>Time constant option "Auto time - 10 periods" means that the time constant is automatically set to 10 periods of
     the signal. You can change the number in front of periods to another value.</li>
    </ul>
    """

    def __init__(self):
        super().__init__()
        
        self.shortname = "7265DSP"

        # Port configuration
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        # port_identifications isn't working but kept for future implementation
        # self.port_identifications = ['Ametek,7280']

        self.port_properties = { 
            "EOL": "\r\n",
            "timeout": 2,
            "baudrate": 9600,
        }

        # Command dictionaries for translating GUI selections to device commands
        self.commands = OrderedDict([
            ("Float", "FLOAT 1"),
            ("Ground", "FLOAT 0"),
        ])

        self.source_commands = OrderedDict([
            ("Internal", "IE 0"),
            ("External TTL Rear", "IE 1"),
            ("External Analog Front", "IE 2"),
        ])
                            
        self.input_commands = OrderedDict([
            ("Current B High bandwidth, Front", "IMODE1; REF FRONT"),
            ("Current B Low noise, Front", "IMODE2; REF FRONT"),
            ("Voltage A, Front", "IMODE0; VMODE 1; REF FRONT"),
            ("Voltage -B, Front", "IMODE0; VMODE 2; REF FRONT"),
            ("Voltage A-B, Front", "IMODE0; VMODE 3; REF FRONT"),
            ("Current B High bandwidth, Rear", "IMODE1; REF REAR"),
            ("Current B Low noise, Rear", "IMODE2; REF REAR"),
            ("Voltage A, Rear", "IMODE0; VMODE 1; REF REAR"),
            ("Voltage -B, Rear", "IMODE0; VMODE 2; REF REAR"),
            ("Voltage A-B, Rear", "IMODE0; VMODE 3; REF REAR"),
        ])
                        
        self.gains = OrderedDict([
            ("Auto gain", "AUTOMATIC 1"),
            ("0 dB", "AUTOMATIC 0; ACGAIN 0"),
            ("10 dB", "AUTOMATIC 0; ACGAIN 1"),
            ("20 dB", "AUTOMATIC 0; ACGAIN 2"),
            ("30 dB", "AUTOMATIC 0; ACGAIN 3"),
            ("40 dB", "AUTOMATIC 0; ACGAIN 4"),
            ("50 dB", "AUTOMATIC 0; ACGAIN 5"),
            ("60 dB", "AUTOMATIC 0; ACGAIN 6"),
            ("70 dB", "AUTOMATIC 0; ACGAIN 7"),
            ("80 dB", "AUTOMATIC 0; ACGAIN 8"),
            ("90 dB", "AUTOMATIC 0; ACGAIN 9"),
        ])
        
        # Create reverse mapping for gains (command value -> dB value)                       
        self.inv_gains = {
            int(v.split()[-1]): int(k[:-3]) 
            for k, v in self.gains.items() 
            if v.startswith("AUTOMATIC 0; ACGAIN")
        }
                               
        self.timeconstants = OrderedDict([
            ("10µ", "TC 0"),
            ("20µ", "TC 1"),
            ("40µ", "TC 2"),
            ("80µ", "TC 3"),
            ("160µ", "TC 4"),
            ("320µ", "TC 5"),
            ("640µ", "TC 6"),
            ("5m", "TC 7"),
            ("10m", "TC 8"),
            ("20m", "TC 9"),
            ("50m", "TC 10"),
            ("100m", "TC 11"),
            ("200m", "TC 12"),
            ("500m", "TC 13"),
            ("1", "TC 14"),
            ("2", "TC 15"),
            ("5", "TC 16"),
            ("10", "TC 17"),
            ("20", "TC 18"),
            ("50", "TC 19"),
            ("100", "TC 20"),
            ("200", "TC 21"),
            ("500", "TC 22"),
            ("1k", "TC 23"),
            ("2k", "TC 24"),
            ("5k", "TC 25"),
            ("10k", "TC 26"),
            ("20k", "TC 27"),
            ("50k", "TC 28"),
            ("100k", "TC 29"),
        ])

        # Pre-calculate floating point values for time constants
        self.timeconstants_numbers = [self._value_to_float(x) for x in self.timeconstants]

        # Sensitivity settings for different input modes
        self.sensitivities_voltages = OrderedDict([
            ("2 nV", "SEN 1"),
            ("5 nV", "SEN 2"),
            ("10 nV", "SEN 3"),
            ("20 nV", "SEN 4"),
            ("50 nV", "SEN 5"),
            ("100 nV", "SEN 6"),
            ("200 nV", "SEN 7"),
            ("500 nV", "SEN 8"),
            ("1 µV", "SEN 9"),
            ("2 µV", "SEN 10"),
            ("5 µV", "SEN 11"),
            ("10 µV", "SEN 12"),
            ("20 µV", "SEN 13"),
            ("50 µV", "SEN 14"),
            ("100 µV", "SEN 15"),
            ("200 µV", "SEN 16"),
            ("500 µV", "SEN 17"),
            ("1 mV", "SEN 18"),
            ("2 mV", "SEN 19"),
            ("5 mV", "SEN 20"),
            ("10 mV", "SEN 21"),
            ("20 mV", "SEN 22"),
            ("50 mV", "SEN 23"),
            ("100 mV", "SEN 24"),
            ("200 mV", "SEN 25"),
            ("500 mV", "SEN 26"),
            ("1 V", "SEN 27")
        ])

        self.sensitivities_currents_high_bandwidth = OrderedDict([
            ("2 fA", "SEN 1"),
            ("5 fA", "SEN 2"),
            ("10 fA", "SEN 3"),
            ("20 fA", "SEN 4"),
            ("50 fA", "SEN 5"),
            ("100 fA", "SEN 6"),
            ("200 fA", "SEN 7"),
            ("500 fA", "SEN 8"),
            ("1 pA", "SEN 9"),
            ("2 pA", "SEN 10"),
            ("5 pA", "SEN 11"),
            ("10 pA", "SEN 12"),
            ("20 pA", "SEN 13"),
            ("50 pA", "SEN 14"),
            ("100 pA", "SEN 15"),
            ("200 pA", "SEN 16"),
            ("500 pA", "SEN 17"),
            ("1 nA", "SEN 18"),
            ("2 nA", "SEN 19"),
            ("5 nA", "SEN 20"),
            ("10 nA", "SEN 21"),
            ("20 nA", "SEN 22"),
            ("50 nA", "SEN 23"),
            ("100 nA", "SEN 24"),
            ("200 nA", "SEN 25"),
            ("500 nA", "SEN 26"),
            ("1 µA", "SEN 27")
        ])

        self.sensitivities_currents_low_noise = OrderedDict([
            ("2 fA", "SEN 7"),
            ("5 fA", "SEN 8"),
            ("10 fA", "SEN 9"),
            ("20 fA", "SEN 10"),
            ("50 fA", "SEN 11"),
            ("100 fA", "SEN 12"),
            ("200 fA", "SEN 13"),
            ("500 fA", "SEN 14"),
            ("1 pA", "SEN 15"),
            ("2 pA", "SEN 16"),
            ("5 pA", "SEN 17"),
            ("10 pA", "SEN 18"),
            ("20 pA", "SEN 19"),
            ("50 pA", "SEN 20"),
            ("100 pA", "SEN 21"),
            ("200 pA", "SEN 22"),
            ("500 pA", "SEN 23"),
            ("1 nA", "SEN 24"),
            ("2 nA", "SEN 25"),
            ("5 nA", "SEN 26"),
            ("10 nA", "SEN 27"),
        ])

        self.slopes = OrderedDict([
            ("6 dB/octave",  "SLOPE 0"),
            ("12 dB/octave", "SLOPE 1"),
            ("18 dB/octave", "SLOPE 2"),
            ("24 dB/octave", "SLOPE 3"),
        ])
                        
        self.filter1_commands = OrderedDict([
            ("Off",  "LF 0 0"),
            ("50 Hz notch filter", "LF 1 1"),
            ("60 Hz notch filter", "LF 1 0"),
            ("100 Hz notch filter", "LF 2 1"),
            ("120 Hz notch filter", "LF 2 0"),
            ("50 Hz and 100 Hz notch filter", "LF 3 1"),
            ("60 Hz and 120 Hz notch filter", "LF 3 0"),
        ])

        self.filter2_commands = OrderedDict([
            ("Sync filter off", "SYNC 0"),
            ("Sync filter on", "SYNC 1"),
        ])
        
        self.coupling_commands = OrderedDict([
            ("Fast", "CP 0"),
            ("Slow", "CP 1"),
        ])
        
        # Initialize instance variables with defaults
        self.sweepmode = "None"
        self.source = "Internal"
        self.oscillator_frequency = 1000
        self.oscillator_amplitude = 0.1
        self.input = "Voltage A, Front"
        self.coupling = "Fast"
        self.slope = "12 dB/octave"
        self.ground = "Ground"
        self.sensitivity = "Auto sensitivity"
        self.filter1 = "Off"
        self.filter2 = "Sync filter off"
        self.gain = "Auto gain"
        self.time_constant = "100m"
        self.wait_time_constants = 4.0
        self.factor_auto_time_constant = 10.0
        
        # Results storage
        self.frq = 0.0
        self.r = 0.0 
        self.phi = 0.0
        self.sen = 0.0
        self.nhz = 0.0
        self.acg = 0
        self.acg_dB = 0
        self.tc = 0.0
        self.time_ref = 0.0

    def set_GUIparameter(self) -> Dict[str, Any]:
        """
        Define the GUI parameters for this device.
        
        Returns:
            Dictionary with all GUI parameters and their possible values.
        """
        
        gui_parameter = {
            "SweepMode": ["None", "Oscillator frequency in Hz"],
            "Source": list(self.source_commands.keys()),
            "OscillatorFrequency": 1000,
            "OscillatorAmplitude": 0.1,
            "Input": list(self.input_commands.keys()),
            "Sensitivity": ["Auto sensitivity"] +
                           list(self.sensitivities_voltages.keys()) +
                           list(self.sensitivities_currents_high_bandwidth.keys()),
            "Filter1": list(self.filter1_commands.keys()),
            "Filter2": list(self.filter2_commands.keys()),
            "TimeConstant": list(self.timeconstants.keys()) + ["Auto time - 10 periods"],
            "Gain": list(self.gains.keys()),
            "Slope": list(self.slopes.keys()),
            "Coupling": list(self.coupling_commands.keys()),
            "Ground": ["Ground", "Float"],
            "WaitTimeConstants": 4.0,
        }
                        
        return gui_parameter
        
    def get_GUIparameter(self, parameter: Dict[str, Any]) -> None:
        """
        Apply the GUI parameters and configure device variables.
        
        Args:
            parameter: Dictionary containing the GUI parameters.
        
        Raises:
            Exception: If required parameters are missing (old module version).
        """

        if "OscillatorAmplitude" not in parameter:
            raise Exception("Please update to the latest LockIn module to use the Signal Recovery 7265 driver.")

        self.sweepmode = parameter["SweepMode"]
        self.source = parameter["Source"]
        self.oscillator_frequency = parameter["OscillatorFrequency"]
        self.oscillator_amplitude = parameter["OscillatorAmplitude"]
        self.input = parameter["Input"]
        self.coupling = parameter["Coupling"]
        self.slope = parameter["Slope"]
        self.ground = parameter["Ground"]
        self.sensitivity = parameter["Sensitivity"]
        self.filter1 = parameter["Filter1"]
        self.filter2 = parameter["Filter2"]
        self.gain = parameter["Gain"]
        self.time_constant = parameter["TimeConstant"]
        self.wait_time_constants = float(parameter["WaitTimeConstants"])

        # Set up result variables based on input type
        self.variables = ["Magnitude", "Phase", "Frequency", "Sensitivity", "Noise density", "AC Gain", "Time constant"]

        if self.input.startswith("Voltage"):
            self.units = ["V", "deg", "Hz", "V", "V/sqrt(Hz)", "dB", "s"]
        elif self.input.startswith("Current"):
            self.units = ["A", "deg", "Hz", "A", "A/sqrt(Hz)", "dB", "s"]

        # All variables are plottable and saveable
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    def initialize(self) -> None:
        """
        Initialize the device with default settings.
        
        Raises:
            Exception: If sweep mode is incompatible with source setting.
        """
        # Check for valid configuration
        if self.source != "Internal" and self.sweepmode == "Oscillator frequency in Hz":
            raise Exception("To sweep the oscillator frequency, the reference must be 'Internal'. "
                            "Please change and try again.")

        # Put device in remote mode, turn on display, and restore default settings
        self.set_remote(True)
        self.set_display_light(True)
        self.port.write("ADF 1")  # restore default settings
        self.wait_for_complete()

    def deinitialize(self) -> None:
        """Return control to the front panel."""
        self.set_remote(False)

    def configure(self) -> None:
        """Configure all device settings based on GUI parameters."""
        # Source adjustment
        self.port.write(self.source_commands[self.source])
        self.wait_for_complete()

        # Input adjustment
        self.port.write(self.input_commands[self.input])
        self.wait_for_complete()

        # Slope adjustment
        self.port.write(self.slopes[self.slope])
        self.wait_for_complete()

        # Ground adjustment
        self.port.write(self.commands[self.ground])
        self.wait_for_complete()

        # Coupling adjustment
        self.port.write(self.coupling_commands[self.coupling])
        self.wait_for_complete()

        # Set notch filter
        self.port.write(self.filter1_commands[self.filter1])
        self.wait_for_complete()

        # Set sync filter
        self.port.write(self.filter2_commands[self.filter2])
        self.wait_for_complete()

        # Gain adjustment
        self.port.write(self.gains[self.gain])
        self.wait_for_complete()

        # Sensitivity adjustment
        if self.sensitivity != "Auto sensitivity":
            self._set_sensitivity_by_input_type()

        # Time constant adjustment
        if not self.time_constant.startswith("Auto time"):
            self._set_time_constant()
        else:
            self._parse_auto_time_constant()
       
        # Configure oscillator if using internal source
        if self.source == "Internal":
            if self.sweepmode != "Oscillator frequency in Hz":
                self.set_oscillator_frequency(self.oscillator_frequency)
            self.set_oscillator_amplitude(self.oscillator_amplitude)

        # Phase re-adjustment
        self.adjust_phase()

    def _set_sensitivity_by_input_type(self) -> None:
        """Set sensitivity based on the current input type."""
        if "Voltage" in self.input:
            self.port.write(self.sensitivities_voltages[self.sensitivity])
        elif "Current B High bandwidth" in self.input:
            self.port.write(self.sensitivities_currents_high_bandwidth[self.sensitivity])
        elif "Current B Low noise" in self.input:
            self.port.write(self.sensitivities_currents_low_noise[self.sensitivity])
        self.wait_for_complete()

    def _set_time_constant(self) -> None:
        """Set the time constant from the current setting."""
        if self.time_constant in self.timeconstants:
            new_tc_key = self.time_constant
        else:
            new_tc_key = self._find_best_time_constant_key(self.time_constant)
        self.port.write(self.timeconstants[new_tc_key])
        self.wait_for_complete()
        
    def _parse_auto_time_constant(self) -> None:
        """Parse the auto time constant setting."""
        factor_periods_str = self.time_constant.split("-")[1].strip()
        # Extract numeric value from string like "10 periods"
        factor_value = ''.join(c for c in factor_periods_str if c.isdigit() or c == '.')
        self.factor_auto_time_constant = float(factor_value)

    def reconfigure(self, parameters: Dict[str, Any], keys: List[str]) -> None:
        """
        Reconfigure the device with updated parameters.
        
        Args:
            parameters: Dictionary with updated parameters.
            keys: List of keys for parameters that have changed.
        """
        if "TimeConstant" in keys:
            self.time_constant = parameters["TimeConstant"]
            if not self.time_constant.startswith("Auto time"):
                self._set_time_constant()
            else:
                self._parse_auto_time_constant()

    def apply(self) -> None:
        """Apply the current sweep value."""
        if self.sweepmode == "Oscillator frequency in Hz":
            self.set_oscillator_frequency(self.value)

    def reach(self) -> None:
        """Called when a new sweep value is reached."""
        pass
   
    def adapt(self) -> None:
        """Adapt device settings based on current conditions."""
        # Auto-adjust time constant based on frequency if needed
        if self.time_constant.startswith("Auto time"):
            self.auto_time_constant(self.factor_auto_time_constant)

        # Start auto-sensitivity if enabled
        if self.sensitivity == "Auto sensitivity":
            self.start_autosensitivity()

    def adapt_ready(self) -> None:
        """Called when adaptation is complete."""
        if self.sensitivity == "Auto sensitivity":
            self.wait_for_complete()

        self.time_ref = time.time()
            
    def trigger_ready(self) -> None:
        """
        Wait for device to stabilize before measurement.
        
        Ensures that at least wait_time_constants * time_constant has passed
        since the last setting change.
        """
        self.tc = self.get_time_constant()

        # Wait for device to stabilize
        delta_time = (self.wait_time_constants * self.tc) - (time.time() - self.time_ref)
        if delta_time > 0.0:
            time.sleep(delta_time)

    def measure(self) -> None:
        """Prepare for measurement."""
        pass

    def request_result(self) -> None:
        """Request measurement results from the device."""
        pass

    def read_result(self) -> None:
        """Read and store measurement results from the device."""
        self.frq = self.get_frequency()
        self.r = self.get_magnitude()
        self.phi = self.get_phase()
        self.sen = self.get_sensitivity()

        # Model 7265 can only measure noise density until 60 kHz
        if self.frq <= 60000:
            self.nhz = self.get_noise_density()
        else:
            self.nhz = float('nan')

        self.acg = self.get_acgain()
        self.acg_dB = self.inv_gains.get(self.acg, 0)  # Safe access with default

    def call(self) -> List[float]:
        """
        Return current measurement results.
        
        Returns:
            List of measurement values in order of self.variables.
        """
        return [self.r, self.phi, self.frq, self.sen, self.nhz, self.acg_dB, self.tc]

    # Helper methods
        
    def _value_to_float(self, value: Union[str, float]) -> float:
        """
        Convert a value with units and prefixes to a float.
        
        Args:
            value: Value as string with unit prefixes or as float.
            
        Returns:
            Floating point representation of the value.
        """
        # Define unit prefix conversions
        chars = OrderedDict([
            ("V", ""),
            ("s", ""),
            (" ", ""),
            ("n", "e-9"),
            ("µ", "e-6"),
            ("m", "e-3"),
            ("k", "e3"),
            ("M", "e6"),
            ("G", "e9"),
        ])

        if isinstance(value, str):
            # Replace units and prefixes with their numerical representation
            result = value
            for char, replacement in chars.items():
                result = result.replace(char, replacement)
            
            # Convert to float
            try:
                return float(result)
            except ValueError:
                # In case of conversion error, return 0.0 or raise exception
                return 0.0
        
        return float(value)

    def _find_best_time_constant_key(self, time_constant: Union[str, float]) -> str:
        """
        Find the closest available time constant.
        
        Args:
            time_constant: Desired time constant value.
            
        Returns:
            Key of the closest available time constant.
        """
        time_constant_float = self._value_to_float(time_constant)

        # Count how many time constants are smaller than requested value
        tc_index = sum(np.array(self.timeconstants_numbers) < time_constant_float)

        # Get the corresponding key or use maximum value if out of range
        if tc_index < len(self.timeconstants):
            return list(self.timeconstants.keys())[tc_index]
        else:
            return "100k"  # Maximum available time constant

    def auto_time_constant(self, factor: float = 10.0) -> None:
        """
        Set time constant based on signal frequency.
        
        Args:
            factor: Multiplier for time constant relative to signal period.
        """
        try:
            frq = self.get_frequency()
            if frq > 0:  # Avoid division by zero
                period = 1.0 / frq
                new_tc = factor * period
                new_tc_key = self._find_best_time_constant_key(new_tc)
                
                # Send command to set time constant
                self.port.write(self.timeconstants[new_tc_key])
                self.wait_for_complete()
        except Exception as e:
            print(f"Error in auto_time_constant: {e}")

    def wait_for_complete(self, timeout: float = 20.0) -> None:
        """
        Wait for command completion by monitoring the status byte.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Raises:
            Exception: If operation times out.
        """
        starttime = time.time()
        while True:
            try:
                # Direct GPIB status byte read
                stb = self.port.port.read_stb()
                if stb & 1 == 1:  # First byte indicates command processed
                    break
            except AttributeError:
                # Fall back if read_stb not available
                self.port.write("ST")
                try:
                    stb = int(self.port.read())
                    if stb & 1 == 1:
                        break
                except (ValueError, TypeError):
                    pass
                
            # Check for timeout
            if time.time() - starttime > timeout:
                raise Exception("Timeout during wait for completion.")
                
            # Sleep to avoid CPU overuse
            time.sleep(0.01)

    # Device-specific command methods

    def get_identification(self) -> str:
        """Get device identification string."""
        self.port.write("ID")
        return self.port.read()

    def get_version(self) -> str:
        """Get device firmware version."""
        self.port.write("VER")
        return self.port.read()

    def get_status_byte(self) -> int:
        """
        Get device status byte.
        
        Returns:
            Integer status byte.
        """
        self.port.write("ST")
        try:
            return int(self.port.read())
        except (ValueError, TypeError):
            return 0

    def get_overload_byte(self) -> int:
        """
        Get device overload status.
        
        Returns:
            Integer overload byte.
        """
        self.port.write("N")
        try:
            return int(self.port.read())
        except (ValueError, TypeError):
            return 0

    def set_delimiter(self, value: int) -> None:
        """
        Set the command delimiter.
        
        Args:
            value: Delimiter value.
        """
        self.port.write(f"DD {int(value)}")
        self.wait_for_complete()

    def set_remote(self, state: bool = True) -> None:
        """
        Enable or disable remote control.
        
        Args:
            state: True to enable remote control, False to disable.
        """
        self.port.write(f"REMOTE {1 if state else 0}")
        self.wait_for_complete()

    def set_display_light(self, state: bool = True) -> None:
        """
        Set display backlight state.
        
        Args:
            state: True to enable backlight, False to disable.
        """
        self.port.write(f"LTS {1 if state else 0}")
        self.wait_for_complete()

    def get_acgain(self) -> int:
        """
        Get current AC gain setting.
        
        Returns:
            AC gain value.
        """
        self.port.write("ACGAIN")
        try:
            return int(self.port.read())
        except (ValueError, TypeError):
            return 0

    def set_line_frequency_filter(self, n1: int, n2: int) -> None:
        """
        Set line frequency filter settings.
        
        Args:
            n1: Filter mode (0=Off, 1=50/60Hz, 2=100/120Hz, 3=Both)
            n2: Filter frequency (0=60Hz/120Hz, 1=50Hz/100Hz)
        """
        self.port.write(f"LF {int(n1)} {int(n2)}")
        self.wait_for_complete()

    def set_oscillator_amplitude(self, value: float) -> None:
        """
        Set oscillator amplitude.
        
        Args:
            value: Amplitude in volts.
        """
        # Convert to mV (value sent in mV)
        amplitude_mV = int(float(value) * 1000)
        self.port.write(f"OA. {amplitude_mV}")
        self.wait_for_complete()

    def set_oscillator_frequency(self, frequency: float) -> None:
        """
        Set oscillator frequency.
        
        Args:
            frequency: Frequency in Hz.
        """
        self.port.write(f"OF. {frequency:.6E}")
        self.wait_for_complete()

    def start_autosensitivity(self) -> None:
        """Start auto-sensitivity adjustment."""
        self.port.write("AS")

    def adjust_phase(self) -> None:
        """Auto-adjust phase to get X maximum, Y minimum."""
        self.port.write("AQN")
        self.wait_for_complete()

    def get_time_constant(self) -> float:
        """
        Get current time constant.
        
        Returns:
            Time constant in seconds.
        """
        self.port.write("TC.")
        try:
            return float(self.port.read())
        except (ValueError, TypeError):
            return 0.0

    def set_time_constant(self, value: int) -> None:
        """
        Set time constant by index.
        
        Args:
            value: Time constant index (0-29).
        """
        self.port.write(f"TC {int(value)}")
        self.wait_for_complete()

    def get_magnitude(self) -> float:
        self.port.write("MAG.")
        return float(self.port.read())

    def get_phase(self):
        self.port.write("PHA.")
        return float(self.port.read())

    def get_frequency(self):
        self.port.write("FRQ.")
        return float(self.port.read())

    def get_sensitivity(self):
        self.port.write("SEN.")
        return float(self.port.read())

    def set_sensitivity(self, value):
        self.port.write("SEN %i" % int(value))
        self.wait_for_complete()

    def get_noise_density(self):
        """
        The noise density can only be measured until 60 kHz according to the manual. At higher frequencies this
        function does not work and will lead to an error or a timeout.

        Returns:
            flaot: noise density in V/sqrt(Hz) or A/sqrt(Hz)
        """
        self.port.write("NHZ.")
        return float(self.port.read())

    def get_time_constant(self):
        """
        Returns:
            float: time constant in s
        """
        self.port.write("TC.")
        return float(self.port.read())
