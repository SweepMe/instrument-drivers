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
# * Instrument: Thorlabs PAX1000

# Contribution: a first, DLL-based version of this driver was contributed by a SweepMe! user.
# This driver instead speaks SCPI over USBTMC and needs no Thorlabs TLPAX instrument driver DLL.

"""SweepMe! Logger driver for the Thorlabs PAX1000 polarimeter, using SCPI over USBTMC."""

from __future__ import annotations

import math
import time
from typing import Any, ClassVar

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

# Operating modes. The value is sent as parameter of "SENS:CALC" and uses the same enumeration as the
# TLPAX_MEASMODE_x constants of the Thorlabs instrument driver. The label states how many waveplate
# revolutions contribute to one measurement and how many points are used for the FFT.
MEASUREMENT_MODES = {
    "Half turn, 512 points": 1,
    "Half turn, 1024 points": 2,
    "Half turn, 2048 points": 3,
    "Full turn, 512 points": 4,
    "Full turn, 1024 points": 5,
    "Full turn, 2048 points": 6,
    "Double turn, 512 points": 7,
    "Double turn, 1024 points": 8,
    "Double turn, 2048 points": 9,
}

DEFAULT_MEASUREMENT_MODE = "Full turn, 1024 points"

# The measurement rate depends on the operating mode: a half turn mode yields one scan per basic scan
# period, a full turn mode one per two periods and a double turn mode one per four periods.
SCANS_PER_BASIC_PERIOD = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 4,
    8: 4,
    9: 4,
}

# --- Layout of the "SENS:DATA:LAT?" response ---------------------------------------------------------
#
# The instrument answers with 13 comma separated values: seven integers followed by six floats. The
# field count and the split into 7 integers / 6 floats are certain, as is the meaning of the three
# floats listed first below. The remaining assignments are derived from the Thorlabs instrument driver
# and should be confirmed against a real instrument once - see examples/probe_scan_record.py, which
# prints a raw response together with the interpretation used here.
#
# Confirmed: the instrument reports azimuth, ellipticity and DOP. It does NOT report the Stokes
# parameters; those are calculated from azimuth and ellipticity (see stokes_from_ellipse) and form a
# unit vector, so DOLP and DOCP have to be scaled with DOP.
SCAN_FIELD_COUNT = 13
SCAN_INTEGER_FIELDS = 7

IDX_SCAN_COUNTER = 0
IDX_TIMESTAMP = 1
IDX_WAVEPLATE_COUNT = 5

IDX_AZIMUTH = 7
IDX_DOP = 8
IDX_ELLIPTICITY = 9
IDX_POWER = 10
IDX_REVOLUTION_TIME = 11
IDX_MISALIGNMENT = 12

# Optical power below this level is reported as this dBm value instead of -inf.
MINIMUM_DBM = -200.0


