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

        self.variables = ["Frequency", "Power", "Impedance"]
        self.units = ["Hz", "dBm", "Ohm"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.frequency: float = 2.2e9
        self.amplitude: float = 0.1


    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Power in dBm"],
            # "Waveform": ["Pulse"],
            "PeriodFrequency": ["Frequency in Hz"],
            "PeriodFrequencyValue": 2e-6,
            "AmplitudeHiLevel": ["Amplitude in V"],
            "AmplitudeHiLevelValue": 1.0,
            # "OffsetLoLevel": ["Low level in V"],  # "Offset in V"],
            # "OffsetLoLevelValue": 0.0,
            # "DelayPhase": ["Delay in s"],  # "Phase in deg"],
            # "DelayPhaseValue": 0.0,
            # "DutyCyclePulseWidth": ["Pulse width in s"],  # "Duty cycle in %",],
            # "DutyCyclePulseWidthValue": 1e-6,
            # "RiseTime": 100e-9,
            # "FallTime": 100e-9,
            # "Impedance": ["50", "1e6"],
            # "OperationMode": ["Range 20 V (slow)", "Range 5 V (fast)"]
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get the GUI parameters."""
        self.port_string = parameter["Port"]

        self.sweep_mode = parameter["SweepMode"]
        self.frequency = float(parameter["PeriodFrequencyValue"])
        self.amplitude = float(parameter["AmplitudeHiLevelValue"])

        # self.identifier = "Keithley_4200-SCS_" + self.port_string
        #
        # self.waveform = parameter["Waveform"]
        # self.periodfrequency = parameter["PeriodFrequency"]
        # self.periodfrequencyvalue = float(parameter["PeriodFrequencyValue"])
        # self.amplitudehilevel = parameter["AmplitudeHiLevel"]
        # self.amplitudehilevelvalue = float(parameter["AmplitudeHiLevelValue"])
        # self.offsetlolevel = parameter["OffsetLoLevel"]
        # self.offsetlolevelvalue = float(parameter["OffsetLoLevelValue"])
        # self.dutycyclepulsewidth = parameter["DutyCyclePulseWidth"]
        # self.dutycyclepulsewidthvalue = float(parameter["DutyCyclePulseWidthValue"])
        # self.delayphase = parameter["DelayPhase"]
        # self.delayphasevalue = float(parameter["DelayPhaseValue"])
        # self.impedance_value = parameter["Impedance"]
        #
        # self.rise_time = parameter["RiseTime"]
        # self.fall_time = parameter["FallTime"]
        #
        # self.channel = parameter["Channel"]
        #
        # self.card_name = self.channel.split("-")[0].strip()
        # self.pulse_channel = int(self.channel.split("-")[1][-1])
        #
        # self.shortname = "4200-SCS %s" % parameter["Channel"]

    def connect(self) -> None:
        """Connect to the device."""
        self.port.write("*RST")
        # self.port.write("*CLS")
        self.port.write("*IDN?")
        ret = self.port.read()
        print(f"Connected to: {ret}")

    def initialize(self) -> None:
        """Initialize the device."""

    def configure(self) -> None:
        """Configure the device."""
        self.set_manual_control(False)

        self.set_power_mode("CW")
        self.set_power_unit("V")
        self.set_power_level(self.amplitude)

        self.set_frequency_mode("CW")
        self.set_frequency(self.frequency)

        self.set_output_state(True)

    def unconfigure(self) -> None:
        """Unconfigure the device."""
        self.set_output_state(False)
        self.set_manual_control(True)

    def apply(self) -> None:
        """Apply new sweep value."""
        self.value = float(self.value)

        if self.sweep_mode.startswith("Frequency"):
            self.set_frequency(self.value)
        elif self.sweep_mode.startswith("Power"):
            self.set_power_level(self.value)

    def measure(self) -> None:
        """Retrieve measured values."""

    def call(self) -> tuple:
        """Return the measured values."""
        measured_frequency = self.get_frequency()
        measured_power = self.get_power_level()
        measured_impedance = self.get_impedance()
        return measured_frequency, measured_power, measured_impedance

    """Wrapper Functions"""

    def run_self_test(self) -> bool:
        """Run the self test."""
        self.port.write("*TST?")
        ret = self.port.read()
        return ret == "0"

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the RF output."""
        self.port.write(f"SOUR:FREQ {frequency}")

    def get_frequency(self) -> float:
        """Get the frequency of the RF output."""
        self.port.write("SOUR:FREQ?")
        return float(self.port.read())

    def set_frequency_mode(self, mode: str) -> None:
        """Set the frequency mode of the RF output to either 'CW' or 'Sweep'."""
        state = "SWE" if mode == "SWE" else "CW"
        self.port.write(f":SOUR:FREQ:MODE {state}")

    def set_power_level(self, power_level: float) -> None:
        """Set the power level of the RF output."""
        self.port.write(f"SOUR:POW:POW {power_level}")

    def get_power_level(self) -> float:
        """Get the power level of the RF output."""
        self.port.write("SOUR:POW:POW?")
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

    def get_power_unit(self) -> str:
        """Get the power unit of the RF output."""
        self.port.write("UNIT:POW?")
        return self.port.read()

    def set_output_state(self, set_on: bool) -> None:
        """Set the HF output state."""
        state = "ON" if set_on else "OFF"
        self.port.write(f":OUTP {state}")

    def get_output_state(self) -> bool:
        """Get the HF output state."""
        self.port.write("OUTP?")
        state = self.port.read()
        return state == 1

    def get_impedance(self) -> float:
        """Get the impedance of the RF output."""
        self.port.write(":OUTP:IMP?")
        return float(self.port.read())

    def set_manual_control(self, is_locked: bool) -> None:
        """Lock or unlock manual control through the keyboard of the device."""
        state = "ON" if is_locked else "OFF"
        self.port.write(f"SYST:KLOC {state}")

    def get_manual_control(self) -> bool:
        """Get the manual control state. Return True if locked, False if unlocked."""
        self.port.write("SYST:KLOC?")
        state = self.port.read()
        return state == 1

    def restart_firmware(self) -> None:
        """Restart the firmware of the device."""
        self.port.write(":SYST:REST")

    def shutdown_device(self) -> None:
        """Shutdown the device."""
        self.port.write(":SYST:SHUT")

    """ Check if needed. """

    def set_data_format(self) -> None:
        """Set the format of the return data from the device."""
        command = "FORM ASC"  # for ASCII
        command = "FORM PACK"  # for packed binary
        self.port.write(command)

    """
    SOURce Subsystem for configuring digital and analog signals.

    Subsystems: AM, CORR, FM, FREQU, INP, LIST, MOD, PGEN, PHAS, PM, POW, PULM, ROSC, STER, SWE
    """
    # Probably need AM functions



