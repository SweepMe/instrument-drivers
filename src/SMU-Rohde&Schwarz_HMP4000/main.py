# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2026 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank D M S Sultan for providing the initial version of this driver.

# SweepMe! driver
# * Module: SMU
# * Instrument: Rohde&Schwarz HMP4000

# ruff: noqa: ARG002  # a command does not send the channel: @command selects it through apply_selectors

from __future__ import annotations

import time
from typing import Annotated, Any

from pysweepme.commands import Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call).
# The instrument keeps the selected channel (INST OUT<n>, user manual 8.2), so the channel is a stateful selector:
# @command selects it through apply_selectors only when it differs from the channel selected last. Channels 3 and 4
# exist only on some models (HMP2030/HMP40x0 and HMP4040); apply_selectors refuses the others once the model is known.
Channel = Annotated[int, Selector(stateful=True), Range(1, 4)]
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]

# Channels per model (user manual 8.2 and title page): the HMP2020 has two, the HMP2030 and HMP4030 three, the
# HMP4040 four channels. A model not listed here (another firmware spelling of *IDN?) is not checked.
CHANNEL_COUNTS: dict[str, int] = {"HMP2020": 2, "HMP2030": 3, "HMP4030": 3, "HMP4040": 4}
# The maximum current per channel the user manual states (2.1 and 5.1): 5 A for the HMP2030, 10 A for the
# HMP4030/HMP4040. The HMP2020 is not stated there (its channels differ), so it is not checked.
CURRENT_MAXIMA: dict[str, float] = {"HMP2030": 5.0, "HMP4030": 10.0, "HMP4040": 10.0}


