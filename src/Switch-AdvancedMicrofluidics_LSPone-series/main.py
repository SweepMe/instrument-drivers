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
#
# SweepMe! driver
# * Module: Switch
# * Instrument: AdvancedMicrofluidics LSPone-series

from __future__ import annotations

import contextlib
import time
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice

import amfTools


class Device(EmptyDevice):
    """Driver for the AdvancedMicrofluidics LSPone-series."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "LSPone-series"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Valve position", "Flow rate", "Plunger current"]
        self.units = ["", "µl/min", "mA"]  # TODO: update units
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = False
        # self.port_types = ["GPIB", "COM", "TCPIP"]
        self.amf: amfTools.AMF | None = None

        # Configuration parameters
        self.speed_modes: dict[str, int] = {
            "Standard": 2,
            "Low": 1,
            "Ultra Low": 0,
        }
        self.speed: str = "Standard"
        self.plunger_force_modes: dict[str, int] = {
            "High force": 0,
            "Normal force": 1,
            "Medium force": 2,
            "Low force": 3,
        }
        self.plunger_force_mode: str = "Normal force"

        # Measurement parameters


    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Volume": "10",
            "Volume unit": ["µl", "ml", "l"],
            "": None,
            "Flow": 0.0,
            "Time unit": ["s", "min"],
            " ": None,
            "Valve": 1,
            "Speed": list(self.speed_modes.keys()),
            "Syringe volume in µl": 5000,
            "Plunger force": list(self.plunger_force_modes.keys()),
            "Wait for pump finish": False,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.volume = int(float(parameters.get("Volume", "10")))
        volume_unit = parameters.get("Volume unit", "µl")
        self.flow = parameters.get("Flow", 0.0)
        self.speed = parameters.get("Speed", "Standard")
        self.valve = int(parameters.get("Valve", "1"))
        self.syringe_volume = int(parameters.get("Syringe volume in µl", "5000"))
        self.plunger_force_mode = parameters.get("Plunger force", "Normal force")
        self.wait_for_pump_finish = parameters.get("Wait for pump finish", False)

    def find_ports(self) -> list[str]:
        """Return a list of available ports for the device."""
        list_amf = amfTools.util.getProductList(silent_mode=True)
        if not list_amf:
            device_list = ["No AMF product found"]
        else:
            device_list = [amf_info.comPort for amf_info in list_amf]

        return device_list

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        list_amf = amfTools.util.getProductList(silent_mode=True)
        for amf_info in list_amf:
            if amf_info.comPort == self.port_string:
                self.amf = amfTools.AMF(amf_info)
                break
        else:
            raise ConnectionAbortedError(f"AMF product on port {self.port_string} not found. Please check your connections")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        with contextlib.suppress(Exception):
            self.amf.disconnect()

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # TODO: Check if homing is desired behavior at initialization
        # if not self.amf.getHomeStatus():
        #     self.amf.home()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # TODO: for low flow rates, use setSpeedLowFlow or setSpeedUltraLowFlow
        self.set_valve(self.valve)
        self.amf.setSpeed(int(self.speed))
        self.amf.setSyringeSize(self.syringe_volume)
        self.amf.setPlungerForce(self.plunger_force_modes[self.plunger_force_mode])

    def reconfigure(self, parameters, keys) -> None:
        if "Flow" in keys:
            self.flow = float(parameters["Flow"])
            self.set_flow_rate(self.flow)
        if "Volume" in keys:
            self.volume = int(float(parameters["Volume"]))

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        # TODO: decide if this is correct
        # self.amf.hardStop()

    def signin(self) -> None:
        """This function is called whenever a module higher up in the sequencer changes its sweep value."""
        # TODO: currently this is pumping/dispensing until the volume is reached instead of pumping/dispensing the given volume
        self.pump_volume(volume=self.volume)

    def trigger_ready(self) -> None:
        """Optional: wait until the pump operation is finished before starting further measurements."""
        if self.wait_for_pump_finish:
            self.wait_for_pump(timeout_seconds=300)  # wait up to 5 minutes

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        valve_position = self.amf.getValvePosition()
        flow_rate = self.amf.getFlowRate()
        plunger_current = self.amf.getPlungerCurrent()  # TODO: check if *10, /10, or nothing is needed
        return [valve_position, flow_rate, plunger_current]

    # Wrapper Commands

    def pump_volume(self, volume: int) -> None:
        """Pump until the specified volume in µl is filled in the syringe."""
        self.amf.pumpVolume(
            volume=volume,
            block=False,  # Wait until the pumping is done
        )

    def set_flow_rate(self, flow_rate: float) -> None:
        """Set the flow rate in µl/min."""
        self.amf.setFlowRate(
            flowRate=flow_rate,
            speedMode=self.speed_modes[self.speed],
            syringeVolume=self.syringe_volume,
            silentMode=False,  # TODO: switch to True after testing
        )

    def set_valve(self, valve_number: int) -> None:
        """Set the valve to the specified port number."""
        self.amf.valveShortestPath(
            target=valve_number,
        )

    def wait_for_pump(self, timeout_seconds: int) -> None:
        time_start = time.time()
        while True:
            if self.is_run_stopped():
                break

            if time.time() - time_start > timeout_seconds:
                break

            status = self.amf.getPumpStatus()
            if status == "0":  # Done
                break
