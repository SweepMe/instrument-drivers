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
# * Instrument: LakeShore M81 VM-10

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):
    """SweepMe! Logger driver for the VM-10 voltage measure module of the LakeShore M81-SSM.

    Supports DC and AC (RMS/peak) voltage measurements. For phase-sensitive detection
    at a reference frequency, use the LockIn driver "LockIn-LakeShore_M81-VM-10" instead.
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
            # READ queries block until settling + averaging time are finished.
            # The maximum averaging time is 600 NPLC = 12 s at 50 Hz.
            "timeout": 30,
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "SOCKET_EOLwrite": "\n",
            "SOCKET_EOLread": "\n",
        }

        # Measurement modes of the VM-10 supported by this Logger driver
        self.modes: list[str] = ["DC", "AC"]

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

        # Analog input filter optimization modes
        self.filter_optimizations: dict[str, str] = {
            "Lowest noise": "NOISe",
            "Highest reserve": "REServe",
        }

        # Measurement parameters set via the GUI
        self.slot: str = ""  # measure channel number "1", "2", or "3"
        self.port_string: str = ""
        self.mode: str = "DC"
        self.range: float = 0.0  # 0.0 = autorange
        self.nplc: float = 1.0  # averaging time in number of power line cycles
        self.input_config: str = "AB"
        self.coupling: str = "DC"
        self.include_peaks: bool = False
        self.filter_on: bool = False
        self.filter_optimization: str = "NOISe"
        self.lowpass_corner: str = "NONE"
        self.lowpass_rolloff: int = 6
        self.highpass_corner: str = "NONE"
        self.highpass_rolloff: int = 6
        self.freq_range_threshold: float = 0.1
        self.darkmode: bool = False

        # Result parameters
        self.results: list[float] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return a dictionary of GUI fields and defaults depending on the current parameters."""
        mode = parameters.get("Mode", "DC")

        gui_parameters: dict[str, Any] = {
            "Channel": ["M1", "M2", "M3"],  # physical measure channels of the M81
            "Mode": self.modes,
            "Range": list(self.voltage_ranges.keys()),
            "Averaging time (NPLC)": 1.0,
            "Input configuration": list(self.input_configurations.keys()),
            "Coupling": ["DC", "AC"],
        }

        if mode == "AC":
            # Peak detection is only meaningful for AC signals
            gui_parameters["Include peak values"] = False

        gui_parameters[" "] = None  # empty line
        gui_parameters["Analog input filter"] = False
        if parameters.get("Analog input filter"):
            gui_parameters["Filter optimization"] = list(self.filter_optimizations.keys())
            gui_parameters["Low pass corner frequency"] = list(self.cutoff_frequencies.keys())
            gui_parameters["Low pass rolloff"] = list(self.filter_rolloffs.keys())
            if mode == "AC":
                # A hardware high pass would remove the DC component and falsify DC readings
                gui_parameters["High pass corner frequency"] = list(self.cutoff_frequencies.keys())
                gui_parameters["High pass rolloff"] = list(self.filter_rolloffs.keys())

        gui_parameters["  "] = None  # empty line
        gui_parameters["Frequency range threshold factor of -3 dB"] = 0.1
        gui_parameters["Turn off LED"] = False
        return gui_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Read the GUI parameters selected by the user and store them in driver attributes."""
        channel = str(parameters.get("Channel", ""))
        if channel.strip().lower() in ("m1", "m2", "m3"):
            self.slot = channel.strip()[1]  # e.g. "1" for "M1"
        else:
            self.slot = ""

        self.port_string = parameters.get("Port", "")
        self.mode = parameters.get("Mode", "DC")
        self.range = self.voltage_ranges.get(parameters.get("Range", "Auto"), 0.0)
        self.input_config = self.input_configurations.get(
            parameters.get("Input configuration", "A-B"), "AB"
        )
        self.coupling = parameters.get("Coupling", "DC")
        self.include_peaks = bool(parameters.get("Include peak values", False))

        try:
            self.nplc = float(parameters.get("Averaging time (NPLC)", 1.0))
        except (ValueError, TypeError):
            self.nplc = 1.0  # do not fail if the parameter is not yet loaded or empty

        self.filter_on = bool(parameters.get("Analog input filter", False))
        if self.filter_on:
            self.filter_optimization = self.filter_optimizations.get(
                parameters.get("Filter optimization", "Lowest noise"), "NOISe"
            )
            self.lowpass_corner = self.cutoff_frequencies.get(
                parameters.get("Low pass corner frequency", "None"), "NONE"
            )
            self.lowpass_rolloff = self.filter_rolloffs.get(
                parameters.get("Low pass rolloff", "6 dB/oct"), 6
            )
            if self.mode == "AC":
                self.highpass_corner = self.cutoff_frequencies.get(
                    parameters.get("High pass corner frequency", "None"), "NONE"
                )
                self.highpass_rolloff = self.filter_rolloffs.get(
                    parameters.get("High pass rolloff", "6 dB/oct"), 6
                )
            else:
                self.highpass_corner = "NONE"

        self.freq_range_threshold = parameters.get("Frequency range threshold factor of -3 dB", 0.1)
        self.darkmode = bool(parameters.get("Turn off LED", False))

        self.shortname = f"VM-10 @ M{self.slot}"

        # Returned variables depend on the mode
        if self.mode == "AC":
            self.variables = ["Voltage RMS", "Voltage DC"]
            self.units = ["V", "V"]
            if self.include_peaks:
                self.variables += ["Voltage Positive Peak", "Voltage Negative Peak", "Voltage Peak-Peak"]
                self.units += ["V", "V", "V"]
        else:
            self.variables = ["Voltage DC"]
            self.units = ["V"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    # --- semantic standard functions called by SweepMe! during a measurement ---

    def initialize(self) -> None:
        """Check channel selection and connected module, then load the module defaults."""
        if not self.slot:
            msg = "Please give a correct channel number (M1, M2 or M3)."
            raise ValueError(msg)
        self.check_device()
        self.port.write(f"SENSe{self.slot}:PRESet")  # reset module to power-on defaults

    def configure(self) -> None:
        """Write all GUI settings to the instrument."""
        self.set_mode(self.mode)
        self.set_input_configuration(self.input_config)
        self.set_coupling(self.coupling)
        self.set_analog_filter()  # set filters before range: the range limits depend on them
        self.set_range()
        self.set_nplc(self.nplc)
        self.set_advanced_settings()

    def reconfigure(self, parameters: dict[str, Any] | None = None, keys: list[str] | None = None) -> None:
        """Reapply the configuration when a GUI parameter changes during a run via the {...} parameter system."""
        if parameters:
            self.apply_gui_parameters(parameters)
        self.configure()

    def measure(self) -> None:
        """Trigger a new reading; the query returns after settling and the averaging time (NPLC)."""
        if self.mode == "AC":
            specifiers = f"MRMS,{self.slot},MDC,{self.slot}"
            if self.include_peaks:
                specifiers += f",MPPeak,{self.slot},MNPeak,{self.slot},MPTPeak,{self.slot}"
            # READ? acquires a fresh, time-synchronized reading of all requested values
            self.port.write(f"READ? {specifiers}")
        else:
            self.port.write(f"READ:SENSe{self.slot}:DC?")

    def read_result(self) -> None:
        """Read the acquired values from the instrument."""
        response = self.port.read().split(",")
        if len(response) != len(self.variables):
            msg = (
                f"Unexpected response length: expected {len(self.variables)} values, "
                f"received {len(response)}: '{','.join(response)}'"
            )
            raise ValueError(msg)
        self.results = [self.convert_measurement(value) for value in response]

    def call(self) -> list[float]:
        """Return the measurement results in the order of self.variables."""
        return self.results

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
        """Set the measurement mode of the module (DC or AC)."""
        if mode not in self.modes:
            msg = f"Invalid mode '{mode}'. This driver supports: {', '.join(self.modes)}."
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:MODE {mode}")

    def set_input_configuration(self, input_config: str) -> None:
        """Set the input configuration (AB, A, or GROund)."""
        self.port.write(f"SENSe{self.slot}:CONFiguration {input_config}")

    def set_coupling(self, coupling: str) -> None:
        """Set the input coupling (DC or AC)."""
        if coupling not in ("DC", "AC"):
            msg = f"Invalid coupling '{coupling}'. Use 'DC' or 'AC'."
            raise ValueError(msg)
        if coupling == "AC" and self.mode == "DC":
            # AC coupling engages a 0.16 Hz high pass that blocks the DC component
            msg = "AC coupling cannot be used in DC mode as it blocks the DC signal."
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:COUPling {coupling}")

    def set_range(self) -> None:
        """Set the voltage range or enable autorange (self.range == 0.0)."""
        if self.range:
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

    def set_nplc(self, nplc: float) -> None:
        """Set the averaging time in number of power line cycles (0.01 to 600)."""
        if not 0.01 <= nplc <= 600:
            msg = "The averaging time (NPLC) must be between 0.01 and 600.00."
            raise ValueError(msg)
        self.port.write(f"SENSe{self.slot}:NPLCycles {nplc}")

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
        if self.highpass_corner != "NONE":
            self.port.write(f"SENSe{self.slot}:FILTer:HPASs:ATTenuation R{self.highpass_rolloff}")

    def set_advanced_settings(self) -> None:
        """Configure the autorange frequency threshold and dark mode."""
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

    @staticmethod
    def convert_measurement(value_string: str) -> float:
        """Convert an M81 reading to float, mapping the SCPI sentinel values.

        The M81 uses two special values:
        * 9.90e37 -> measurement overload -> converted to +inf
        * 9.91e37 -> value invalid/settling -> converted to NaN
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