class Device(EmptyDevice):
    """Driver for the Rohde & Schwarz HMP2020, HMP2030, HMP4030 and HMP4040 power supplies."""

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "HMP4000"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        # LAN is raw socket only (user manual 7.1.1), USB as USBTMC or virtual COM port (7.1.2), RS-232 (7.1.3) and
        # GPIB (7.1.4) through the optional interface modules
        self.port_types = ["COM", "USBTMC", "GPIB", "TCPIP"]
        self.port_properties = {
            "timeout": 1,
            "EOL": "\n",
            "baudrate": 9600,
        }

        # The raw GUI parameters; converted values are written to the attributes below in initialize and configure
        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.sweep_mode: str = "Voltage in V"
        self.compliance: float = 5.0
        self.channel: int = 1

        # The model from *IDN? (e.g. "HMP4040"), read in initialize; None while unknown
        self.model: str | None = None

        self.v: float = float("nan")
        self.i: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields of the SMU module."""
        return {
            "SweepMode": ["Voltage in V", "Voltage in V (with wait)", "Current in A", "Current in A (with wait)"],
            "Channel": [1, 2, 3, 4],
            "RouteOut": ["Front"],
            "Compliance": 5.0,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the user selections; the numbers are converted in initialize and configure."""
        self.gui_parameters = parameters
        self.port_string = str(parameters.get("Port", ""))
        self.sweep_mode = str(parameters.get("SweepMode", "Voltage in V"))

    def apply_selectors(self, channel: int) -> None:
        """Select the channel the following commands act on (INST OUT<n>, user manual 8.2).

        @command calls it when a command takes another channel than the one selected last, Instrument Control after
        connect() with the channel a bench entry binds. pysweepme remembers the selection per Port.
        """
        channel = int(channel)
        channel_count = CHANNEL_COUNTS.get(self.model or "")
        if channel_count is not None and channel > channel_count:
            msg = f"The {self.model} has {channel_count} channels, channel {channel} does not exist."
            raise ValueError(msg)
        self.port.write(f"INST OUT{channel}")
        self.channel = channel

    def connect(self) -> None:
        """Check the LAN resource and set the socket terminators; the HMP speaks raw socket only (user manual 7.1.1)."""
        if self.port_string.startswith("TCPIP"):
            if self.port_string.endswith("SOCKET"):
                self.port.port.write_termination = "\n"
                self.port.port.read_termination = "\n"
            else:
                msg = (
                    "The HMP does not support VXI-11 (a TCPIP resource ending with 'INSTR'). Use the raw socket "
                    "resource 'TCPIP::<ip address>::5025::SOCKET' instead."
                )
                raise ValueError(msg)

    def initialize(self) -> None:
        """Identify the model, then check the channel and the compliance the user chose."""
        identification = self.get_identification()
        # "Rohde&Schwarz,<device type>,<part number>/<serial number>,<firmware version>" (user manual 8.1)
        fields = identification.split(",")
        self.model = fields[1].strip() if len(fields) > 1 else None

        self._convert_gui_parameters()
        channel_count = CHANNEL_COUNTS.get(self.model or "")
        if channel_count is not None and self.channel > channel_count:
            msg = f"The {self.model} has {channel_count} channels, channel {self.channel} does not exist."
            raise ValueError(msg)
        if self.compliance < 0:
            msg = f"The compliance must not be negative, not {self.compliance:g}."
            raise ValueError(msg)

    def configure(self) -> None:
        """Set the limit of the quantity not swept and start the swept quantity at zero; the output stays off."""
        self._convert_gui_parameters()
        if self.sweep_mode.startswith("Voltage"):
            self.set_current(self.channel, self.compliance)
            self.set_voltage(self.channel, 0.0)
        elif self.sweep_mode.startswith("Current"):
            self.set_voltage(self.channel, self.compliance)
            self.set_current(self.channel, 0.0)

    def poweron(self) -> None:
        """Switch the output of the channel on."""
        self.set_output(self.channel, True)

    def poweroff(self) -> None:
        """Switch the output of the channel off; the outputs of the other channels stay as they are."""
        self.set_output(self.channel, False)

    def apply(self) -> None:
        """Set the new sweep value."""
        if self.sweep_mode.startswith("Voltage"):
            self.set_voltage(self.channel, float(self.value))
        elif self.sweep_mode.startswith("Current"):
            self.set_current(self.channel, float(self.value))

        # wait for the set voltage or current to settle before other channels are changed
        if "(with wait)" in self.sweep_mode:
            time.sleep(0.5)

    def measure(self) -> None:
        """Measure voltage and current of the channel."""
        self.v = self.get_voltage(self.channel)
        self.i = self.get_current(self.channel)

    def call(self) -> list[float]:
        """Return the measured voltage and current."""
        return [self.v, self.i]

    # Communication commands

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification: Rohde&Schwarz,<device type>,<part number>/<serial number>,<firmware version>."""
        return self.port.query("*IDN?").strip()

    @command(returns=("error",), reads="state")
    def get_error(self) -> str:
        """Return and remove the oldest entry of the error queue (SYST:ERR?); '0, "No error"' when it is empty."""
        return self.port.query("SYST:ERR?").strip()

    @command(warnings="Resets every setting of the instrument to its default, the outputs switched off.")
    def reset_instrument(self) -> None:
        """Reset the instrument to its default settings (*RST)."""
        self.port.write("*RST")
        # the reset may change the selected channel: the next command selects again
        self.forget_selections()

    @command
    def clear_status(self) -> None:
        """Clear the status registers, the error queue and the output buffer (*CLS)."""
        self.port.write("*CLS")

    @command
    def set_voltage(self, channel: Channel, voltage: Annotated[Volts, Range(0.0, 32.05)]) -> None:
        """Set the voltage of the channel, 0 to 32.05 V in 1 mV steps (user manual 8.3)."""
        self.port.write(f"VOLT {voltage:.3f}")

    @command(returns=("voltage",), reads="setpoint")
    def get_voltage_setpoint(self, channel: Channel) -> Volts:
        """Return the voltage the channel is set to."""
        return float(self.port.query("VOLT?"))

    @command(returns=("voltage",))
    def get_voltage(self, channel: Channel) -> Volts:
        """Measure the voltage at the terminals of the channel."""
        return float(self.port.query("MEAS:VOLT?"))

    @command
    def set_current(self, channel: Channel, current: Amperes) -> None:
        """Set the current limit of the channel in 0.1 mA steps: up to 5 A on the HMP2030, 10 A on the HMP40x0.

        The maximum of the HMP2020 is not checked (the user manual does not state it); the lower limit is the
        instrument's own (CURR? MIN, 0.5 mA in the manual's example), below it the instrument decides.
        """
        if current < 0:
            msg = f"The current limit must not be negative, not {current:g} A."
            raise ValueError(msg)
        current_maximum = CURRENT_MAXIMA.get(self.model or "")
        if current_maximum is not None and current > current_maximum:
            msg = f"The current limit of the {self.model} is at most {current_maximum:g} A, not {current:g} A."
            raise ValueError(msg)
        self.port.write(f"CURR {current:.4f}")

    @command(returns=("current",), reads="setpoint")
    def get_current_setpoint(self, channel: Channel) -> Amperes:
        """Return the current limit the channel is set to."""
        return float(self.port.query("CURR?"))

    @command(returns=("current",))
    def get_current(self, channel: Channel) -> Amperes:
        """Measure the current through the terminals of the channel."""
        return float(self.port.query("MEAS:CURR?"))

    @command
    def set_output_armed(self, channel: Channel, output_armed: bool) -> None:
        """Arm (True) or disarm (False) the output of the channel (OUTP:SEL).

        An armed output delivers while the general output is on. Arming alone switches nothing on;
        set_general_output(True) switches every armed output on at once.
        """
        self.port.write(f"OUTP:SEL {1 if output_armed else 0}")

    @command(warnings="Acts on every armed channel of the instrument, also on channels armed from the front panel.")
    def set_general_output(self, general_output: bool) -> None:
        """Switch the general output on (True) or off (False): every armed channel delivers, or none (OUTP:GEN)."""
        self.port.write(f"OUTP:GEN {1 if general_output else 0}")

    @command(
        composite=True,
        warnings="Switching on also switches the general output on: a channel armed from the front panel delivers too.",
    )
    def set_output(self, channel: Channel, output: bool) -> None:
        """Switch the output of the channel on (arm it and switch the general output on) or off (disarm it).

        Switching off disarms the channel only, so the other channels keep delivering; the general output stays on.
        """
        if output:
            self.set_output_armed(channel, True)
            self.set_general_output(True)
        else:
            self.set_output_armed(channel, False)

    @command(returns=("output",), reads="setpoint")
    def get_output(self, channel: Channel) -> bool:
        """Return whether the output of the channel is on (OUTP?): armed and the general output on."""
        return self.port.query("OUTP?").strip() in ("1", "ON")

    @command
    def unlock_local_interface(self) -> None:
        """Unlock the front panel for manual control (SYST:LOC)."""
        self.port.write("SYST:LOC")

    # Helpers

    def _convert_gui_parameters(self) -> None:
        """Convert the raw GUI parameters to typed attributes."""
        self.channel = int(self.gui_parameters.get("Channel", 1))
        self.compliance = float(self.gui_parameters.get("Compliance", 5.0))
