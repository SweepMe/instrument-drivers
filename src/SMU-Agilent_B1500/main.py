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

    description = """<p><strong>Agilent B1500A</strong>
    Start EasyExpert must run on PC, but IO Control must be minimized and EasyExpert closed
    </p>
    """
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
            "timeout": 20,
            # "delay": 0.1,
        }
        # TODO: can this be omitted?
        self.port_identifications = ["Agilent Technologies,B1500A"]
        self.channel: int = 1
        self.shortname = f"B1500 Ch{self.channel}"

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
        self.use_list_mode: bool = False
        self.list_modes = {
            "linear": 1,
            "logarithmic": 2,
            "linear dual": 3,  # start - stop - start
            "logarithmic dual": 4,  # start - stop - start
        }
        self.list_mode: int = 1  # linear
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
        self.list_start = float(parameter["ListSweepStart"])
        self.list_stop = float(parameter["ListSweepEnd"])
        self.list_steps = int(parameter["ListSweepStepPointsValue"])
        self.list_hold = float(parameter["ListSweepHoldtime"])
        self.list_delay = float(parameter["ListSweepDelaytime"])

        step_type = parameter["ListSweepStepPointsType"]
        if step_type.startswith("Points (lin.)"):
            self.list_mode = self.list_modes["linear"] if not parameter["ListSweepDual"] else self.list_modes[
                "linear dual"]

        elif step_type.startswith("Points (log.)"):
            self.list_mode = self.list_modes["logarithmic"] if not parameter["ListSweepDual"] else self.list_modes[
                "logarithmic dual"]

        # # Add time staps to return values
        # self.variables.extend(["Time stamp", "Time stamp zeroed"])
        # self.units.extend(["s", "s"])
        # self.plottype.extend([True, True])
        # self.savetype.extend([True, True])

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        print("clearing error queue...")
        self.check_errors()
        print(self.port.query("*IDN?"))
        driver_port_string = "Agilent_B1500_" + self.port_string

        # initialize commands only need to be sent once, so we check here whether another instance of the same driver
        # AND same port did it already. If not, this instance is the first and has to do it.
        if not driver_port_string in self.device_communication:
            self.port.write("*RST")  # reset to initial settings
            self.port.write("BC")  # buffer clear
            self.port.write("AZ 0")  # Auto-Zero off for faster measurements
            self.port.write("FMT 2")  # use to change the output format

            # if initialize commands have been sent, we can add the driver_port_string to the dictionary that is seen by
            # all drivers
            self.device_communication[driver_port_string] = True

        if self.use_list_mode:
            print("Setting format for list mode...")
            self.port.write("FMT 2,1")  # overwrite for list mode to return the set values as well. Might need to go for 2,2 when using multiple channels



    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # The command CN has to be sent at the beginning as it resets certain parameters
        # If the command CN would be used later, e.g. durin  "poweron", it would overwrite parameters that are defined during "configure"
        self.port.write(f"CN {self.channel}")  # switches the channel on
        self.set_speed(self.speed)
        if self.source.startswith("Voltage"):
            self.port.write(f"DV {self.channel},{self.voltage_range},0.0,{self.protection}, 0,{self.current_range}")
        if self.source.startswith("Current"):
            self.port.write(f"DI {self.channel},{self.current_range},0.0,{self.protection}, 0,{self.voltage_range}")
        # RI and RV #comments to adjust the range, autorange is default
        self.set_average(self.average)
        self.check_errors()

        if self.use_list_mode:
            print("Configuring list mode...")
            self.configure_list_mode(
                source=self.source[0],
                mode=self.list_mode,
                output_range=0,  # autorange
                start=self.list_start,
                stop=self.list_stop,
                steps=self.list_steps,
                compliance=self.protection,
            )
            self.set_measurement_mode(2, [self.channel])  # staircase sweep mode. Might need to move to poweron
            self.set_list_timing(self.list_hold, self.list_delay)
            # Enable automatic abort function (2). Return to start value (1) after abort
            self.port.write("WM 2, 1")
            self.check_errors()

        # *LRN? is a function to ask for current status of certain parameters,
        # 0 = output on or off
        # self.port.write("*LRN? 0")
        # print(self.port.read())

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        # This throws an error because IN cannot be used when the channel is off from poweroff
        # self.port.write(f"IN {self.channel}")
        # self.check_errors()
        # resets to zero volt
        # self.port.write("DZ")

    def poweron(self) -> None:
        """In a previous version, the CN command was sent here.

        However, this leads to a reset of all parameters previously changed during 'configure'. Therefore, the CN
        command should not be used here, but has been moved to the beginning of 'configure'.
        """
        pass

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write(f"CL {self.channel}")  # switches the channel off

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        if self.use_list_mode:
            return

        if self.source.startswith("Voltage"):
            self.port.write(f"DV {self.channel},{self.voltage_range},{self.value}")

        if self.source.startswith("Current"):
            self.port.write(f"DI {self.channel},{self.current_range},{self.value}")

        self.check_errors()

    def check_errors(self) -> None:
        """Check for errors in the device error queue.

        122 - Number of channels must be corrected.
Check the MM, FL, CN, CL, IN, DZ, or RZ command, and correct the
number of channels.
        """
        status = self.port.query("ERR?")

        known_errors = {
            " 100": "Undefined GPIB command.",
        }

        # if status != "0,0,0,0":
        print(status)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.use_list_mode:
            # TODO: only the list_master channel should execute XE?
            print("Starting list mode measurement...")
            self.check_errors()
            self.port.write("XE")  # execute measurement
        else:
            self.port.write(f"TI {self.channel},0")
            self.port.write(f"TV {self.channel},0")

    def request_result(self) -> None:
        """Wait for the list mode to finish and request the measurement results."""
        if self.use_list_mode:
            timeout_s = 10
            start_time = time.perf_counter()

            # TODO: allow aborting the wait from outside
            while True:
                if self.is_run_stopped():
                    break

                ret = self.port.query("*OPC?")
                if ret:
                    break

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'request_result'."""
        if self.use_list_mode:
            print("Reading list mode results.")
            results = self.port.read()
            values = [float(part.strip()) for part in results.split(',') if part.strip()]
            print(values)

            
            if self.source.startswith("Voltage"):
                self.measured_voltage = values[0::2]
                self.measured_current = values[1::2]
            else:
                self.measured_current = values[0::2]
                self.measured_voltage = values[1::2]

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

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.measured_voltage, self.measured_current]

    # Wrapped functions

    """
    Enables channels CN [chnum ... [,chnum] ... ]
    Disables channels CL [chnum ... [,chnum] ... ]
    Sets filter ON/OFF [FL] mode[,chnum ... [,chnum] ... ]
    Sets series resistor ON/OFF [SSR] chnum,mode
    Sets integration time
    (Agilent B1500 can use
    AAD/AIT instead of AV.)
    [AV] number[,mode]
    [AAD] chnum[,type]
    [AIT] type,mode[,N]
    Forces constant voltage DV chnum,range,output
    [,comp[,polarity[,crange]]]
    Forces constant current DI
    Sets voltage measurement
    range
    [RV] chnum,range
    Sets current measurement
    range
    [RI] chnum,range
    [RM] chnum,mode[,rate]
    Sets measurement mode MM 1,chnum[,chnum ... [,chnum] ... ]
    Sets SMU operation mode [CMM] chnum,mode
    Executes measurement XE
    """

    def set_average(self, average: int) -> None:
        """Set the number of averaging samples of the A/D converter.

        The average number can either be 1-1023 (samples depending on mode) or -1 - -100 (number of PLCs)
        """
        if average < -100 or (average > 1023 or average == 0):
            msg = f"Invalid average value: {average}. Must be 1-1023 (samples) or -1 to -100 (PLCs)."
            raise ValueError(msg)
        self.port.write(f"AV {average}")

    def set_measurement_mode(self, mode: int, channels: list[int]) -> None:
        """Set the measurement mode to one of 18 available modes (see manual table 4-14).

        1 - Spot (DI, DV)
        2 - Staircase Sweep
        """
        # command =
        self.port.write(f"MM {mode},{','.join(str(ch) for ch in channels)}")
        print("Checking errors after setting measurement mode")
        self.check_errors()

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

    # WT, WV, WI
    # TSC enables time stamp output

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

