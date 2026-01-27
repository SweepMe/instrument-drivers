# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Keysight 816xx Lightwave Multimeter/Measurement System/Multichannel System

from __future__ import annotations

import struct
import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight 816xx Lightwave system."""

    description = """
    <h3>Keysight 816xx-Lightwave Multimeter/Measurement System/Multichannel System</h3>
    This driver supports the 8163A/B Lightwave Multimeter, 8164A/B Lightwave Measurement System, & 8166A/B Lightwave 
    Multichannel System. Can also work for HP 8135A.
    <h4>Parameters</h4>
    <ul>
    <li>Channel: If your power meter supports multiple channels. Otherwise, choose 1.</li>
    <li>Slot: Choose the slot your powermeter is connected to.</li>
    <li>Wavelength: If no wavelength should be set, set to 0.</li>
    <li>List length: might need to add +1.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "816xx"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Power"]
        self.units = ["W"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]
        # self.port_properties = {
        #     "timeout": 20,
        #     "baudrate": 9600,
        #     "stopbits": 1,
        #     "parity": "N",
        #     "EOL": "\n",
        # }

        # Measurement parameters
        self.slot: str = "1"  # Slot number of the power meter
        self.channel: str = "1"  # In case the connected power meter has multiple channels
        self.averaging_time: str = "0.1"  # in seconds
        self.power_units = ["W", "dBm"]
        self.power_unit: str = "W"  # can be "W" or "dBm"
        self.automatic_power_ranging: bool = True  # Enable automatic power ranging
        self.wavelength: str = "1550"
        self.measured_power: float = float("nan")  # Measured power value, initialized to NaN

        # List mode
        self.list_mode: bool = False  # If True, the device will operate in list mode
        self.list_length: int = 10  # Length of the list in list mode, default is 10
        self.list_averaging: float = 0.1  # Averaging time in seconds for list mode

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "Channel": ["1", "2"],
            "Slot": "1",
            "Power unit": self.power_units,
            "Automatic Power Ranging": True,
            "Averaging in s": 0.1,
            "Wavelength in nm": 1550,  # Default wavelength, can be changed later
            # "Reference State": ["Absolute", "Relative"],
            "Mode": ["Single", "Parameter Logging"],
        }

        if parameters.get("Mode") == "Parameter Logging":
            new_parameters.update({
                "Data points": "10",
                "Averaging in s": "0.1",
                "Trigger": ["External"],
            })

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", "1")
        self.slot = parameters.get("Slot", "1")

        self.power_unit = parameters.get("Power unit", "W")
        self.units = [self.power_unit]

        self.automatic_power_ranging = parameters.get("Automatic Power Ranging", True)
        self.averaging_time = parameters.get("Averaging in s", "0.1")
        self.wavelength = parameters.get("Wavelength in nm", "1550")

        self.list_mode = parameters.get("Mode", "Single") == "Parameter Logging"
        if self.list_mode:
            self.list_length = int(parameters.get("Data points", "10"))
            self.list_averaging = float(parameters.get("Averaging in s", "0.1"))

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_power_unit(self.power_unit)
        self.set_averaging_time(float(self.averaging_time))
        # TODO: Add power range setting
        self.set_automatic_power_ranging(bool(self.automatic_power_ranging))  # Enable automatic power ranging
        self.set_wavelength(float(self.wavelength))

        if self.list_mode:
            self.port.write("trigger:configuration 1") # activate trigger input connector page 214
            self.configure_input_trigger_response("sme")
            self.port.write(f"sense{self.slot}:chan{self.channel}:function:parameter:logging {self.list_length},{self.list_averaging}")

            # see 208 page - trig not armed
            # print("Trigger armed: ", self.port.query(f"trig{self.slot}:chan{self.channel}:inp:rearm?"))  # This should return "0" if the trigger is not armed
            self.port.write("trig:inp:rearm")
        else:
            # Set the software trigger system to non-continuous mode
            self.port.write(f":init{self.slot}:cont OFF")

        # TODO: Decide if additional methods are needed: Upper power limit, reference state

    def start(self) -> None:
        """This function can be used to do some first steps before the acquisition of a measurement point starts."""
        if self.list_mode:
            # trig:inp:rearm
            self.port.write(f"sense{self.slot}:chan{self.channel}:function:state LOGG,start")

            # page 210
            """
            Generally, a continuous sweep can only be started if:
            the trigger frequency, derived from the sweep speed and sweep step, is <= 40kHz, or <=1MHz for 81602A, 81606A, 81607A,
            81608A, and 81960A.
            the number of triggers, calculated from the sweep span and sweep span, is <=100001
            the start wavelength is less than the stop wavelength.
            In addition, a continuous sweep with lambda logging requires:
            the trigger output to be set to step finished
            modulation set to coherence control or off.
            """

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        # TODO: As the trigger is run for all channels, implement a device_communication method to trigger only once
        # list mode uses external trigger
        # TODO: Implement a method to set the trigger source
        if not self.list_mode:
            self.initiate_software_trigger()

    def request_result(self) -> None:
        """Wait until the measurement is complete and the results are ready to be read."""
        if self.list_mode:
            # If the averaging time is much smaller than the sweep time of the laser, the timeout needs to be increased
            expected_time = self.list_length * self.list_averaging
            timeout_s = max(expected_time * 2, 10)

            while True:
                if self.is_run_stopped():
                    break

                status = self.port.query(f"sens{self.slot}:chan{self.channel}:func:stat?")

                if "COMPLETE" in status:
                    break

                if timeout_s <= 0:
                    msg = f"Sweep did not finish within the timeout period of {max(expected_time * 2, 10)}s."
                    raise TimeoutError(msg)

                time.sleep(0.1)
                timeout_s -= 0.1

    def read_result(self) -> None:
        """Read the measured data.

        Do not split between request and read results to prevent communication problems when reading multiple channels.
        """
        if self.list_mode:
            self.measured_power = self.get_list_mode_data()

            # stop logging
            self.port.write(f"sens{self.slot}:chan{self.channel}:func:state logg,stop")
        else:
            result = self.port.query(f":fetc{self.slot}:chan{self.channel}:scal:pow:dc?")
            try:
                measured_power = float(result.strip())
            except ValueError:
                measured_power = float("nan")

            error_value = 3.402823E38
            if measured_power == error_value:
                measured_power = float("nan")

            self.measured_power = measured_power

    def call(self) -> list[float] | list[list[float]]:
        """Return the power as a list to prevent SweepMe! from interpreting the list mode results as individual values."""
        return [self.measured_power]

    def set_averaging_time(self, averaging_time: float) -> None:
        """Set the averaging time for the power measurement."""
        self.port.write(f"sens{self.slot}:chan{self.channel}:pow:atim {averaging_time}")
        self.wait_for_opc()

    def set_automatic_power_ranging(self, enable: bool = True) -> None:
        """Enable or disable automatic power ranging.

        Can only be set for both channels at the same time.
        """
        if enable:
            self.port.write(f"sens{self.slot}:pow:rang:auto on")
        else:
            self.port.write(f"sens{self.slot}:pow:rang:auto off")
        self.wait_for_opc()

    # Wrapper Functions

    def set_power_unit(self, unit: str) -> None:
        """Set the power unit to either W or dBm."""
        if unit.lower() not in ["w", "dbm"]:
            msg = "Unit must be 'W' or 'dBm'."
            raise ValueError(msg)
        elif unit.lower() == "dbm":
            unit = "DBM"
        elif unit.lower() == "w":
            unit = "Watt"
        self.port.write(f"sens{self.slot}:chan{self.channel}:pow:unit {unit}")
        self.wait_for_opc()

    def set_wavelength(self, wavelength_nm: float) -> None:
        """Sets the sensor wavelength.

        Frequent use of this command can conflict with the timing of autoranging in some configurations.
        Auto range can be disabled before and enabled after the command if needed.
        The changes are applied to all channels
        """
        if wavelength_nm == 0:
            return

        if wavelength_nm < 0:
            msg = f"Invalid wavelength: {wavelength_nm}"
            raise ValueError(msg)
        self.port.write(f"sens{self.slot}:pow:wav {wavelength_nm}nm")
        self.wait_for_opc()

    def wait_for_opc(self, timeout_s: float = 10.0) -> None:
        """Wait for the operation complete (OPC) bit to be set."""
        start_time = time.time()
        while time.time() - start_time < timeout_s:
            status = self.port.query("*OPC?")
            if status.strip() == "1":
                break

    def set_reference_state(self, reference: str = "absolute") -> None:
        """Set the reference state of the power measurement to either absolute or relative."""
        reference = reference.strip().lower()
        if reference not in ("absolute", "relative"):
            msg = f"Invalid reference state: {reference}. Must be 'absolute' or 'relative'."
            raise ValueError(msg)

        if reference == "absolute":
            self.port.write(f"sens{self.slot}:pow:ref:stat 0")
        elif reference == "relative":
            self.port.write(f"sens{self.slot}:pow:ref:stat 1")

        self.wait_for_opc()

    def initiate_software_trigger(self) -> None:
        """Initiates the software trigger system and completes one full trigger cycle.

        Can only be sent to primary channel, the secondary channel will be also be affected.
        """
        self.port.write(f":init{self.slot}:imm")

    def configure_input_trigger_response(self, response: str = "ign") -> None:
        """Configure the input trigger response for the device.

        IGNore: ignore incoming triggers.
        SMEasure: Start a single measurement. If a measurement function is active (func:stat), one sample is performed and stored in an array
        CMEasure: Start a complete measurement. If a measurement function is active, a complete measurement function is performed
        NEXTstep: Perform next step of a stepped sweep
        SWSart: Start a sweep cycle.

        Affects all tunable laser modules, power meter, and return loss modules.
        """
        response = response.strip().lower()
        if response not in ["ign", "sme", "cme", "next", "sws"]:
            msg = f"Invalid trigger response: {response}. Must be 'ign', 'sme', 'cme', 'next', or 'sws'."
            raise ValueError(msg)

        self.port.write(f"trig{self.slot}:chan{self.channel}:inp {response}")

    def get_list_mode_data(self) -> list[float]:
        """Get the data from the list mode measurement."""
        self.port.write(f"sens{self.slot}:chan{self.channel}:func:res?")
        binary_data = self.port.port.read_raw()

        # Strip SCPI header
        if not binary_data.startswith(b'#'):
            msg = "Data does not start with SCPI binary block header"
            raise ValueError(msg)
        n_digits = int(chr(binary_data[1]))
        data_len = int(binary_data[2:2 + n_digits].decode())
        header_len = 2 + n_digits
        power_data_binary = binary_data[header_len:header_len + data_len]

        # Each value is a 4-byte float (little-endian)
        num_values = len(power_data_binary) // 4
        return list(struct.unpack("<" + "f" * num_values, power_data_binary))

    # Currently unused wrapper functions

    def get_identification(self) -> str:
        """Return the identification string of the device."""
        return self.port.query("*IDN?").strip()

    def get_averaging_time(self) -> float:
        """Get the current averaging time for the power measurement."""
        response = self.port.query(f"sens{self.slot}:chan{self.channel}:pow:atim?")
        return float(response.strip())

    def get_wavelength(self) -> float:
        """Get the current wavelength setting of the power meter."""
        response = self.port.query(f"sens{self.slot}:chan{self.channel}:pow:wav?")
        return float(response.strip())


