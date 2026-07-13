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
# * Instrument: LakeShore M81 VM-10

from __future__ import annotations

import time
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):
    """SweepMe! LockIn driver for the VM-10 voltage measure module of the LakeShore M81-SSM.

    The VM-10 is operated in lock-in (LIA) mode and performs phase-sensitive voltage
    detection at the frequency of the selected reference source (any M81 source channel
    or the external reference input). The driver returns X, Y, magnitude R, phase theta,
    the reference frequency, and the lock-in DC component.
    """

    def __init__(self) -> None:
        """Initialize driver parameters and option-to-command dictionaries."""
        EmptyDevice.__init__(self)

        self.shortname = "M81 VM-10"

        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP", "SOCKET"]

        self.port_properties = {
            "baudrate": 921600,  # fixed baud rate of the M81 USB serial interface
            "EOL": "\n",
            "timeout": 15,
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "SOCKET_EOLwrite": "\n",
            "SOCKET_EOLread": "\n",
        }

        # Voltage ranges of the VM-10 in V; 0.0 stands for autorange
        self.voltage_ranges: dict[str, float] = {
            "Auto": 0.0,
            "10 V": 10.0,
            "1 V": 1.0,
            "100 mV": 0.1,
            "10 mV": 0.01,
        }

        # Input configurations of the VM-10
        self.input_configurations: dict[str, str] = {
            "A-B": "AB",
            "A": "A",
            "Ground": "GROund",
        }

        # Corner frequency options for the analog input high/low pass filters
        self.cutoff_frequencies: dict[str, str] = {
            "None": "NONE",
            "10 Hz": "F10",
            "30 Hz": "F30",
            "100 Hz": "F100",
            "300 Hz": "F300",
            "1 kHz": "F1000",
            "3 kHz": "F3000",
            "10 kHz": "F10000",
        }

        # Rolloff options for the analog input high/low pass filters
        self.filter_rolloffs: dict[str, int] = {"6 dB/oct": 6, "12 dB/oct": 12}

        # Analog input filter optimization modes ('Reserve' in the SweepMe! LockIn GUI)
        self.filter_optimizations: dict[str, str] = {
            "None (analog input filter off)": "",
            "Lowest noise": "NOISe",
            "Highest reserve": "REServe",
        }

        # Measurement parameters set via the GUI
        self.slot: str = ""  # measure channel number "1", "2", or "3"
        self.port_string: str = ""
        self.sweep_mode: str = "None"
        self.range: float = 0.0  # 0.0 = autorange
        self.input_config: str = "AB"
        self.coupling: str = "DC"
        self.lia_ref: str = "S1"
        self.lia_harmonic: int = 1
        self.lia_lowpass: bool = True  # traditional IIR low pass output filter on/off
        self.lia_tc: float = 0.1  # time constant of the IIR output filter in s
        self.lia_rolloff: int = 12  # rolloff of the IIR output filter in dB/oct
        self.lia_avg_ref_cycles: int = 0  # 0 disables the FIR averaging output filter
        self.lia_phase_mode: str = "Auto"  # "Auto", "As is", or a float as string
        self.lia_phase_shift: float = 0.0
        self.stored_phase_shift: float = 0.0  # phase read back before PRESet for 'As is'
        self.wait_time_constants: str = "Auto"
        self.wait_time: float = 0.0  # additional settle wait per point in s
        self.filter_on: bool = False
        self.filter_optimization: str = "NOISe"
        self.lowpass_corner: str = "NONE"
        self.lowpass_rolloff: int = 6
        self.highpass_corner: str = "NONE"
        self.highpass_rolloff: int = 6
        self.digital_highpass: bool = True
        self.freq_range_threshold: float = 0.1
        self.darkmode: bool = False

        # Result parameters
        self.x_lia: float = float("nan")
        self.y_lia: float = float("nan")
        self.r_lia: float = float("nan")
        self.theta_lia: float = float("nan")
        self.freq_lia: float = float("nan")
        self.dc_lia: float = float("nan")

        self.variables = ["X", "Y", "Magnitude", "Phase", "Frequency", "Lock-In DC"]
        self.units = ["V", "V", "V", "°", "Hz", "V"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return a dictionary of GUI fields and defaults depending on the current parameters."""
        gui_parameters: dict[str, Any] = {
            "SweepMode": ["None", "Sensitivity in V", "Time constant in s"],
            "Channel": ["M1", "M2", "M3"],  # physical measure channels of the M81
            "Source": ["S1", "S2", "S3", "Reference In"],  # lock-in reference source
            "Input": list(self.input_configurations.keys()),
            "Coupling": ["DC", "AC"],
            "Sensitivity": list(self.voltage_ranges.keys()),
            "TimeConstant": ["0.1 (edit)", "Traditional low pass output filter OFF"],
            "Slope": [
                "6 dB/oct (output filter)",
                "12 dB/oct (output filter)",
                "18 dB/oct (output filter)",
                "24 dB/oct (output filter)",
            ],
            "WaitTimeConstants": "Auto",
            "Averaging reference cycles": 0,
            "Reserve": list(self.filter_optimizations.keys()),
        }

        # The analog input high/low pass filters are only active
        # if a filter optimization ('Reserve') is selected.
        reserve = parameters.get("Reserve", "")
        if reserve and self.filter_optimizations.get(reserve, ""):
            gui_parameters["HighPassFilter"] = ["None"] + [
                f"{corner}, {rolloff}"
                for corner in list(self.cutoff_frequencies.keys())[1:]
                for rolloff in self.filter_rolloffs
            ]
            gui_parameters["LowPassFilter"] = ["None"] + [
                f"{corner}, {rolloff}"
                for corner in reversed(list(self.cutoff_frequencies.keys())[1:])
                for rolloff in self.filter_rolloffs
            ]

        gui_parameters.update(
            {
                "Filter1": ["High pass digital filter ON", "High pass digital filter OFF"],
                "Lock-In harmonic": 1,
                "Reference phase shift in degrees": ["Auto", "As is", "0.0 (edit)"],
                "Frequency range threshold factor of -3 dB": 0.1,
                "": None,  # empty line
                "Turn off LED": False,
            }
        )
        return gui_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Read the GUI parameters selected by the user and store them in driver attributes."""
        channel = str(parameters.get("Channel", ""))
        if channel.strip().lower() in ("m1", "m2", "m3"):
            self.slot = channel.strip()[1]  # e.g. "1" for "M1"
        else:
            self.slot = ""

        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.range = self.voltage_ranges.get(parameters.get("Sensitivity", "Auto"), 0.0)
        self.input_config = self.input_configurations.get(parameters.get("Input", "A-B"), "AB")
        self.coupling = parameters.get("Coupling", "DC")
        self.lia_ref = parameters.get("Source", "S1")
        self.lia_harmonic = parameters.get("Lock-In harmonic", 1)
        self.lia_avg_ref_cycles = parameters.get("Averaging reference cycles", 0)
        self.wait_time_constants = str(parameters.get("WaitTimeConstants", "Auto"))

        # Traditional IIR low pass output filter: a numeric entry is the time constant,
        # any non-numeric entry (e.g. "Traditional low pass output filter OFF") disables it.
        raw_tc = str(parameters.get("TimeConstant", "0.1"))
        try:
            self.lia_tc = float(raw_tc.split(" ")[0])
            self.lia_lowpass = True
        except (ValueError, TypeError):
            self.lia_lowpass = False

        raw_slope = str(parameters.get("Slope", "12"))
        try:
            self.lia_rolloff = int(raw_slope.split(" ")[0])
        except (ValueError, TypeError):
            self.lia_rolloff = 12

        # Analog input filter ('Reserve' selects the filter optimization)
        self.filter_optimization = self.filter_optimizations.get(parameters.get("Reserve", ""), "")
        self.filter_on = bool(self.filter_optimization)
        if self.filter_on:
            lowpass = str(parameters.get("LowPassFilter", "None")).split(",")
            self.lowpass_corner = self.cutoff_frequencies.get(lowpass[0].strip(), "NONE")
            if len(lowpass) > 1:
                self.lowpass_rolloff = self.filter_rolloffs.get(lowpass[1].strip(), 6)
            highpass = str(parameters.get("HighPassFilter", "None")).split(",")
            self.highpass_corner = self.cutoff_frequencies.get(highpass[0].strip(), "NONE")
            if len(highpass) > 1:
                self.highpass_rolloff = self.filter_rolloffs.get(highpass[1].strip(), 6)

        self.digital_highpass = "ON" in str(parameters.get("Filter1", "ON"))
        self.lia_phase_mode = str(parameters.get("Reference phase shift in degrees", "Auto"))
        self.freq_range_threshold = parameters.get("Frequency range threshold factor of -3 dB", 0.1)
        self.darkmode = bool(parameters.get("Turn off LED", False))

        self.shortname = f"VM-10 @ M{self.slot}"

    # --- semantic standard functions called by SweepMe! during a measurement ---

    def initialize(self) -> None:
        """Check channel selection and connected module, then load the module defaults."""
        if not self.slot:
            msg = "Please give a correct channel number (M1, M2 or M3)."
            raise ValueError(msg)
        self.check_device()
        if self.lia_phase_mode.strip().lower() == "as is":
            # PRESet below resets the reference phase shift to its power-on default.
            # Remember the phase currently set on the instrument so that
            # set_lockin_settings() can restore it afterwards.
            self.stored_phase_shift = float(self.port.query(f"SENSe{self.slot}:LIA:DPHase?"))
        self.port.write(f"SENSe{self.slot}:PRESet")  # reset module to power-on defaults

    def configure(self) -> None:
        """Write all GUI settings to the instrument."""
        self.set_mode("LIA")
        self.set_input_configuration(self.input_config)
        self.set_coupling(self.coupling)
        self.set_analog_filter()  # set filters before range: the range limits depend on them
        self.set_range()
        self.set_time_constant()
        self.set_lockin_settings()
        self.set_advanced_settings()

    def reconfigure(self, parameters: dict[str, Any] | None = None, keys: list[str] | None = None) -> None:
        """Reapply the configuration when a GUI parameter changes during a run via the {...} parameter system."""
        if parameters:
            self.apply_gui_parameters(parameters)
        self.configure()

    def apply(self) -> None:
        """Apply a new sweep value (self.value) according to the selected sweep mode."""
        if self.sweep_mode == "Sensitivity in V":
            value = self.value
            if isinstance(value, str) and value in self.voltage_ranges:
                self.range = self.voltage_ranges[value]
            else:
                try:
                    self.range = float(value)
                except (ValueError, TypeError) as e:
                    msg = f"Cannot parse sensitivity sweep value: {value}"
                    raise ValueError(msg) from e
            self.set_range()

        elif self.sweep_mode == "Time constant in s":
            value = self.value
            if isinstance(value, str) and "off" in value.lower():
                self.lia_lowpass = False
            else:
                try:
                    self.lia_tc = float(value)
                    self.lia_lowpass = True
                except (ValueError, TypeError) as e:
                    msg = f"Cannot parse time constant sweep value: {value}"
                    raise ValueError(msg) from e
            self.set_time_constant()

    def measure(self) -> None:
        """Wait the requested settle time, then request a synchronized snapshot of all lock-in values."""
        if self.wait_time > 0:
            # Additional wait of N time constants, e.g. after a source module changed its value.
            # Sleep in small steps so the user can stop the run at any time.
            start_time = time.time()
            while not self.is_run_stopped() and time.time() - start_time < self.wait_time:
                time.sleep(min(0.05, self.wait_time))
        self.request_lockin_snapshot()

    def read_result(self) -> None:
        """Read the snapshot and repeat the query until the instrument reports settled values."""
        timeout = float(self.port_properties.get("timeout", 15))
        start_time = time.time()
        while True:
            response = self.port.read().split(",")
            if len(response) == 6:
                settling = bool(int(float(response[5])))
                if not settling:
                    break
            if self.is_run_stopped():
                return
            if time.time() - start_time > timeout + self.wait_time:
                msg = f"Lock-in did not settle within the timeout of {timeout} s."
                raise TimeoutError(msg)
            time.sleep(0.05)
            self.request_lockin_snapshot()

        self.x_lia = self.convert_measurement(response[0])
        self.y_lia = self.convert_measurement(response[1])
        self.r_lia = self.convert_measurement(response[2])
        self.theta_lia = self.convert_measurement(response[3])
        self.freq_lia = self.convert_measurement(response[4])

        # The lock-in DC component is not available via FETCh:MULTiple and is queried separately.
        # It is only measured by the instrument when the high pass digital filter is enabled.
        if self.digital_highpass:
            dc_response = self.port.query(f"FETCh:SENSe{self.slot}:LIA:DC?")
            self.dc_lia = self.convert_measurement(dc_response)
        else:
            self.dc_lia = float("nan")

    def call(self) -> list[float]:
        """Return the measurement results in the order of self.variables."""
        return [self.x_lia, self.y_lia, self.r_lia, self.theta_lia, self.freq_lia, self.dc_lia]

    # --- wrapped functions ---

    def check_device(self) -> None:
        """Verify that the module connected to the selected channel is a VM-10."""
        model = self.port.query(f"SENSe{self.slot}:MODel?")
        if "VM-10" not in model:
            msg = (
                f"Device connected on channel M{self.slot} does not match this driver. "
                f"Found: '{model}'"
            )
            raise ValueError(msg)

    def set_mode(self, mode: str) -> None:
        """Set the measurement mode of the module (DC, AC, or LIA)."""
        self.port.write(f"SENSe{self.slot}:MODE {mode}")

    def set_input_configuration(self, input_config: str) -> None:
        """Set the input configuration (AB, A, or GROund)."""
        self.port.write(f"SENSe{self.slot}:CONFiguration {input_config}")

    def set_coupling(self, coupling: str) -> None:
        """Set the input coupling (DC or AC)."""
        if coupling not in ("DC", "AC"):
            msg = f"Invalid coupling '{coupling}'. Use 'DC' or 'AC'."
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:COUPling {coupling}")

    def set_range(self) -> None:
        """Set the voltage range or enable autorange (self.range == 0.0)."""
        if self.range:
            if self.range not in self.voltage_ranges.values():
                msg = (
                    f"Invalid sensitivity '{self.range}'. "
                    f"The VM-10 supports 10 V, 1 V, 0.1 V, and 0.01 V."
                )
                raise ValueError(msg)
            if self.filter_on and self.filter_optimization == "REServe" and self.range > 0.1:
                # The VM-10 does not support this combination. It would quietly reduce the range.
                msg = (
                    "The 10 V and 1 V ranges cannot be used while the analog input filter "
                    "is enabled with filter optimization 'Highest reserve'."
                )
                raise ValueError(msg)
            self.port.write(f"SENSe{self.slot}:VOLTage:RANGe:AUTO 0")
            self.port.write(f"SENSe{self.slot}:VOLTage:RANGe {self.range}")
        else:
            self.port.write(f"SENSe{self.slot}:VOLTage:RANGe:AUTO 1")

    def set_time_constant(self) -> None:
        """Configure the traditional IIR low pass output filter and the settle wait time."""
        # Additional wait time per measurement point in units of the time constant
        if self.wait_time_constants.strip().lower() == "auto":
            # Rely on the instrument's settling flag, no additional wait
            self.wait_time = 0.0
        else:
            try:
                self.wait_time = float(self.wait_time_constants) * (self.lia_tc if self.lia_lowpass else 0.0)
            except (ValueError, TypeError) as e:
                msg = "'WaitTimeConstants' must be 'Auto' or a number."
                raise ValueError(msg) from e

        self.port.write(f"SENSe{self.slot}:LIA:LPASs {'1' if self.lia_lowpass else '0'}")
        if self.lia_lowpass:
            if not 0.0001 <= self.lia_tc <= 10000:
                msg = f"Lock-In time constant is {self.lia_tc} s. Must be between 0.0001 s and 10,000 s."
                raise ValueError(msg)
            if self.lia_rolloff not in (6, 12, 18, 24):
                msg = f"Invalid output filter slope '{self.lia_rolloff}'. Use 6, 12, 18, or 24 dB/oct."
                raise ValueError(msg)
            self.port.write(f"SENSe{self.slot}:LIA:TIMEconstant {self.lia_tc}")
            self.port.write(f"SENSe{self.slot}:LIA:ROLLoff R{self.lia_rolloff}")

    def set_lockin_settings(self) -> None:
        """Configure reference source, harmonic, FIR averaging filter, and reference phase shift."""
        # Reference source
        reference = self.lia_ref
        if reference not in ("S1", "S2", "S3"):
            if reference.lower().startswith("reference"):
                reference = "RIN"  # external reference input
            else:
                msg = f"No valid reference source selected: {self.lia_ref}."
                raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:LIA:RSOurce {reference}")

        # Reference harmonic
        try:
            harmonic = int(self.lia_harmonic)
        except (ValueError, TypeError) as e:
            msg = "Please enter a positive integer for the lock-in harmonic."
            raise ValueError(msg) from e
        if harmonic < 1:
            msg = "The lock-in harmonic must be >= 1."
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:LIA:DHARmonic {harmonic}")

        # FIR averaging output filter over N cycles of the reference frequency
        try:
            cycles = int(self.lia_avg_ref_cycles)
        except (ValueError, TypeError) as e:
            msg = (
                "Please enter an integer number of averaging reference cycles. "
                "'0' disables the averaging output filter."
            )
            raise ValueError(msg) from e
        if cycles == 0:
            self.port.write(f"SENSe{self.slot}:LIA:AVERage 0")
        else:
            if not 1 <= cycles <= 1000000:
                msg = "The number of averaging reference cycles must be between 1 and 1,000,000."
                raise ValueError(msg)
            self.port.write(f"SENSe{self.slot}:LIA:AVERage 1")
            self.port.write(f"SENSe{self.slot}:LIA:REFerence:CYCLes {cycles}")

        # Reference phase shift
        phase_mode = self.lia_phase_mode.strip()
        if phase_mode.lower() == "auto":
            # The instrument sets the phase shift so that the present signal appears at 0°.
            # Note: the measurement should be settled when this command is sent.
            self.port.write(f"SENSe{self.slot}:LIA:DPHase:AUTO")
        elif phase_mode.lower() == "as is":
            # Restore the phase shift that was set on the instrument before the run,
            # because the module preset during initialize() has reset it.
            self.port.write(f"SENSe{self.slot}:LIA:DPHase {self.stored_phase_shift}")
        else:
            try:
                self.lia_phase_shift = float(phase_mode.split(" ")[0])
            except (ValueError, TypeError) as e:
                msg = (
                    "The reference phase shift must be 'Auto', 'As is', "
                    "or a number between -360 and +360 degrees."
                )
                raise ValueError(msg) from e
            if not -360 <= self.lia_phase_shift <= 360:
                msg = "The reference phase shift must be between -360 and +360 degrees."
                raise ValueError(msg)
            self.port.write(f"SENSe{self.slot}:LIA:DPHase {self.lia_phase_shift}")

    def set_analog_filter(self) -> None:
        """Configure the analog input filter of the VM-10 (hardware high/low pass)."""
        if not self.filter_on:
            self.port.write(f"SENSe{self.slot}:FILTer:STATe 0")
            return
        self.port.write(f"SENSe{self.slot}:FILTer:STATe 1")
        self.port.write(f"SENSe{self.slot}:FILTer:OPTimization {self.filter_optimization}")
        self.port.write(f"SENSe{self.slot}:FILTer:LPASs:FREQuency {self.lowpass_corner}")
        self.port.write(f"SENSe{self.slot}:FILTer:LPASs:ATTenuation R{self.lowpass_rolloff}")
        self.port.write(f"SENSe{self.slot}:FILTer:HPASs:FREQuency {self.highpass_corner}")
        self.port.write(f"SENSe{self.slot}:FILTer:HPASs:ATTenuation R{self.highpass_rolloff}")

    def set_advanced_settings(self) -> None:
        """Configure the digital high pass filter, autorange frequency threshold, and dark mode."""
        self.port.write(f"SENSe{self.slot}:DIGital:FILTer:HPASs {'1' if self.digital_highpass else '0'}")

        try:
            threshold = float(self.freq_range_threshold)
        except (ValueError, TypeError) as e:
            msg = "Please enter a number for the frequency range threshold."
            raise ValueError(msg) from e
        if not 0.0 <= threshold <= 1.0:
            msg = (
                "The frequency range threshold must be between 0.0 and 1.0. "
                "It is normalized to the -3 dB bandwidth of the range."
            )
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:FRTHreshold {threshold}")

        self.port.write(f"SENSe{self.slot}:DMODe {'1' if self.darkmode else '0'}")

    def request_lockin_snapshot(self) -> None:
        """Request a time-synchronized snapshot of all lock-in readings and the settling flag."""
        self.port.write(
            f"FETCh:MULTiple? "
            f"MX,{self.slot},"
            f"MY,{self.slot},"
            f"MR,{self.slot},"
            f"MTHeta,{self.slot},"
            f"MRFRequency,{self.slot},"
            f"MSETtling,{self.slot}"
        )

    def get_settle_time(self, settle_percent: float = 0.1) -> float:
        """Query the lock-in settle time in s for the given settle percentage (e.g. 0.1 = 0.1 %)."""
        return float(self.port.query(f"SENSe{self.slot}:LIA:STIMe? {settle_percent}"))

    def get_equivalent_noise_bandwidth(self) -> float:
        """Query the equivalent noise bandwidth (ENBW) of the lock-in output filters in Hz."""
        return float(self.port.query(f"SENSe{self.slot}:LIA:ENBW?"))

    def is_locked(self) -> bool:
        """Query whether the lock-in PLL is locked to the reference signal."""
        return bool(int(self.port.query(f"FETCh:SENSe{self.slot}:LIA:LOCK?")))

    @staticmethod
    def convert_measurement(value_string: str) -> float:
        """Convert an M81 reading to float, mapping the SCPI sentinel values.

        The M81 uses two special values:
        * 9.90e37 -> measurement overload -> converted to +inf
        * 9.91e37 -> PLL unlocked or value invalid/settling -> converted to NaN
        """
        try:
            value = float(value_string)
        except (ValueError, TypeError):
            return float("nan")
        if value == 9.90e37:
            return float("inf")
        if value == 9.91e37:
            return float("nan")
        return value
