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

# SweepMe! driver
# * Module: SMU
# * Instrument: Agilent B1500

from __future__ import annotations
from collections import OrderedDict

from pysweepme.EmptyDeviceClass import EmptyDevice

import numpy as np
import time


class Device(EmptyDevice):
    description = """<div class="device-description">
      <h3>Agilent B1500A - Semiconductor Parameter Analyzer</h3>
    
      <p><strong>Overview</strong>: This driver controls the Agilent B1500A for single measurements and synchronized list sweeps. It exposes voltage/current sources, measurement timing and list sweep features used for multi‑channel experiments.</p>
    
      <h4>Prerequisites</h4>
      <ul>
        <li>The helper application \"Start EasyExpert\" must be running on the PC. Before running sweeps, minimize IO Control and close any active EasyExpert GUI instances to avoid resource conflicts.</li>
        <li>Ensure the correct GPIB/USB port is selected and the instrument is powered and addressed.</li>
      </ul>
    
      <h4>List Mode (synchronized multi‑channel sweeps)</h4>
      <ul>
        <li>When using list mode, the device returns the programmed source values (not measured source values).</li>
        <li>A branch can contain multiple channels; if any channel in a branch uses list mode, the whole branch is treated as a list sweep.</li>
        <li>Single‑value channels inside a list branch produce lists where start = stop = value.</li>
        <li>All channels participating in the same list sweep must share the same list length, hold time and delay time.</li>
        <li>Timestamps are provided and are normalized relative to the list master channel.</li>
        <li>For longer measurements the timeout might not be sufficient. Create a custom driver version and increase self.port_properties = {
            "timeout": 30}.</li>
      </ul>
    
      <h4>Usage guidance</h4>
      <ul>
        <li>Use list mode for synchronized, multi‑channel acquisitions (e.g. concurrent source/measure sequences).</li>
        <li>Use single measurement mode for isolated, on‑demand readings.</li>
        <li>Check range, compliance and averaging settings before starting a sweep to avoid measurement errors or instrument protection trips.</li>
      </ul>
    </div>"""

    def __init__(self):

        EmptyDevice.__init__(self)

        self.channels = ["CH1", "CH2", "CH3", "CH4", "CH5", "CH6"]

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["GPIB", "USB"]
        self.port_properties = {
            "timeout": 30,
            # "delay": 0.1,
        }
        self.port_string: str = ""
        self.channel: int = 1
        self.shortname = f"B1500 Ch{self.channel}"

        self.driver_port_string: str = ""
        """A unique identifier for this driver instance and port combination. Used as key in device_communication."""

        self.current_ranges = OrderedDict([
            ("Auto", "0"),
            ("1 pA limited auto", "8"),
            ("10 pA limited auto", "9"),
            ("100 pA limited auto", "10"),
            ("1 nA limited auto", "11"),
            ("10 nA limited auto", "12"),
            ("100 nA limited auto", "13"),
            ("1 μA limited auto", "14"),
            ("10 μA limited auto", "15"),
            ("100 μA limited auto", "16"),
            ("1 mA limited auto", "17"),
            ("10 mA limited auto", "18"),
            ("100 mA limited auto", "19"),
            ("1 A limited auto", "20"),
        ])
        self.current_range: str = "0"
        self.voltage_range = "0"  # voltage autoranging

        # Measurement parameters
        self.route_out: str = "Rear"
        self.source: str = "Voltage in V"

        self.protection: float = 100e-6
        self.speed: str = "Fast"
        self.average: int = 1

        self.measured_current: float | list[float] = 0.0
        self.measured_voltage: float | list[float] = 0.0

        # Pulse parameters - not yet implemented in the code

        # List sweep parameters
        self.use_list_mode: bool = False  # whether the user has selected 'list sweep' as sweep value
        self.list_master: bool = False  # The first channel that configures the list mode and starts the measurement
        self.list_follower: bool = False  # If another channel is the list master, this channel becomes a list follower. No matter if it is set to single or list mode

        self.list_modes = {
            "linear": 1,
            "logarithmic": 2,
            "linear dual": 3,  # start - stop - start
            "logarithmic dual": 4,  # start - stop - start
        }
        self.list_mode: int = -1  # linear
        self.list_start: float = 0.0
        self.list_stop: float = 1.0
        self.list_steps: int = 10
        self.list_hold: float = 0.0
        self.list_delay: float = 0.0

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "Current ín A"],
            "Channel": self.channels,
            "RouteOut": ["Rear"],
            "Speed": ["Fast", "Medium", "Slow"],
            "Range": list(self.current_ranges.keys()),
            "Compliance": "100e-6",
            "Average": "1",

            # List Mode Parameters
            "ListSweepCheck": False,
            "ListSweepType": ["Sweep"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Points (lin.):", "Points (log.):"],
            "ListSweepStepPointsValue": 10,
            "ListSweepDual": False,
            "ListSweepHoldtime": "0.0",
            "ListSweepDelaytime": "0.0",
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.route_out = parameter["RouteOut"]
        self.source = parameter["SweepMode"]
        self.current_range = self.current_ranges[parameter["Range"]]
        self.speed = parameter["Speed"]

        try:
            self.protection = float(parameter["Compliance"])
        except ValueError:
            self.protection = -1  # set an invalid value to raise an error later

        try:
            self.average = int(parameter["Average"])
        except ValueError:
            self.average = -1  # set an invalid value to raise an error later

        try:
            self.channel = int(parameter["Channel"].strip()[-1])
        except ValueError:
            self.channel = -1  # set an invalid value to raise an error later

        self.shortname = f"B1500 CH{self.channel}"

        # List Mode Parameters
        try:
            sweep_value = parameter.get("SweepValue", "")
        except KeyError:
            # this might be the case when driver is used with pysweepme
            # then, "SweepValue" is not defined during set_GUIparameter
            sweep_value = None

        if sweep_value == "List sweep":
            self.use_list_mode = True
            self.handle_list_sweep_parameter(parameter)

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        if parameter["ListSweepType"] != "Sweep":
            msg = "Only 'Sweep' type is currently supported for Agilent B1500 list sweeps."
            raise ValueError(msg)

        # TODO: handle exceptions
        try:
            self.list_start = float(parameter["ListSweepStart"])
            self.list_stop = float(parameter["ListSweepEnd"])
            self.list_steps = int(parameter["ListSweepStepPointsValue"])
            self.list_hold = float(parameter["ListSweepHoldtime"])
            self.list_delay = float(parameter["ListSweepDelaytime"])
        except ValueError:
            pass

        step_type = parameter["ListSweepStepPointsType"]
        if step_type.startswith("Points (lin.)"):
            self.list_mode = self.list_modes["linear"] if not parameter["ListSweepDual"] else self.list_modes[
                "linear dual"]

        elif step_type.startswith("Points (log.)"):
            self.list_mode = self.list_modes["logarithmic"] if not parameter["ListSweepDual"] else self.list_modes[
                "logarithmic dual"]

        # Add time stamp variable if list mode is used. Init the lists instead of appending to avoid duplicates when get_GUIparameter is called multiple times.
        self.variables = ["Voltage", "Current", "Time Stamp"]
        self.units = ["V", "A", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]


    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.driver_port_string = "Agilent_B1500_" + self.port_string

        # initialize commands only need to be sent once, so we check here whether another instance of the same driver
        # AND same port did it already. If not, this instance is the first and has to do it.
        if not self.driver_port_string in self.device_communication:
            self.port.write("*RST")  # reset to initial settings
            self.port.write("BC")  # buffer clear
            self.port.write("AZ 0")  # Auto-Zero off for faster measurements
            self.port.write("FMT 2")  # use to change the output format. This will be overwritten if list mode is used

            # if initialize commands have been sent, we can add the driver_port_string to the dictionary that is seen by
            # all drivers
            self.device_communication[self.driver_port_string] = {
                "is_initialized": True,
                "channels": [self.channel],
                "list_master_channel": -1,
                "list_length": 0,
                "list_hold": 0.0,
                "list_delay": 0.0,
                "list_results": {},
            }

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # When entering a branch, add the channel to the device configuration
        device_info = self.device_communication[self.driver_port_string]
        if self.channel not in device_info["channels"]:
            device_info["channels"].append(self.channel)

        if self.use_list_mode:
            if device_info["list_master_channel"] == -1:
                # No list master defined yet, this channel becomes the master
                device_info["list_master_channel"] = self.channel
                device_info["list_length"] = self.list_steps
                device_info["list_hold"] = self.list_hold
                device_info["list_delay"] = self.list_delay
                self.list_master = True
            else:
                # another channel is already the list master, this channel becomes a list follower
                self.list_follower = True

                if self.list_steps != device_info["list_length"]:
                    msg = (f"List sweep length mismatch: list master channel {device_info['list_master_channel']} has "
                           f"{device_info['list_length']} steps, but channel {self.channel} has {self.list_steps} steps.")
                    raise ValueError(msg)

                if self.list_hold != device_info["list_hold"] or self.list_delay != device_info["list_delay"]:
                    msg = (f"List sweep timing mismatch: list master channel {device_info['list_master_channel']} has "
                           f"hold time {device_info['list_hold']} s and delay time {device_info['list_delay']} s, but channel {self.channel} has "
                           f"hold time {self.list_hold} s and delay time {self.list_delay} s.")
                    raise ValueError(msg)

        # the decision between list follower and single step mode should be made after all channels are signed in

        # The command CN has to be sent at the beginning as it resets certain parameters
        # If the command CN would be used later, e.g. durin  "poweron", it would overwrite parameters that are defined during "configure"
        self.port.write(f"CN {self.channel}")  # switches the channel on

        self.set_speed(self.speed)

        # Initialize the source with 0V / 0A
        if self.source.startswith("Voltage"):
            self.port.write(f"DV {self.channel},{self.voltage_range},0.0,{self.protection}, 0,{self.current_range}")
        if self.source.startswith("Current"):
            self.port.write(f"DI {self.channel},{self.current_range},0.0,{self.protection}, 0,{self.voltage_range}")

        # RI and RV #comments to adjust the range, autorange is default
        self.set_average(self.average)
        self.check_errors()

        if self.list_master:
            # Only the list master channels uses configure_list_mode, all others use create_synchronous_list afterward
            # self.port.write("FMT 1,1")  # 2: ASCII 12 digits w/o header, 2: source output data for synchronous list mode
            self.set_data_output_format(include_header=True, source_output=False)
            self.configure_list_mode(
                source=self.source[0],
                mode=self.list_mode,
                output_range=0,  # autorange
                start=self.list_start,
                stop=self.list_stop,
                steps=self.list_steps,
                compliance=self.protection,
            )

            self.set_list_timing(self.list_hold, self.list_delay)
            self.enable_time_stamps()

            # Enable automatic abort function (2). Return to start value (1) after abort
            self.port.write("WM 2, 1")
            self.check_errors()

    def unconfigure(self) -> None:
        """Remove the channel from the device configuration when the procedure leaves a branch of the sequencer.

        The 'IN' and 'DZ' commands to switch the channel off cannot be used here, because it throws an error if the
        channel is already off from a previous 'poweroff' call.
        """
        if self.list_master:
            self.enable_time_stamps(False)

        device_info = self.device_communication[self.driver_port_string]
        if self.channel in device_info["channels"]:
            device_info["channels"].remove(self.channel)
        if self.use_list_mode and self.list_master:
            device_info["list_master_channel"] = -1
            device_info["list_length"] = 0

    def signin(self) -> None:
        """This function is called after configure.

        After all channels are registered in device communication during 'configure', the list master can set up the
        list mode. All other channels that are not list masters become list followers here.
        """
        if self.list_master:
            channel_list = self.device_communication[self.driver_port_string]["channels"]
            measurement_mode = 2  # staircase sweep mode
            self.set_measurement_mode(measurement_mode, channel_list)
            self.check_errors()

        # here we check if another channel in the same branch is forcing the list mode, even if this channel was set to
        # single measurement
        elif self.device_communication[self.driver_port_string]["list_master_channel"] != -1:
            self.list_follower = True
        else:
            self.list_follower = False

    def poweron(self) -> None:
        """In a previous version, the CN command was sent here.

        However, this leads to a reset of all parameters previously changed during 'configure'. Therefore, the CN
        command should not be used here, but has been moved to the beginning of 'configure'.
        """
        pass

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write(f"CL {self.channel}")  # switches the channel off

    def start(self) -> None:
        """Channels that are configured for list mode but are not the list master register their list values after the
        list master has configured the list mode in 'signin'.
        """
        if self.list_follower and self.use_list_mode:
            self.create_synchronous_list(self.list_start, self.list_stop)
            self.check_errors()

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        if self.list_master:
            # list master channel sets up list mode in configure
            return

        if self.list_follower:
            if self.use_list_mode:
                # this is never reached bc when using list mode as sweep source, the driver does not receive a sweep value
                pass
            else:
                # If the channel was set up for single measurement, but another channel is using list mode, we have to
                # create a synchronous list with start = stop = value
                value = float(self.value)
                self.create_synchronous_list(value, value)

            self.check_errors()
            return

        # Single measurement mode
        if self.source.startswith("Voltage"):
            self.port.write(f"DV {self.channel},{self.voltage_range},{self.value}")

        if self.source.startswith("Current"):
            self.port.write(f"DI {self.channel},{self.current_range},{self.value}")

        self.check_errors()

    def create_synchronous_list(self, start: float, stop: float) -> None:
        """Create a staircase sweep source that will be synchronized with the primary sweep source.

        The primary source (list master) must have configured its list mode via WI or WV before calling this function.
        Otherwise, it will be overwritten.

        The 'WNX' command is used for synchronous list sources (probably 2D sweeps?).
        command = f"WNX {source_number},{self.channel},{mode},{source_range},{start},{stop}, {self.protection}"
        the source number is a unique identifier. It must be between 2-10. We use the channel number + 1 here.
        mode = 1 if self.source.startswith("Voltage") else 2

        We use the WSI / WSV commands instead, as they seem to be more appropriate for our use case.
        """
        source_range = 0  # autorange, can be extended later
        command = f"WS{self.source[0]} {self.channel}, {source_range},{start},{stop}"
        self.port.write(command)

    def check_errors(self) -> None:
        """Check for errors in the device error queue (4 possible errors).

        TODO: can be extended to raise exceptions or print the translated error messages.

        122 - Number of channels must be corrected.
            Check the MM, FL, CN, CL, IN, DZ, or RZ command, and correct the
            number of channels.
        """
        status = self.port.query("ERR?")

        known_errors = {
            " 100": "Undefined GPIB command.",
        }

        if status != "0,0,0,0":
            print(status)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.list_master:
            self.check_errors()
            self.port.write("XE")  # execute measurement. The device will be in busy state until the list sweep is finished

        elif self.list_follower:
            return

        else:
            self.port.write(f"TI {self.channel},0")
            self.port.write(f"TV {self.channel},0")

    def request_result(self) -> None:
        """The master channel waits for the list mode to finish and request the measurement results."""
        if self.list_master:
            while True:
                if self.is_run_stopped():
                    break

                # set port timeout to a low value, check with try except until OPC returns 1
                try:
                    ret = self.port.query("*OPC?")
                    if ret:
                        break
                except TimeoutError:
                    time.sleep(0.1)  # short sleep time, the main time is spent in waiting for OPC
                    continue

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'request_result'."""
        if self.list_master:
            results = self.port.read()

            # Initialize the list results dictionary
            for channel in self.device_communication[self.driver_port_string]["channels"]:
                self.device_communication[self.driver_port_string]["list_results"][channel] = {
                    "measurements": [],
                    "timestamps": [],
                }

            for result in results.split(','):
                result = result.strip()
                header = result[:3]
                status = header[0]  # not used yet, can be used to check for errors
                channel_id = header[1]  # A-J, a-j for slots 1-10 and subchannel 1/2 (a/A)
                channel_num = ord(channel_id) - ord('A') + 1
                data_type = header[2]  # can be I,V,T
                value = float(result[3:])  # the actual value

                # save the value in the device communication dictionary
                if data_type == "T":
                    self.device_communication[self.driver_port_string]["list_results"][channel_num]["timestamps"].append(value)
                else:
                    self.device_communication[self.driver_port_string]["list_results"][channel_num]["measurements"].append(value)

            # make timestamps relative to the first timestamp of the list master
            master_timestamps = self.device_communication[self.driver_port_string]["list_results"][self.channel]["timestamps"]
            if master_timestamps:
                t0 = master_timestamps[0]
                for channel in self.device_communication[self.driver_port_string]["channels"]:
                    timestamps = self.device_communication[self.driver_port_string]["list_results"][channel]["timestamps"]
                    relative_timestamps = [t - t0 for t in timestamps]
                    self.device_communication[self.driver_port_string]["list_results"][channel]["timestamps"] = relative_timestamps

        elif self.list_follower:
            # list followers read results from device_communication in call
            return

        else:
            answer = self.port.read()
            try:
                self.measured_current = float(answer)
            except ValueError:
                self.measured_current = float(answer[3:])  # sometimes NAI comes first, we have to strip it

            answer = self.port.read()
            try:
                self.measured_voltage = float(answer)
            except ValueError:
                self.measured_voltage = float(answer[3:])  # sometimes NAI comes first, we have to strip it

    def call(self) -> list[float] | list[list[float]]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.list_follower or self.list_master:
            device_communication = self.device_communication[self.driver_port_string]
            measured_values = device_communication["list_results"][self.channel]["measurements"]

            # Create source values list
            source_values = self.get_source_values()

            # assign to measured voltage and current based on source type
            if self.source.startswith("Voltage"):
                self.measured_voltage = source_values
                self.measured_current = measured_values
            else:
                self.measured_current = source_values
                self.measured_voltage = measured_values

            if self.use_list_mode:
                timestamps = device_communication["list_results"][self.channel]["timestamps"]
                return [self.measured_voltage, self.measured_current, timestamps]

        return [self.measured_voltage, self.measured_current]

    def set_average(self, average: int) -> None:
        """Set the number of averaging samples of the A/D converter.

        The average number can either be 1-1023 (samples depending on mode) or -1 - -100 (number of PLCs)
        """
        if average < -100 or (average > 1023 or average == 0):
            msg = f"Invalid average value: {average}. Must be 1-1023 (samples) or -1 to -100 (PLCs)."
            raise ValueError(msg)
        self.port.write(f"AV {average}")

    # Wrapped functions

    def set_measurement_mode(self, mode: int, channels: list[int]) -> None:
        """Set the measurement mode to one of 18 available modes (see manual table 4-14).

        1 - Spot (DI, DV)
        2 - Staircase Sweep
        """
        # command =
        self.port.write(f"MM {mode},{','.join(str(ch) for ch in channels)}")
        self.check_errors()

    def set_data_output_format(self, include_header: bool = False, source_output: bool = False) -> None:
        """Set the data output format.

        include_header: If True, the output data will include a header with NAI codes.
        source_output: If True, the output data will include source values of the primary list source (for list mode).
        This function could be extended to include all 12 format options and all 12 modes. See manual table 4-24.
        """
        format_code_1 = 1 if include_header else 2
        format_code_2 = 1 if source_output else 0
        self.port.write(f"FMT {format_code_1},{format_code_2}")

    def set_speed(self, speed: str) -> None:
        """Set the measurement speed."""
        speed = speed.strip().lower()
        if speed == "fast":  # 1 Short (0.1 PLC) preconfigured selection Fast
            self.port.write("AIT 0,0,1")
            self.port.write("AAD %s,0" % self.channel)
        elif speed == "medium":  # 2 Medium (1.0 PLC) preconfigured selection Normal
            self.port.write("AIT 1,0,1")
            self.port.write("AAD %s,1" % self.channel)
        elif speed == "slow":  # 3 Long (10 PLC) preconfigured selection Quiet
            self.port.write("AIT 1,2,10")
            self.port.write("AAD %s,1" % self.channel)
        else:
            msg = f"Invalid speed setting: {speed}. Use 'Fast', 'Medium', or 'Slow'."
            raise ValueError(msg)

    # Wrapped functions - list mode

    def configure_list_mode(self, source: str, mode: int, output_range:int, start:float, stop:float, steps: int, compliance: float) -> None:
        """Configure a staircase sweep using the list sweep values."""
        if steps > 1001 or steps < 1:
            msg = f"Invalid number of list steps: {steps}. Device staircase sweeps support 1-1001 points."
            raise ValueError(msg)

        if source not in ("V", "I"):
            msg = f"Invalid source for list sweep: {source}. Use 'V' or 'I'."
            raise ValueError(msg)

        # TODO: add compliance, range, and power compliance
        self.port.write(f"W{source} {self.channel},{mode},{output_range}, {start},{stop},{steps},{compliance}")

    def set_list_timing(self, hold: float, delay: float) -> None:
        """Set the timing parameters for list sweeps.

        We set the hold time to 0 (time between starting the sweep and forcing the first step).
        We set the delay time in s (time between forcing and starting a measurement), which corresponds to the SweepMe Hold time.
        We set the Sdelay time in s (time between starting a measurement and forcing the next step), which corresponds to the SweepMe Delay time.
        """
        if hold < 0 or hold > 655.35:
            msg = f"Invalid hold time: {hold}. Must be between 0 and 655.35 s."
            raise ValueError(msg)

        if delay < 0 or delay > 655.35:
            msg = f"Invalid delay time: {delay}. Must be between 0 and 655.35 s."
            raise ValueError(msg)

        self.port.write(f"WT 0,{hold},{delay}")

    def enable_time_stamps(self, enable: bool = True) -> None:
        """Enable or disable time stamp output for list sweeps."""
        if enable:
            self.port.write("TSC 1")
        else:
            self.port.write("TSC 0")

    def get_source_values(self) -> list[float]:
        """Calculate the source values for the list sweep from the list sweep parameters."""
        source_values = []
        if not self.use_list_mode:
            # if a single value channel is used as list follower, we create a list with start = stop = value
            try:
                single_value = float(self.value)
            except ValueError:
                single_value = float('nan')
            source_values = [single_value] * self.device_communication[self.driver_port_string]["list_length"]

        elif self.list_mode in (1, 3):  # linear or linear dual
            source_values = np.linspace(self.list_start, self.list_stop, self.list_steps).tolist()

        elif self.list_mode in (2, 4):  # logarithmic or logarithmic dual
            if self.list_start <= 0 or self.list_stop <= 0:
                msg = "Logarithmic list sweeps require positive start and stop values."
                raise ValueError(msg)

            source_values = np.logspace(np.log10(self.list_start), np.log10(self.list_stop), self.list_steps).tolist()

        if self.list_mode in (3, 4):  # dual sweeps
            source_values += source_values[::-1]

        return source_values

    # Currently unused wrapped functions

    def get_identification(self) -> str:
        """Return the device identification string."""
        return self.port.query("*IDN?")
