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
# * Module: SMU
# * Instrument: Agilent/Keysight E3631A

# ruff: noqa: ARG002  # a command does not send the channel: @command selects it through apply_selectors

from __future__ import annotations

from typing import Annotated, Any, Literal

from pysweepme import Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call).
# The instrument keeps the selected output (INST:SEL), so the channel is a stateful selector: @command selects it
# through apply_selectors only when it differs from the output selected last. TRACK25V is the +25V output with
# tracking on, which drives the -25V output to the same voltage with the opposite sign: it overlaps both 25 V outputs.
Channel = Annotated[
    Literal["+6V", "+25V", "-25V", "TRACK25V"],
    Selector(stateful=True, overlaps={"TRACK25V": ("+25V", "-25V")}),
]
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]

# Per channel the output selected (INST:SEL); TRACK25V also switches tracking on, set_tracking(False) switches it off
OUTPUTS: dict[str, str] = {"+6V": "P6V", "+25V": "P25V", "-25V": "N25V", "TRACK25V": "P25V"}
# The rated voltage and current of each channel; tracking is set by the positive voltage of the +25V output
VOLTAGE_RATINGS: dict[str, tuple[float, float]] = {
    "+6V": (0.0, 6.0),
    "+25V": (0.0, 25.0),
    "-25V": (-25.0, 0.0),
    "TRACK25V": (0.0, 25.0),
}
CURRENT_RATINGS: dict[str, float] = {"+6V": 5.0, "+25V": 1.0, "-25V": 1.0, "TRACK25V": 1.0}
# The channels as the GUI names them; sequences saved "Synced +/-25V" for tracking
GUI_CHANNELS: dict[str, str] = {"+6V": "+6V", "+25V": "+25V", "-25V": "-25V", "Synced +/-25V": "TRACK25V"}


