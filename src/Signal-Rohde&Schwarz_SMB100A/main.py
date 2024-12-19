# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Module: Signal
# * Instrument: Rohde&Schwarz SMB100A

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Rohde&Schwarz SMB100A Signal Generator."""

    def __init__(self) -> None:
        """Initialize device parameters."""
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = [
            "USB",
            # "GPIB",
            "TCPIP",
        ]

        self.variables = ["Frequency", "Amplitude"]
        self.units = ["Hz", "V"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.frequency_input: str = "Frequency in Hz"  # or "Period in s"
        self.frequency: float = 2.2e9

        self.amplitude_mode: str = "Amplitude in V"  # or "High level in V"
        self.amplitude: float = 0.1

        self.delay_mode: str = "Phase in deg"  # or "Delay in s"
        self.delay: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": [
                "None",
                "Frequency in Hz",
                "Period in s",
                "Amplitude in V",
                "High level in V",
                "Phase in deg",
                "Delay in s",
            ],
            "Waveform": ["Sinus"],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 2e-6,
            "AmplitudeHiLevel": ["Amplitude in V", "High level in V"],
            "AmplitudeHiLevelValue": 1.0,
            "DelayPhase": ["Delay in s", "Phase in deg"],
            "DelayPhaseValue": 0.0,
            "Impedance": ["50"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get the GUI parameters."""
        self.sweep_mode = parameter["SweepMode"]
        self.frequency_input = parameter["PeriodFrequency"]
        self.frequency = float(parameter["PeriodFrequencyValue"])

        self.amplitude_mode = parameter["AmplitudeHiLevel"]
        self.amplitude = float(parameter["AmplitudeHiLevelValue"])

        self.delay_mode = parameter["DelayPhase"]
        self.delay = float(parameter["DelayPhaseValue"])

        self.variables = [self.frequency_input.split(" ")[0], self.amplitude_mode.split(" ")[0]]
        self.units = [self.frequency_input.split(" ")[-1], self.amplitude_mode.split(" ")[-1]]

    def connect(self) -> None:
        """Connect to the device."""
        self.port.write("*RST")
        # self.port.write("*CLS")

    def configure(self) -> None:
        """Configure the device."""
        self.lock_user_interface(True)

        self.set_power_mode("CW")
        self.set_power_unit("V")

        self.set_power_level(self.amplitude)

        # Set frequency
        self.set_frequency_mode("CW")

        if self.frequency_input == "Period in s":  # else it is "Frequency in Hz"
            self.frequency = 1 / self.frequency
        self.set_frequency(self.frequency)

        # Set phase
        if self.delay_mode == "Phase in deg":
            self.set_phase(self.delay)
        elif self.delay_mode == "Delay in s":
            self.set_delay(self.delay)

        self.set_output_state(True)

    def unconfigure(self) -> None:
        """Unconfigure the device."""
        self.check_errors()

        self.set_output_state(False)
        self.lock_user_interface(False)

    def apply(self) -> None:
        """Apply new sweep value."""
        self.value = float(self.value)

        if self.sweep_mode.startswith("Frequency"):
            self.set_frequency(self.value)

        elif self.sweep_mode.startswith("Period"):
            self.set_frequency(1 / self.value)

        elif self.sweep_mode.startswith("Amplitude") or self.sweep_mode.startswith("High level"):
            self.set_power_level(self.value)

        elif self.sweep_mode.startswith("Phase in deg"):
            self.set_phase(self.value)

        elif self.sweep_mode.startswith("Delay in s"):
            self.set_phase(self.value * 360 / self.frequency)

    def call(self) -> tuple:
        """Return the measured values."""
        measured_frequency = self.get_frequency()
        measured_power = self.get_power_level()
        return measured_frequency, measured_power  # , measured_impedance

    """Wrapper Functions"""

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the RF output."""
        min_frequency = 100e3
        max_frequency = 12.75e6
        if self.value < min_frequency or self.value > max_frequency:
            msg = f"Frequency {frequency} out of range. Choose between {min_frequency} and {max_frequency}."
            raise ValueError(msg)

        self.port.write(f"SOUR:FREQ {frequency}")

    def get_frequency(self) -> float:
        """Get the frequency of the RF output."""
        self.port.write("SOUR:FREQ?")
        return float(self.port.read())

    def set_frequency_mode(self, mode: str) -> None:
        """Set the frequency mode of the RF output to either 'CW' or 'Sweep'."""
        state = "SWE" if mode == "SWE" else "CW"
        self.port.write(f":SOUR:FREQ:MODE {state}")

    def set_phase(self, phase_degree: float) -> None:
        """Sets the phase variation relative to the current phase."""
        # Set the phase variation relative to the current phase
        phase_radians = phase_degree * np.pi / 180
        self.port.write(f"SOUR:PHAS {phase_radians}")

        # Adopt the set phase as the current phase
        self.port.write("PHAS:REF")

    def set_delay(self, delay: float) -> None:
        """Set the delay of the RF output."""
        phase_degree = delay * 360 / self.frequency
        self.set_phase(phase_degree % 360)

    def set_power_level(self, power: float) -> None:
        """Set the power level of the RF output."""
        if self.amplitude_mode == "Amplitude in V":
            self.set_amplitude(power)
        elif self.amplitude_mode == "High level in V":
            self.set_high_level(power)

    def set_amplitude(self, amplitude: float) -> None:
        """Set the amplitude of the RF output."""
        max_power = 7.071
        if self.value < 0 or self.value > max_power:
            msg = f"Power {amplitude} out of range. Choose between 0 and {max_power} V."
            raise ValueError(msg)
        # This one is without offset
        self.port.write(f"SOUR:POW:POW {amplitude}")

    def set_high_level(self, high_level: float) -> None:
        """Set the high level of the RF output."""
        max_power = 7.071
        if self.value < 0 or self.value > max_power:
            msg = f"Power {high_level} out of range. Choose between 0 and {max_power} V."
            raise ValueError(msg)

        # this one is with offset
        self.port.write(f"SOUR:POW:LEV:IMM:AMPL {high_level}")

    def get_power_level(self) -> float:
        """Get the power level of the RF output."""
        if self.amplitude_mode == "Amplitude in V":
            # This one is without offset
            self.port.write("SOUR:POW:POW?")
        elif self.amplitude_mode == "High level in V":
            # this one is with offset
            self.port.write("SOUR:POW:LEV:IMM:AMPL?")

        return float(self.port.read())

    def set_power_mode(self, mode: str) -> None:
        """Set the power mode of the RF output to either 'CW' or 'Sweep'."""
        state = "SWE" if mode == "SWE" else "CW"
        self.port.write(f":SOUR:POW:MODE {state}")

    def set_power_unit(self, unit: str) -> None:
        """Set the power unit of the RF output."""
        if unit not in ["V", "DBUV", "DBM"]:
            msg = "Invalid power unit. Choose from 'V', 'DBUV', 'DBM'."
            raise ValueError(msg)
        self.port.write(f"UNIT:POW {unit}")

    def set_output_state(self, set_on: bool) -> None:
        """Set the RF output state."""
        state = "ON" if set_on else "OFF"
        self.port.write(f":OUTP {state}")

    def check_errors(self) -> None:
        """Check for errors. Currently, no additional error handling is implemented."""
        self.port.write("SYST:ERR:ALL?")
        ret = self.port.read()
        if ret != '0,"No error"':
            print(f"Error: {ret}")

    def lock_user_interface(self, is_locked: bool) -> None:
        """Lock or unlock manual control through the keyboard of the device."""
        state = "DONL" if is_locked else "ENAB"
        self.port.write(f"SYST:ULOC {state}")

    """ Currently not implemented functions """

    def get_impedance(self) -> float:
        """Get the impedance of the RF output."""
        self.port.write(":OUTP:IMP?")
        answer = self.port.read()
        if answer == "G50":
            impedance = 50
        elif answer == "G1K":
            impedance = 1000
        else:
            impedance = -1
        return impedance

    def set_rf_mode(self, mode: str = "normal") -> None:
        """Low distortion, low noise, or normal."""
        level_modes = {
            "Normal": "NORM",
            "Low noise": "LOWN",
            "Low distortion": "LOWD",
        }
        self.port.write(f"SOURC:POW:LMODE {level_modes[mode]}")

    def run_self_test(self) -> bool:
        """Run the self test."""
        self.port.write("*TST?")
        ret = self.port.read()
        return ret == "0"

    def get_power_unit(self) -> str:
        """Get the power unit of the RF output."""
        self.port.write("UNIT:POW?")
        return self.port.read()

    def set_data_format(self) -> None:
        """Set the format of the return data from the device."""
        command = "FORM ASC"  # for ASCII
        command = "FORM PACK"  # for packed binary
        self.port.write(command)

    def check_idn(self) -> str:
        """Check the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()

    def get_output_state(self) -> bool:
        """Get the RF output state."""
        self.port.write("OUTP?")
        state = self.port.read()
        return state == 1

    def get_manual_control(self) -> bool:
        """Get the manual control state. Return True if locked, False if unlocked."""
        self.port.write("SYST:ULOC?")
        state = self.port.read()
        return state == 1

    def restart_firmware(self) -> None:
        """Restart the firmware of the device."""
        self.port.write(":SYST:REST")

    def shutdown_device(self) -> None:
        """Shutdown the device."""
        self.port.write(":SYST:SHUT")