class Device(EmptyDevice):
    """SweepMe! Logger driver for the Thorlabs PAX1000 rotating waveplate polarimeter."""

    actions: ClassVar[list[str]] = ["set_power_autorange_once"]

    def __init__(self) -> None:
        """Initialize driver parameters. Kept lightweight, as it is also called for metadata only."""
        super().__init__()

        self.shortname = "PAX1000"

        self.port_manager = True
        self.port_types = ["USBTMC"]
        self.port_properties = {
            "timeout": 5,  # in seconds
        }

        # GUI parameters
        self.port_string: str = ""
        self.wavelength_nm: str = "633"
        self.measurement_mode: int = MEASUREMENT_MODES[DEFAULT_MEASUREMENT_MODE]
        self.scan_rate: str = "Maximum"
        self.power_range_mode: str = "Auto"
        self.power_range_dbm: str = "0"
        self.power_unit: str = "mW"
        self.wait_for_new_scan: bool = True
        self.averages: int = 1
        self.keep_motor_running: bool = True
        self.report_stokes: bool = False
        self.report_diagnostics: bool = False

        # Instrument limits, read during initialize
        self.wavelength_limits_m: tuple[float, float] = (0.0, 0.0)

        # Measured quantities, all in SI base units
        self.azimuth_rad: float = 0.0
        self.ellipticity_rad: float = 0.0
        self.dop: float = 0.0
        self.dolp: float = 0.0
        self.docp: float = 0.0
        self.power_w: float = 0.0
        self.s1: float = 0.0
        self.s2: float = 0.0
        self.s3: float = 0.0
        self.revolution_time_s: float = 0.0
        self.misalignment: float = 0.0
        self.waveplate_count: int = 0

        # Bookkeeping to recognize a scan that the instrument has already reported before
        self.last_waveplate_count: int | None = None
        self.expected_scan_period_s: float = 0.1

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the available user interface fields for the current state."""
        power_range_mode = parameters.get("Power range", "Auto")

        gui_parameters = {
            "Wavelength in nm": parameters.get("Wavelength in nm", "633"),
            "Measurement mode": list(MEASUREMENT_MODES.keys()),
            "Basic scan rate in 1/s": ["Maximum", "Minimum", "50", "100", "200", "400"],
            "Power range": ["Auto", "Auto once", "Manual"],
        }

        if power_range_mode == "Manual":
            gui_parameters["Power range in dBm"] = parameters.get("Power range in dBm", "0")

        gui_parameters.update(
            {
                " ": None,
                "Acquisition": None,
                "Wait for new scan": True,
                "Averages": 1,
                "Keep motor running between branches": True,
                "  ": None,
                "Additional output": None,
                "Power unit": ["mW", "W", "dBm"],
                "Non-normalized Stokes vector": False,
                "Scan diagnostics": False,
            },
        )

        return gui_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selected user interface values and update the output variables."""
        self.port_string = parameters.get("Port", "")

        self.wavelength_nm = parameters.get("Wavelength in nm", "633")
        mode_label = parameters.get("Measurement mode", DEFAULT_MEASUREMENT_MODE)
        self.measurement_mode = MEASUREMENT_MODES.get(mode_label, MEASUREMENT_MODES[DEFAULT_MEASUREMENT_MODE])
        self.scan_rate = parameters.get("Basic scan rate in 1/s", "Maximum")
        self.power_range_mode = parameters.get("Power range", "Auto")
        self.power_range_dbm = parameters.get("Power range in dBm", "0")

        self.power_unit = parameters.get("Power unit", "mW")
        self.wait_for_new_scan = parameters.get("Wait for new scan", True)
        self.averages = max(1, int(parameters.get("Averages", 1)))
        self.keep_motor_running = parameters.get("Keep motor running between branches", True)
        self.report_stokes = parameters.get("Non-normalized Stokes vector", False)
        self.report_diagnostics = parameters.get("Scan diagnostics", False)

        # SweepMe! reads the output variables before any other function is called, so they must be
        # updated here and not only in configure().
        variables = [
            "Azimuth",
            "Ellipticity",
            "DOP",
            "DOLP",
            "DOCP",
            "Power",
            "Polarized power",
            "Unpolarized power",
            "s1",
            "s2",
            "s3",
        ]
        units = ["deg", "deg", "%", "%", "%", self.power_unit, self.power_unit, self.power_unit, "", "", ""]

        if self.report_stokes:
            variables += ["S0", "S1", "S2", "S3"]
            units += [self.power_unit] * 4

        if self.report_diagnostics:
            variables += ["Revolution time", "Misalignment", "Waveplate count"]
            units += ["s", "", ""]

        self.variables = variables
        self.units = units
        self.plottype = [True] * len(variables)
        self.savetype = [True] * len(variables)

    def initialize(self) -> None:
        """Reset the status reporting, identify the instrument and read out its wavelength limits."""
        self.clear_status()
        identification = self.get_identification()
        debug(f"PAX1000: connected to {identification}")

        self.wavelength_limits_m = self.get_wavelength_limits()

    def configure(self) -> None:
        """Apply wavelength, power range, operating mode and waveplate speed."""
        wavelength_m = float(self.wavelength_nm) * 1e-9
        minimum, maximum = self.wavelength_limits_m
        if not minimum <= wavelength_m <= maximum:
            msg = (
                f"Wavelength {float(self.wavelength_nm):.1f} nm is outside the range of this PAX1000 "
                f"({minimum * 1e9:.1f} nm to {maximum * 1e9:.1f} nm)."
            )
            raise ValueError(msg)
        self.set_wavelength(wavelength_m)

        if self.power_range_mode == "Manual":
            # Setting a fixed range implicitly switches auto ranging off.
            self.set_power_range(10.0 ** (float(self.power_range_dbm) / 10.0) * 1e-3)
        else:
            self.set_power_autorange(True)
            if self.power_range_mode == "Auto once":
                self.set_power_autorange_once()

        # The operating mode also starts the waveplate motor. It has to be set before the scan rate,
        # because the allowed scan rate range depends on it.
        self.set_measurement_mode(self.measurement_mode)

        applied_mode, motor_running = self.get_measurement_mode()
        if applied_mode != self.measurement_mode or not motor_running:
            msg = (
                f"PAX1000 did not accept the operating mode: requested {self.measurement_mode}, "
                f"instrument reports mode {applied_mode} with motor state {int(motor_running)}."
            )
            raise RuntimeError(msg)

        self.apply_basic_scan_rate()
        self.check_error()

        self.wait_until_motor_settled()
        self.last_waveplate_count = None

    def unconfigure(self) -> None:
        """Stop the waveplate motor unless it shall keep running for the next branch."""
        if self.keep_motor_running:
            return

        self.set_measurement_mode(0)

    def deinitialize(self) -> None:
        """Stop the motor and hand control back to the front panel."""
        self.set_measurement_mode(0)

        try:
            self.port.port.control_ren(6)  # go to local
        except Exception:
            debug("PAX1000: could not switch the instrument back to local control.")

    def measure(self) -> None:
        """Read one scan, or average over several scans."""
        if self.averages == 1:
            self.evaluate_scan(self.acquire_scan())
            return

        sum_s1 = sum_s2 = sum_s3 = 0.0
        sum_power = sum_dop = 0.0
        sum_revolution_time = sum_misalignment = 0.0

        for _ in range(self.averages):
            self.evaluate_scan(self.acquire_scan())
            sum_s1 += self.s1
            sum_s2 += self.s2
            sum_s3 += self.s3
            sum_power += self.power_w
            sum_dop += self.dop
            sum_revolution_time += self.revolution_time_s
            sum_misalignment += self.misalignment

        count = float(self.averages)
        self.power_w = sum_power / count
        self.dop = sum_dop / count
        self.revolution_time_s = sum_revolution_time / count
        self.misalignment = sum_misalignment / count

        # Averaging is done on the Stokes vector rather than on the angles, which would be wrong close
        # to the wrap-around of the azimuth. The mean vector is scaled back to unit length afterwards.
        length = math.sqrt(sum_s1**2 + sum_s2**2 + sum_s3**2)
        if length > 0.0:
            self.s1 = sum_s1 / length
            self.s2 = sum_s2 / length
            self.s3 = sum_s3 / length

        self.azimuth_rad = 0.5 * math.atan2(self.s2, self.s1)
        self.ellipticity_rad = 0.5 * math.atan2(self.s3, math.sqrt(self.s1**2 + self.s2**2))
        self.update_degrees_of_polarization()

    def call(self) -> list[float]:
        """Return one value per entry of self.variables."""
        values = [
            math.degrees(self.azimuth_rad),
            math.degrees(self.ellipticity_rad),
            self.dop * 100.0,
            self.dolp * 100.0,
            self.docp * 100.0,
            self.convert_power(self.power_w),
            self.convert_power(self.power_w * self.dop),
            self.convert_power(self.power_w * (1.0 - self.dop)),
            self.s1,
            self.s2,
            self.s3,
        ]

        if self.report_stokes:
            # The Stokes vector s is normalized to unit length, so the non-normalized components carry
            # the degree of polarization as an additional factor.
            values += [
                self.convert_power(self.power_w),
                self.convert_power(self.power_w * self.dop * self.s1),
                self.convert_power(self.power_w * self.dop * self.s2),
                self.convert_power(self.power_w * self.dop * self.s3),
            ]

        if self.report_diagnostics:
            values += [self.revolution_time_s, self.misalignment, float(self.waveplate_count)]

        return values

    # --- Scan handling ---------------------------------------------------------------------------

    def acquire_scan(self) -> list[float]:
        """Return the fields of a scan, optionally waiting until the instrument has finished a new one.

        Returns:
            The 13 fields of the "SENS:DATA:LAT?" response, integers first.
        """
        fields = self.get_latest_scan()

        if not self.wait_for_new_scan:
            return fields

        # A scan is new when the waveplate has advanced. The instrument repeats the most recent scan
        # when it is polled faster than it measures.
        deadline = time.monotonic() + 10.0 * self.expected_scan_period_s + 2.0
        while int(fields[IDX_WAVEPLATE_COUNT]) == self.last_waveplate_count:
            if time.monotonic() > deadline:
                msg = (
                    "PAX1000 did not deliver a new scan in time. Check that the waveplate motor is "
                    "running and that the basic scan rate matches the operating mode."
                )
                raise RuntimeError(msg)
            time.sleep(0.2 * self.expected_scan_period_s)
            fields = self.get_latest_scan()

        return fields

    def evaluate_scan(self, fields: list[float]) -> None:
        """Store the quantities of one scan and derive everything the instrument does not report."""
        self.last_waveplate_count = int(fields[IDX_WAVEPLATE_COUNT])
        self.waveplate_count = int(fields[IDX_WAVEPLATE_COUNT])

        self.azimuth_rad = fields[IDX_AZIMUTH]
        self.ellipticity_rad = fields[IDX_ELLIPTICITY]
        self.dop = fields[IDX_DOP]
        self.power_w = fields[IDX_POWER]
        self.revolution_time_s = fields[IDX_REVOLUTION_TIME]
        self.misalignment = fields[IDX_MISALIGNMENT]

        self.s1, self.s2, self.s3 = self.stokes_from_ellipse(self.azimuth_rad, self.ellipticity_rad)
        self.update_degrees_of_polarization()

    def update_degrees_of_polarization(self) -> None:
        """Derive DOLP and DOCP from DOP and the normalized Stokes vector."""
        self.dolp = self.dop * math.sqrt(self.s1**2 + self.s2**2)
        self.docp = self.dop * abs(self.s3)

    @staticmethod
    def stokes_from_ellipse(azimuth_rad: float, ellipticity_rad: float) -> tuple[float, float, float]:
        """Return the normalized Stokes vector for a polarization ellipse.

        The result has unit length and describes the direction of the state of polarization only. The
        degree of polarization is reported separately by the instrument.

        Args:
            azimuth_rad: Azimuth angle of the polarization ellipse in radian.
            ellipticity_rad: Ellipticity angle of the polarization ellipse in radian.

        Returns:
            The three normalized Stokes parameters s1, s2 and s3.
        """
        s1 = math.cos(2.0 * ellipticity_rad) * math.cos(2.0 * azimuth_rad)
        s2 = math.cos(2.0 * ellipticity_rad) * math.sin(2.0 * azimuth_rad)
        s3 = math.sin(2.0 * ellipticity_rad)
        return s1, s2, s3

    def convert_power(self, power_w: float) -> float:
        """Convert an optical power in W into the unit selected in the user interface."""
        if self.power_unit == "W":
            return power_w
        if self.power_unit == "mW":
            return power_w * 1e3
        if power_w <= 0.0:
            return MINIMUM_DBM
        return 10.0 * math.log10(power_w / 1e-3)

    def apply_basic_scan_rate(self) -> None:
        """Set the waveplate speed and remember how long one scan is expected to take."""
        minimum, maximum = self.get_basic_scan_rate_limits()

        if self.scan_rate == "Maximum":
            scan_rate = maximum
        elif self.scan_rate == "Minimum":
            scan_rate = minimum
        else:
            scan_rate = min(max(float(self.scan_rate), minimum), maximum)

        self.set_basic_scan_rate(scan_rate)

        applied_rate = self.get_basic_scan_rate()
        self.expected_scan_period_s = SCANS_PER_BASIC_PERIOD[self.measurement_mode] / max(applied_rate, 1e-6)

    def wait_until_motor_settled(self, timeout_s: float = 20.0) -> None:
        """Block until the waveplate motor has reached its target speed."""
        deadline = time.monotonic() + timeout_s

        while not self.is_motor_settled():
            if time.monotonic() > deadline:
                msg = f"PAX1000 waveplate motor did not settle within {timeout_s:.0f} s."
                raise RuntimeError(msg)
            time.sleep(0.2)

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        self.port.write("*IDN?")
        return self.port.read()

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS;*SRE 0;*ESE 0;:STAT:PRES")

    def check_error(self) -> None:
        """Raise if the instrument has queued an error."""
        self.port.write("SYST:ERR?")
        answer = self.port.read()

        code = answer.split(",")[0].strip()
        if code not in ("0", "+0"):
            msg = f"PAX1000 reports an error: {answer}"
            raise RuntimeError(msg)

    def set_wavelength(self, wavelength_m: float) -> None:
        """Set the wavelength used to calculate the measurement data.

        Args:
            wavelength_m: Wavelength in meter.
        """
        self.port.write(f"SENS:CORR:WAV {wavelength_m:.12e}")

    def get_wavelength(self) -> float:
        """Return the configured wavelength in meter."""
        self.port.write("SENS:CORR:WAV?")
        return float(self.port.read())

    def get_wavelength_limits(self) -> tuple[float, float]:
        """Return the smallest and largest wavelength this instrument supports, in meter."""
        self.port.write("SENS:CORR:WAV? MIN;:SENS:CORR:WAV? MAX")
        minimum, maximum = self.port.read().split(";")
        return float(minimum), float(maximum)

    def set_power_range(self, power_w: float) -> None:
        """Set the highest optical power expected at the input, which disables auto ranging.

        Args:
            power_w: Maximum expected optical power in watt.
        """
        self.port.write(f"SENS:POW:RANG {power_w:.12e}")

    def set_power_autorange(self, state: bool) -> None:
        """Switch continuous power auto ranging on or off."""
        self.port.write(f"SENS:POW:RANG:AUTO {int(state)}")

    def set_power_autorange_once(self) -> None:
        """Run auto ranging a single time and keep the range that was found."""
        self.port.write("SENS:POW:RANG:AUTO ONCE")

    def set_measurement_mode(self, mode: int) -> None:
        """Set the operating mode and start or stop the waveplate motor.

        Args:
            mode: Operating mode, see MEASUREMENT_MODES. Mode 0 stops the motor.
        """
        self.port.write(f"SENS:CALC {mode};:INP:ROT:STAT {int(mode != 0)}")

    def get_measurement_mode(self) -> tuple[int, bool]:
        """Return the active operating mode and whether the waveplate motor is running."""
        self.port.write("SENS:CALC?;:INP:ROT:STAT?")
        mode, motor_state = self.port.read().split(";")
        return int(mode), bool(int(motor_state))

    def set_basic_scan_rate(self, scan_rate: float) -> None:
        """Set the number of waveplate half turns per second.

        Args:
            scan_rate: Basic scan rate in 1/s.
        """
        self.port.write(f"INP:ROT:VEL {scan_rate:.6e}")

    def get_basic_scan_rate(self) -> float:
        """Return the basic scan rate in 1/s."""
        self.port.write("INP:ROT:VEL?")
        return float(self.port.read())

    def get_basic_scan_rate_limits(self) -> tuple[float, float]:
        """Return the basic scan rate limits in 1/s for the active mode and power supply."""
        self.port.write("INP:ROT:VEL? MIN;:INP:ROT:VEL? MAX")
        minimum, maximum = self.port.read().split(";")
        return float(minimum), float(maximum)

    def is_motor_settled(self) -> bool:
        """Return whether the waveplate motor has reached its target speed."""
        self.port.write("INP:ROT:SETT?")
        return bool(int(self.port.read()))

    def get_latest_scan(self) -> list[float]:
        """Return the fields of the most recently finished scan.

        Returns:
            The 13 values of the response, integers first. See the field index constants at the top of
            this file for their meaning.
        """
        self.port.write("SENS:DATA:LAT?")
        answer = self.port.read()

        fields = answer.split(",")
        if len(fields) != SCAN_FIELD_COUNT:
            msg = f"PAX1000 returned {len(fields)} instead of {SCAN_FIELD_COUNT} scan values. Response was: {answer}"
            raise RuntimeError(msg)

        return [float(field) for field in fields]
