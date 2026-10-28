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

# SweepMe! driver
# * Module: SMU
# * Instrument: Rohde&Schwarz NGx

# ruff: noqa: ARG002  # a command does not send the channel: @command selects it through apply_selectors

from __future__ import annotations

import time
from typing import Annotated, Any, Literal

from pysweepme import Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call).
# The instrument keeps the selected output (INST:OUT<n>), so the channel is a stateful selector: @command selects it
# through apply_selectors only when it differs from the output selected last.
Channel = Annotated[int, Selector(stateful=True), Range(1, 4)]
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
VoltageRange = Literal["Auto", "20 V", "6 V"]
CurrentRange = Literal["Auto", "10 µA", "1 mA", "10 mA", "100 mA", "3 A", "10 A"]

# The measurement range commands per range choice
VOLTAGE_RANGE_COMMANDS: dict[str, str] = {
    "Auto": "SENS:VOLT:RANG:AUTO 1",
    "20 V": "SENS:VOLT:RANG 20",
    "6 V": "SENS:VOLT:RANG 6",
}
CURRENT_RANGE_COMMANDS: dict[str, str] = {
    "Auto": "SENS:CURR:RANG:AUTO 1",
    "10 µA": "SENS:CURR:RANG 0.0001",
    "1 mA": "SENS:CURR:RANG 0.001",
    "10 mA": "SENS:CURR:RANG 0.01",
    "100 mA": "SENS:CURR:RANG 0.1",
    "3 A": "SENS:CURR:RANG 3",
    "10 A": "SENS:CURR:RANG 10",
}

# NPLC per speed: the NGU series and the other models
NPLC_NGU: dict[str, float] = {"Very fast": 0, "Fast": 5, "Medium": 10, "Slow": 50, "Very slow": 100}
NPLC_OTHERS: dict[str, float] = {"Very fast": 0, "Fast": 0.1, "Medium": 1, "Slow": 10, "Very slow": 10}