class Device(EmptyDevice):
    """Driver for the Agilent/Keysight E3631A triple output power supply (+6 V, +25 V, -25 V)."""

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "E3631A"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        self.port_properties = {"timeout": 3}

        self.channel: str = "+6V"
        self.current_limit: float = 1.0
        self.average: int = 1

        self.v: float = float("nan")
        self.i: float = float("nan")

    def set_GUIparameter(self) -> dict[str, Any]:  # noqa: N802
        """Return the GUI fields of the SMU module."""
        return {
            "SweepMode": ["Voltage in V"],
            "Channel": list(GUI_CHANNELS),
            "RouteOut": ["Front"],
            "Compliance": 1,
            "Average": 1,
        }

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:  # noqa: N802
        """Store the user selections."""
        channel = str(parameter.get("Channel", "+6V"))
        self.channel = GUI_CHANNELS.get(channel, channel)
        self.current_limit = float(parameter.get("Compliance", 1.0))
        self.average = int(parameter.get("Average", 1))

    def apply_selectors(self, channel: str) -> None:
        """Select the output the following commands act on; TRACK25V switches tracking on as well.

        @command calls it when a command takes another channel than the one selected last, Instrument Control after
        connect() with the channel a bench entry binds. pysweepme remembers the selection on the port.
        """
        if channel == "TRACK25V":
            self.port.write("OUTP:TRAC ON")
        self.port.write(f"INST:SEL {OUTPUTS[channel]}")
        self.channel = channel

    def initialize(self) -> None:
        """Check the average and clear the status of the instrument."""
        if self.average < 1:
            msg = "Average smaller 1 not possible. Disable average by setting it to 1."
            raise ValueError(msg)
        self.clear_status()

    def deinitialize(self) -> None:
        """Nothing to do."""

    def configure(self) -> None:
        """Switch tracking off for a single 25 V output, then set the current limit of the channel."""
        if self.channel in ("+25V", "-25V"):
            self.set_tracking(False)
        self.set_current(self.channel, self.current_limit)

    def unconfigure(self) -> None:
        """Set the voltage of the channel back to zero."""
        self.set_voltage(self.channel, 0.0)

    def poweron(self) -> None:
        """Switch the outputs on (all three at once)."""
        self.set_output(True)

    def poweroff(self) -> None:
        """Switch the outputs off (all three at once)."""
        self.set_output(False)

    def apply(self) -> None:
        """Set the new sweep value."""
        self.set_voltage(self.channel, float(self.value))

    def measure(self) -> None:
        """Measure voltage and current of the channel, averaged."""
        voltages, currents = [], []
        for _ in range(self.average):
            voltages.append(self.get_voltage(self.channel))
            currents.append(self.get_current(self.channel))
        self.v = sum(voltages) / self.average
        self.i = sum(currents) / self.average

    def call(self) -> list[float]:
        """Return the measured voltage and current."""
        return [self.v, self.i]

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification (*IDN?): manufacturer, model, 0 and the firmware versions."""
        return self.port.query("*IDN?")

    @command(hazards="Resets every setting of the instrument to its default, the outputs switched off.")
    def reset_instrument(self) -> None:
        """Reset the instrument to its default settings (*RST)."""
        self.port.write("*RST")
        # the reset also selects another output and switches tracking off
        self.forget_selections()

    @command
    def clear_status(self) -> None:
        """Clear the status registers and the error queue (*CLS)."""
        self.port.write("*CLS")

    @command
    def set_voltage(self, channel: Channel, voltage: Volts) -> None:
        """Set the voltage of the channel: +6V 0 to 6 V, +25V and TRACK25V 0 to 25 V, -25V -25 to 0 V.

        With TRACK25V the -25V output follows with the opposite sign.
        """
        low, high = VOLTAGE_RATINGS[channel]
        if not low <= voltage <= high:
            msg = f"The voltage of the {channel} output must lie between {low:g} and {high:g} V, not {voltage:g} V."
            raise ValueError(msg)
        self.port.write(f"VOLT {voltage:1.4f}")

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
        """Set the current limit of the channel: +6V up to 5 A, the 25 V outputs up to 1 A."""
        high = CURRENT_RATINGS[channel]
        if not 0 <= current <= high:
            msg = f"The current limit of the {channel} output must lie between 0 and {high:g} A, not {current:g} A."
            raise ValueError(msg)
        self.port.write(f"CURR {current:1.4f}")

    @command(returns=("current",), reads="setpoint")
    def get_current_setpoint(self, channel: Channel) -> Amperes:
        """Return the current limit the channel is set to."""
        return float(self.port.query("CURR?"))

    @command(returns=("current",))
    def get_current(self, channel: Channel) -> Amperes:
        """Measure the current through the terminals of the channel."""
        return float(self.port.query("MEAS:CURR?"))

    @command
    def set_output(self, output: bool) -> None:
        """Switch the outputs on (True) or off (False): the E3631A switches all three at once."""
        self.port.write(f"OUTP {'ON' if output else 'OFF'}")

    @command(returns=("output",), reads="setpoint")
    def get_output(self) -> bool:
        """Return whether the outputs are on."""
        return self.port.query("OUTP?").strip() in ("1", "ON")

    @command
    def set_tracking(self, tracking: bool) -> None:
        """Switch tracking on (True) or off (False): the -25V output follows the +25V output with the opposite sign.

        Commands on TRACK25V switch it on by themselves.
        """
        self.port.write(f"OUTP:TRAC {'ON' if tracking else 'OFF'}")
        # a selection of TRACK25V promised tracking: the next command selects again
        self.forget_selections()

    @command(returns=("tracking",), reads="setpoint")
    def get_tracking(self) -> bool:
        """Return whether tracking is on: the -25V output follows the +25V output with the opposite sign."""
        return self.port.query("OUTP:TRAC?").strip() in ("1", "ON")

    @command
    def set_display(self, display: bool) -> None:
        """Switch the front panel display on (True) or off (False)."""
        self.port.write(f"DISP {'ON' if display else 'OFF'}")

    @command(returns=("display",), reads="setpoint")
    def get_display(self) -> bool:
        """Return whether the front panel display is on."""
        return self.port.query("DISP?").strip() in ("1", "ON")
