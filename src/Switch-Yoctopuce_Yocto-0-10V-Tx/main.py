# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: Yoctopuce Yocto-0-10V-Tx

from __future__ import annotations

from typing import Annotated, Any, ClassVar

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

from yoctopuce.yocto_api import YAPI, YRefParam  # noqa: E402 - Yoctopuce's library is in the driver's libs folder
from yoctopuce.yocto_voltageoutput import YVoltageOutput  # noqa: E402

Volts = Annotated[float, Unit("V"), Range(0.0, 10.0)]

SWEEP_VOLTAGE = "Voltage in V"
HUB_USERS = "Yoctopuce_Yocto-0-10V-Tx_usb_users"
"""Key in device_communication: how many instances of this driver use Yoctopuce's USB access."""


class Device(EmptyDevice):
    """Driver for one of the two 0 to 10 V outputs of a Yoctopuce Yocto-0-10V-Tx."""

    actions: ClassVar[list[str]] = ["set_voltage_low", "set_voltage_high"]
    """The buttons SweepMe! offers for the driver."""

    def __init__(self) -> None:
        """Define the returned variable; the module is reached in connect."""
        super().__init__()

        self.shortname = "Yocto-0-10V-Tx"

        self.variables = ["Voltage1"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        self.port_string: str = ""
        """The port: the module's serial number or its logical name, as Find Ports lists it."""
        self.channel: str = "1"
        """The output of the module: 1 or 2."""
        self.sweep_mode: str = SWEEP_VOLTAGE
        """The sweep mode of the module."""
        self.idle_voltage_text: str = "0"
        """The idle voltage in V as entered; empty to set none."""
        self.idle_voltage: float | None = 0.0
        """The idle voltage in V, checked in initialize; None to set none."""

        self.voltage_output: Any = None
        """Yoctopuce's object of the output."""
        self.uses_hub: bool = False
        """Whether this instance holds Yoctopuce's USB access."""
        self.voltage: float = float("nan")
        """The voltage in V read in measure."""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields: the output, and the voltage it idles at."""
        del parameters
        return {
            "SweepMode": [SWEEP_VOLTAGE, "None"],
            "Channel": ["1", "2"],
            "Idle voltage in V": "0",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the selections; the variable is named after the output."""
        self.port_string = str(parameters.get("Port", self.port_string))
        self.sweep_mode = str(parameters.get("SweepMode", SWEEP_VOLTAGE))
        self.channel = str(parameters.get("Channel", "1"))
        self.idle_voltage_text = str(parameters.get("Idle voltage in V", "0")).strip()

        self.variables = [f"Voltage{self.channel}"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

    def find_ports(self) -> list[str]:
        """Return the connected Yocto-0-10V-Tx modules, each by its serial number or logical name."""
        self.use_hub()
        try:
            YAPI.UpdateDeviceList()
            ports: list[str] = []
            output = YVoltageOutput.FirstVoltageOutput()
            while output is not None:
                name = str(output.get_module().get_friendlyName())
                if name not in ports:
                    ports.append(name)
                output = output.nextVoltageOutput()
        finally:
            self.release_hub()
        return ports

    def connect(self) -> None:
        """Reach the output of the module; instances of this driver share Yoctopuce's USB access."""
        if self.channel not in ("1", "2"):
            msg = f"The Yocto-0-10V-Tx has the outputs 1 and 2, not '{self.channel}'."
            raise ValueError(msg)
        self.use_hub()
        self.voltage_output = YVoltageOutput.FindVoltageOutput(f"{self.port_string}.voltageOutput{self.channel}")
        if not self.voltage_output.isOnline():
            self.voltage_output = None
            self.release_hub()
            msg = f"No Yocto-0-10V-Tx '{self.port_string}' is connected. Use Find Ports to list the modules."
            raise ConnectionError(msg)

    def disconnect(self) -> None:
        """Let go of the output; the last instance ends Yoctopuce's USB access."""
        self.voltage_output = None
        self.release_hub()

    def initialize(self) -> None:
        """Check the idle voltage and set it."""
        if self.idle_voltage_text == "":
            self.idle_voltage = None
        else:
            try:
                self.idle_voltage = float(self.idle_voltage_text)
            except ValueError:
                msg = f"The idle voltage must be a number in V or empty, not '{self.idle_voltage_text}'."
                raise ValueError(msg) from None
        if self.idle_voltage is not None:
            self.set_voltage(self.idle_voltage)

    def unconfigure(self) -> None:
        """Return to the idle voltage when the output is no longer used."""
        if self.idle_voltage is not None:
            self.set_voltage(self.idle_voltage)

    def apply(self) -> None:
        """Set the voltage of the sweep value."""
        if self.sweep_mode == SWEEP_VOLTAGE:
            self.set_voltage(float(self.value))

    def measure(self) -> None:
        """Read the voltage the output is set to."""
        self.voltage = self.get_voltage()

    def call(self) -> list[float]:
        """Return the voltage of the output."""
        return [self.voltage]

    # Communication commands

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the module's product name, serial number and firmware."""
        module = self.output().get_module()
        return (
            f"Yoctopuce {module.get_productName()}, SN {module.get_serialNumber()}, "
            f"firmware {module.get_firmwareRelease()}"
        )

    @command
    def set_voltage(self, value: Volts) -> None:
        """Set the output to a voltage in V."""
        self.output().set_currentVoltage(float(value))

    @command(returns=("voltage",), reads="setpoint")
    def get_voltage(self) -> Volts:
        """Return the voltage in V the output is set to; the module does not measure it."""
        return float(self.output().get_currentVoltage())

    @command(composite=True)
    def set_voltage_low(self) -> None:
        """Set the output to 0 V."""
        self.set_voltage(0.0)

    @command(composite=True)
    def set_voltage_high(self) -> None:
        """Set the output to 10 V."""
        self.set_voltage(10.0)

    @command
    def set_voltage_startup(self, value: Volts) -> None:
        """Set the voltage in V the output has when the module is powered, and keep it in the module."""
        output = self.output()
        output.set_voltageAtStartUp(float(value))
        output.get_module().saveToFlash()

    @command(returns=("voltage",), reads="setpoint")
    def get_voltage_startup(self) -> Volts:
        """Return the voltage in V the output has when the module is powered."""
        return float(self.output().get_voltageAtStartUp())

    # Helpers

    def output(self) -> Any:  # noqa: ANN401 - Yoctopuce's YVoltageOutput
        """Return the output, or say that the module is not there."""
        if self.voltage_output is None or not self.voltage_output.isOnline():
            msg = f"The Yocto-0-10V-Tx '{self.port_string}' is not connected (any more)."
            raise ConnectionError(msg)
        return self.voltage_output

    def use_hub(self) -> None:
        """Take Yoctopuce's USB access for this instance; the first instance opens it."""
        if self.uses_hub:
            return
        users = int(self.device_communication.get(HUB_USERS, 0))
        if users == 0:
            errmsg = YRefParam()
            if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
                msg = (
                    f"Yoctopuce's USB access failed: {errmsg.value}. Only one program can use the modules over USB; "
                    "is VirtualHub or another program running?"
                )
                raise ConnectionError(msg)
        self.device_communication[HUB_USERS] = users + 1
        self.uses_hub = True

    def release_hub(self) -> None:
        """Give Yoctopuce's USB access back; the last instance closes it and frees the library."""
        if not self.uses_hub:
            return
        self.uses_hub = False
        users = int(self.device_communication.get(HUB_USERS, 1)) - 1
        if users > 0:
            self.device_communication[HUB_USERS] = users
            return
        self.device_communication.pop(HUB_USERS, None)
        YAPI.UnregisterHub("usb")
        YAPI.FreeAPI()