class Device(EmptyDevice):
    """Driver for the Rohde & Schwarz NGx power supplies and source measure units (NGE, NGL, NGM, NGP, NGU)."""

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "NGx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "USBTMC", "GPIB", "TCPIP"]
        self.port_properties = {"timeout": 1}

        # "NGU" once connect() identified an NGU, which has one output and does not understand INST:OUT
        self.model: str | None = None

        self.port_string: str = ""
        self.source: str = "Voltage in V"
        self.protection: float = 5.0
        self.channel: int = 1
        self.current_range: str = "Auto"
        self.voltage_range: str = "Auto"
        self.speed: str = "Very fast"

        self.v: float = float("nan")
        self.i: float = float("nan")

    def set_GUIparameter(self) -> dict[str, Any]:  # noqa: N802
        """Return the GUI fields of the SMU module."""
        return {
            "SweepMode": ["Voltage in V", "Voltage in V (with wait)", "Current in A", "Current in A (with wait)"],
            "Channel": [1, 2],
            "RouteOut": ["Front"],
            "Compliance": 5.0,
            "Range": ["Auto", "10 µA", "1 mA", "10 mA", "100 mA", "3 A", "10 A"],
            "RangeVoltage": ["Auto", "20 V", "6 V"],
            "Speed": ["Very fast", "Fast", "Medium", "Slow", "Very slow"],
        }

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:  # noqa: N802
        """Store the user selections."""
        self.port_string = str(parameter.get("Port", ""))
        self.source = str(parameter.get("SweepMode", "Voltage in V"))
        self.protection = float(parameter.get("Compliance", 5.0))
        self.channel = int(parameter.get("Channel", 1))
        self.current_range = str(parameter.get("Range", "Auto"))
        self.voltage_range = str(parameter.get("RangeVoltage", "Auto"))
        self.speed = str(parameter.get("Speed", "Very fast"))

    def apply_selectors(self, channel: int) -> None:
        """Select the output the following commands act on, and let the stages act on it too.

        @command calls it when a command takes another channel than the one selected last, Instrument Control after
        connect() with the channel a bench entry binds. pysweepme remembers the selection on the port.
        """
        if self.model == "NGU":
            if int(channel) != 1:
                msg = f"The NGU has one output, channel {channel} does not exist."
                raise ValueError(msg)
        else:
            self.port.write(f"INST:OUT{int(channel)}")
        self.channel = int(channel)

    def connect(self) -> None:
        """Set the socket terminations and identify the model."""
        if self.port_string.startswith("TCPIP") and self.port_string.endswith("SOCKET"):
            self.port.port.write_termination = "\n"
            self.port.port.read_termination = "\n"

        # The model decides how outputs are selected (the NGU has one and no INST:OUT), so it is identified first
        if "NGU" in self.get_identification():
            self.model = "NGU"

    def initialize(self) -> None:
        """Reset the instrument."""
        self.reset_instrument()

    def deinitialize(self) -> None:
        """Nothing to do."""

    def configure(self) -> None:
        """Set ranges, limits, the start value and the speed of the selected channel."""
        self.set_voltage_range(self.channel, self.voltage_range)
        self.set_current_range(self.channel, self.current_range)

        if self.source.startswith("Voltage"):
            self.set_current_limit(self.channel, self.protection)
            self.set_voltage(self.channel, 0.0)
            self.set_current(self.channel, self.protection)
        elif self.source.startswith("Current"):
            self.set_voltage_limit(self.channel, self.protection)
            self.set_current(self.channel, 0.0)
            self.set_voltage(self.channel, self.protection)

        # The NPLC values are only known for the NGU series; those of the other models are not checked yet
        nplc = NPLC_NGU if self.model == "NGU" else NPLC_OTHERS
        if self.speed in nplc:
            self.set_nplc(self.channel, nplc[self.speed])

    def unconfigure(self) -> None:
        """Set the source back to zero and unlock the front panel."""
        if self.source.startswith("Voltage"):
            self.set_voltage(self.channel, 0.0)
        elif self.source.startswith("Current"):
            self.set_current(self.channel, 0.0)

        self.unlock_local_interface()

    def poweron(self) -> None:
        """Arm the output of the channel and switch the output generation on."""
        self.set_output_on(self.channel)
        self.set_generation_on()

    def poweroff(self) -> None:
        """Switch the output generation off and disarm the output of the channel."""
        self.set_generation_off()
        self.set_output_off(self.channel)

    def apply(self) -> None:
        """Set the new sweep value."""
        if self.source.startswith("Voltage"):
            self.set_voltage(self.channel, float(self.value))
        elif self.source.startswith("Current"):
            self.set_current(self.channel, float(self.value))

        # wait for achieving the set voltage or set current before other channels are changed
        if "(with wait)" in self.source:
            time.sleep(0.5)

    def measure(self) -> None:
        """Measure voltage and current of the channel."""
        self.v, self.i = self.read_data(self.channel)

    def call(self) -> list[float]:
        """Return the measured voltage and current."""
        return [self.v, self.i]

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification: Rohde&Schwarz,<device type>,<part number>/<serial number>,<firmware version>."""
        return self.port.query("*IDN?")

    @command(returns=("options",), reads="state")
    def get_options(self) -> str:
        """Return the options installed in the instrument."""
        return self.port.query("*OPT?")

    @command(hazards="Resets every setting of the instrument to its default.")
    def reset_instrument(self) -> None:
        """Reset the instrument to its default settings (*RST)."""
        self.port.write("*RST")
        # the reset also changes the selected output
        self.forget_selections()

    def set_channel(self, channel: int) -> None:  # check_driver: ignore DC004 - kept for scripts; no command
        """Select the output the following commands act on; kept for scripts, every command takes its channel now."""
        self.apply_selectors(channel=channel)

    @command
    def set_safety_limits(self, channel: Channel, safety_limits: bool) -> None:
        """Switch the safety limits of the channel on (True) or off (False)."""
        self.port.write(f"ALIM {1 if safety_limits else 0}")

    @command(returns=("safety_limits",), reads="setpoint")
    def get_safety_limits(self, channel: Channel) -> bool:
        """Return whether the safety limits of the channel are on."""
        return self.port.query("ALIM?").strip() in ("1", "ON")

    # check_driver: ignore DC008 - the upper limit has no command of its own; switching the limits on stays part of it
    @command(composite=True)
    def set_voltage_limit(self, channel: Channel, voltage_limit: Volts) -> None:
        """Switch the safety limits of the channel on and set the upper voltage limit."""
        self.set_safety_limits(channel, True)
        self.port.write(f"VOLT:ALIM {voltage_limit:1.3f}")

    @command(returns=("voltage_limit",), reads="setpoint")
    def get_voltage_limit(self, channel: Channel) -> Volts:
        """Return the upper voltage limit of the channel."""
        return float(self.port.query("VOLT:ALIM?"))

    # check_driver: ignore DC008 - the upper limit has no command of its own; switching the limits on stays part of it
    @command(composite=True)
    def set_current_limit(self, channel: Channel, current_limit: Amperes) -> None:
        """Switch the safety limits of the channel on and set the upper current limit."""
        self.set_safety_limits(channel, True)
        self.port.write(f"CURR:ALIM {current_limit:1.4f}")

    @command(returns=("current_limit",), reads="setpoint")
    def get_current_limit(self, channel: Channel) -> Amperes:
        """Return the upper current limit of the channel."""
        return float(self.port.query("CURR:ALIM?"))

    @command
    def set_voltage(self, channel: Channel, voltage: Volts) -> None:
        """Set the voltage of the channel; the output is switched on with set_output_on and set_generation_on."""
        self.port.write(f"VOLT {voltage:1.3f}")

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
        """Set the current of the channel; the output is switched on with set_output_on and set_generation_on."""
        self.port.write(f"CURR {current:1.4f}")

    @command(returns=("current",), reads="setpoint")
    def get_current_setpoint(self, channel: Channel) -> Amperes:
        """Return the current the channel is set to."""
        return float(self.port.query("CURR?"))

    @command(returns=("current",))
    def get_current(self, channel: Channel) -> Amperes:
        """Measure the current through the terminals of the channel."""
        return float(self.port.query("MEAS:CURR?"))

    @command
    def set_output_on(self, channel: Channel) -> None:
        """Arm the output of the channel; it delivers once set_generation_on switches the output generation on."""
        self.port.write("OUTP:SEL 1")

    @command
    def set_output_off(self, channel: Channel) -> None:
        """Disarm the output of the channel."""
        self.port.write("OUTP:SEL 0")

    @command(composite=True)
    def set_output(self, channel: Channel, output: bool) -> None:
        """Arm (True) or disarm (False) the output of the channel."""
        if output:
            self.set_output_on(channel)
        else:
            self.set_output_off(channel)

    @command(returns=("output",), reads="setpoint")
    def get_output(self, channel: Channel) -> bool:
        """Return whether the output of the channel is armed."""
        return self.port.query("OUTP:SEL?").strip() in ("1", "ON")

    @command
    def set_generation_on(self) -> None:
        """Switch the output generation on: every armed output delivers."""
        self.port.write("OUTP:GEN 1")

    @command
    def set_generation_off(self) -> None:
        """Switch the output generation off: no output delivers."""
        self.port.write("OUTP:GEN 0")

    @command(composite=True)
    def set_generation(self, generation: bool) -> None:
        """Switch the output generation on (True) or off (False), for every armed output at once."""
        if generation:
            self.set_generation_on()
        else:
            self.set_generation_off()

    @command(returns=("generation",), reads="setpoint")
    def get_generation(self) -> bool:
        """Return whether the output generation is on."""
        return self.port.query("OUTP:GEN?").strip() in ("1", "ON")

    @command
    def unlock_local_interface(self) -> None:
        """Unlock the front panel, which the first remote command has locked."""
        self.port.write("SYST:LOCal")

    @command(returns=("voltage", "current"))
    def read_data(self, channel: Channel) -> tuple[Volts, Amperes]:
        """Measure voltage and current of the channel at once."""
        voltage, current = self.port.query("READ?").split(",")
        return float(voltage), float(current)

    @command
    def set_voltage_range(self, channel: Channel, voltage_range: VoltageRange) -> None:
        """Set the voltage measurement range of the channel."""
        self.port.write(VOLTAGE_RANGE_COMMANDS[voltage_range])

    @command
    def set_current_range(self, channel: Channel, current_range: CurrentRange) -> None:
        """Set the current measurement range of the channel."""
        self.port.write(CURRENT_RANGE_COMMANDS[current_range])

    @command
    def set_nplc(self, channel: Channel, nplc: float) -> None:
        """Set the integration time in power line cycles: a high NPLC measures slowly and precisely."""
        self.port.write(f"NPLC {nplc:0.1f}")
