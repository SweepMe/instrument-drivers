# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2020-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: LCRmeter
# * Instrument: Zurich Instruments MFIA (and MFLI with the MF-IA option)

from __future__ import annotations

import time
from typing import Any

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import error
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()  # the 'libs' folder holds zhinst for Python 3.6 32 bit; newer versions use 'libraries'

from zhinst import ziPython  # noqa: E402 - the library folder must be on the path first

API_LEVEL = 6  # the driver was developed with API level 6

# GUI label -> instrument value. Labels of earlier driver versions stay as keys, so that saved sequences still load.
INTEGRATIONS = {
    "Short -> medium precision": 0,
    "Medium -> high precision": 1,
    "Medium -> high precision ": 1,  # label with trailing space, used up to 2026
    "Long -> very high precision": 2,
}
OPERATING_MODES = {"4-Terminal": 0, "2-Terminal": 1}

# Sources that can supply the DC bias across the device under test, see doc/description.md
BIAS_INTERNAL = "Internal"  # internal bias source of the instrument, nodes imps/0/bias/*
BIAS_AUX_OUTPUT = "Aux Output (cable to Aux In 1)"  # DC level of an Auxiliary Output, added to the Signal Output
BIAS_EXTERNAL = "External"  # the bias is supplied by another instrument, the driver does not change any bias node
BIAS_SOURCES = [BIAS_INTERNAL, BIAS_AUX_OUTPUT, BIAS_EXTERNAL]

# List sweep: spacing of the sweep points -> Sweeper xmapping (0 = linear, 1 = logarithmic)
STEP_POINTS_TYPES = {"Step width:": 0, "Points (lin.):": 0, "Points (log.):": 1}
SCAN_SEQUENTIAL = 0
SCAN_REVERSE = 3
BANDWIDTH_CONTROL_AUTO = 2

# Output voltage ranges of the Signal Output in V. The range must cover drive amplitude plus DC bias, otherwise the
# instrument clamps the bias silently, e.g. to +/-1 V in the 1 V range.
OUTPUT_RANGES = [0.01, 0.1, 1.0, 10.0]


class Device(EmptyDevice):
    """Driver for the Zurich Instruments MFIA impedance analyzer."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "MFIA"

        # In list sweep mode, each variable holds the values of the whole sweep
        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        self.timeout_autorange: float = 20.0  # in s
        self.sampling_rate: float = 10.0  # in 1/s
        self.bias_tolerance: float = 1e-3  # in V, maximum deviation of the bias read back from the requested bias

        self.daq: Any = None  # LabOne API session, created in connect()

        # GUI parameters as received from the GUI, converted in configure()
        self.gui_parameters: dict[str, Any] = {}
        self.device_id: str = ""
        self.sweep_mode: str = "None"
        self.step_mode: str = "None"
        self.list_sweep: bool = False

        # Converted GUI parameters
        self.value_type_rms: str = "Voltage RMS in V:"
        self.value_rms: float = 0.02
        self.value_type_bias: str = "Voltage bias in V:"
        self.value_bias: float = 0.0
        self.bias_source: str = BIAS_INTERNAL
        self.aux_output_index: int = 0  # zero-based index of the Auxiliary Output used as bias source
        self.precision: int = 0
        self.average: int = 1
        self.frequency: float = 1000.0
        self.operating_mode: int = 0

        # List sweep, converted in configure()
        self.list_start: float = 0.0
        self.list_end: float = 0.0
        self.list_point_count: int = 0
        self.list_xmapping: int = 0
        self.list_dual: bool = False
        self.list_settling_time: float = 0.0
        self.list_settling_inaccuracy: float = 1e-3
        self.list_averaging_tc: float = 0.0
        self.is_first_list_sweep: bool = True

        # Instrument state
        self.current_input_index: int = 0
        self.voltage_input_index: int = 0
        self.output_range: float | None = None  # output range in V set during the current run, None if not yet set
        self.time_constant: float = 0.0
        self.polling_topic: str = ""

        # Results
        self.resistance: float | np.ndarray = float("nan")
        self.reactance: float | np.ndarray = float("nan")
        self.measured_frequency: float | np.ndarray = float("nan")
        self.bias: float | np.ndarray = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI parameters. The sweeper settings are only shown for a list sweep."""
        sweep_modes = ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A"]
        new_parameters: dict[str, Any] = {
            "SweepMode": sweep_modes,
            "StepMode": sweep_modes,
            "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
            "ValueRMS": 0.02,
            "ValueTypeBias": ["Voltage bias in V:", "Current bias in A:"],
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "OperatingMode": list(OPERATING_MODES),
            "Average": ["1", "2", "4", "8", "16", "32", "64"],
            "Integration": ["Short -> medium precision", "Medium -> high precision", "Long -> very high precision"],
            # List sweep, run by the Sweeper module of the instrument
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep"],
            "ListSweepStart": 100.0,
            "ListSweepEnd": 100000.0,
            "ListSweepStepPointsType": list(STEP_POINTS_TYPES),
            "ListSweepStepPointsValue": 31,
            "ListSweepDual": False,
            "ListSweepDelaytime": 0.0,
            # Parameters box
            "BiasSource": BIAS_SOURCES,
            "BiasAuxOutput": ["1", "2", "3", "4"],
        }

        if parameters.get("SweepValue", "") == "List sweep":
            new_parameters["Sweep settling inaccuracy"] = "1e-3"
            new_parameters["Sweep averaging in TC"] = "0"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters; they are converted and checked in configure()."""
        self.gui_parameters = parameters
        self.device_id = str(parameters.get("Port", "")).lower()
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.step_mode = parameters.get("StepMode", "None")
        self.list_sweep = parameters.get("SweepValue", "") == "List sweep"

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def find_ports(self) -> list[str]:
        """Return the IDs of all devices the LabOne Data Server can reach. USB needs the LabOne USB driver."""
        return list(ziPython.ziDiscovery().findAll())

    def connect(self) -> None:
        """Open a LabOne API session and connect the device."""
        if not self.device_id:
            msg = "No device selected. Start the LabOne Data Server, press 'Find ports' and select the device ID."
            raise ValueError(msg)

        discovery = ziPython.ziDiscovery()
        discovery.find(self.device_id)
        properties = discovery.get(self.device_id)
        if properties["apilevel"] != API_LEVEL:
            self.message_log(f"MFIA: API level {properties['apilevel']} does not match driver level {API_LEVEL}.")

        # The zhinst-core library shipped with the driver rarely has exactly the version of the LabOne installation
        # on the user's computer, and the Data Server refuses the connection in that case unless mismatches are
        # allowed explicitly.
        try:
            self.daq = ziPython.ziDAQServer(
                properties["serveraddress"],
                properties["serverport"],
                properties["apilevel"],
                allow_version_mismatch=True,
            )
        except TypeError:
            # old ziPython versions (Python 3.6, 32 bit) do not know the argument 'allow_version_mismatch'
            self.daq = ziPython.ziDAQServer(
                properties["serveraddress"],
                properties["serverport"],
                properties["apilevel"],
            )
        self.daq.connectDevice(self.device_id, properties["interfaces"][0])  # blocking

        self.polling_topic = f"/{self.device_id}/imps/0/sample"

    def disconnect(self) -> None:
        """Disconnect the device."""
        # connect() may have failed before the API session was created, e.g. if the device was not found
        if self.daq is not None:
            self.daq.disconnectDevice(self.device_id)

    def initialize(self) -> None:
        """Read which inputs the impedance unit uses."""
        self.current_input_index = self.daq.getInt(f"/{self.device_id}/imps/0/current/inputselect")
        self.voltage_input_index = self.daq.getInt(f"/{self.device_id}/imps/0/voltage/inputselect")

    def configure(self) -> None:
        """Convert and check the GUI parameters, then set up the impedance unit, the drive and the bias."""
        self.read_gui_parameters()
        self.check_bias_configuration()
        if self.list_sweep:
            self.read_list_sweep_parameters()

        self.output_range = None  # the output range is chosen anew for each configure

        # The point by point measurement polls the impedance samples, the Sweeper module records them by itself
        if not self.list_sweep:
            self.subscribe_polling_topic()

        # integration, cable correction switched off (can be added later), impedance unit
        self.daq.set(
            [
                [f"/{self.device_id}/system/impedance/precision", self.precision],
                [f"/{self.device_id}/system/impedance/calib/cablelength", 0],
                # necessary if an MFLI is used or if the impedance unit was disabled beforehand
                [f"/{self.device_id}/imps/0/enable", 1],
                [f"/{self.device_id}/imps/0/mode", self.operating_mode],
                [f"/{self.device_id}/imps/0/auto/inputrange", 1],
                [f"/{self.device_id}/demods/0/rate", self.sampling_rate],
                [f"/{self.device_id}/imps/0/auto/bw", 1],
                [f"/{self.device_id}/imps/0/freq", self.frequency],
            ],
        )
        self.daq.sync()

        # The output range must be active before amplitude and bias are written, as both are clamped to it
        self.set_output_range(self.get_largest_bias())

        settings = [
            # drive amplitude set manually, otherwise the instrument overwrites it
            [f"/{self.device_id}/imps/0/auto/output", 0],
            [f"/{self.device_id}/imps/0/output/amplitude", self.value_rms],
        ]
        settings += self.get_bias_setup_settings()
        settings += self.get_bias_value_settings(self.value_bias)
        self.daq.set(settings)
        self.daq.sync()

        self.verify_bias_value(self.value_bias)

        self.time_constant = self.get_time_constant()
        self.is_first_list_sweep = True

    def unconfigure(self) -> None:
        """Set drive amplitude and bias back to safe values."""
        if self.daq is None:
            return

        self.daq.unsubscribe("*")

        settings = [
            [f"/{self.device_id}/imps/0/output/amplitude", 0.02],  # oscillator signal back to a small value
        ]
        settings += self.get_bias_reset_settings()  # bias back to 0 V and bias source switched off
        self.daq.set(settings)
        self.daq.sync()

    def poweron(self) -> None:
        """Switch on the Signal Output."""
        self.set_output_state(True)

    def poweroff(self) -> None:
        """Switch off the Signal Output."""
        self.set_output_state(False)

    def apply(self) -> None:
        """Set the new frequency or bias. In a list sweep, only the step value is set; the Sweeper sets the rest."""
        frequency: float | None = None  # new frequency in Hz, None if the frequency does not change
        bias_value: float | None = None  # new DC bias in V, None if the bias does not change

        if not self.list_sweep and self.sweep_mode != "None":
            if self.sweep_mode.startswith("Frequency"):
                frequency = float(self.value)
            else:
                bias_value = float(self.value)

        if self.step_mode not in ("None", self.sweep_mode):
            if self.step_mode.startswith("Frequency"):
                frequency = float(self.stepvalue)
            else:
                bias_value = float(self.stepvalue)

        settings = []
        if frequency is not None:
            settings.append([f"/{self.device_id}/imps/0/freq", frequency])
            self.frequency = frequency

        if bias_value is not None:
            # the output range must be widened before the bias is written, otherwise the bias is clamped
            self.set_output_range(bias_value)
            settings += self.get_bias_value_settings(bias_value)

        if not settings:
            return

        self.daq.set(settings)
        self.daq.sync()

        if bias_value is not None:
            self.verify_bias_value(bias_value)

        self.time_constant = self.get_time_constant()

    def adapt(self) -> None:
        """Autorange the inputs and wait until the filters have settled. In a list sweep, the Sweeper does this."""
        if self.list_sweep:
            return

        # even if 'apply' is not called, external changes might necessitate to trigger autorange again
        self.daq.set(
            [
                [f"/{self.device_id}/currins/{self.current_input_index}/autorange", 1],
                [f"/{self.device_id}/sigins/{self.voltage_input_index}/autorange", 1],
            ],
        )

        start_time = time.time()
        while True:
            time.sleep(0.01)  # to proceed as soon as possible if autoranging has finished
            # Autoranging is finished when the device has set both nodes back to 0
            current_input_autorange = self.daq.getInt(
                f"/{self.device_id}/currins/{self.current_input_index}/autorange",
            )
            voltage_input_autorange = self.daq.getInt(
                f"/{self.device_id}/sigins/{self.voltage_input_index}/autorange",
            )
            if current_input_autorange == 0 and voltage_input_autorange == 0:
                break

            if time.time() - start_time > self.timeout_autorange:
                msg = f"The MFIA did not finish autoranging within {self.timeout_autorange} s."
                raise TimeoutError(msg)

        # A new value must have arrived before the settling time starts
        self.daq.sync()  # needed to empty the buffer
        self.daq.poll(0.01, 5000, 0, True)  # poll length in s, timeout in ms, flags, flat dict

        # after a new value can be polled, the filters need the settling time to deliver good values in 'measure'
        time.sleep(16.0 * self.time_constant)

    def measure(self) -> None:
        """Measure the impedance: average the polled samples, or run the list sweep in the instrument."""
        if self.list_sweep:
            self.measure_list_sweep()
            return

        self.daq.sync()  # empty the buffer, values from the settling process are not wanted

        # Poll as many values as needed for the average. 0.1 is added to get at least the number of values needed.
        poll_length = (self.average + 0.1) / self.sampling_rate
        data = self.daq.poll(poll_length, 10000, 0, True)  # poll length in s, timeout in ms, flags, flat dict

        impedance = np.mean(data[self.polling_topic]["z"])
        self.resistance = float(impedance.real)
        self.reactance = float(impedance.imag)
        self.measured_frequency = float(np.mean(data[self.polling_topic]["frequency"]))
        self.bias = self.get_bias_value()

    def call(self) -> list[float | np.ndarray]:
        """Return R, X, frequency and bias, as single values or as arrays of the list sweep."""
        return [self.resistance, self.reactance, self.measured_frequency, self.bias]

    """ here, the list sweep is run with the Sweeper module of the instrument """

    def measure_list_sweep(self) -> None:
        """Run the list sweep, forward and in a dual sweep also backward, and store the results as arrays."""
        results = [self.run_sweep(SCAN_SEQUENTIAL)]
        if self.list_dual and not self.is_run_stopped():
            results.append(self.run_sweep(SCAN_REVERSE))

        if self.is_run_stopped():
            return

        grid = np.concatenate([result["grid"] for result in results])
        self.resistance = np.concatenate([result["realz"] for result in results])
        self.reactance = np.concatenate([result["imagz"] for result in results])
        self.measured_frequency = np.concatenate([result["frequency"] for result in results])

        if self.sweep_mode.startswith("Voltage bias"):
            self.bias = grid
        else:
            self.bias = np.full(len(grid), self.get_bias_value())

    def run_sweep(self, scan: int) -> dict[str, np.ndarray]:
        """Run one sweep with the Sweeper module and return the impedance results by field name."""
        sweeper = self.daq.sweep()
        try:
            for key, value in self.get_sweeper_settings(scan):
                sweeper.set(key, value)
            sweeper.subscribe(self.polling_topic)
            sweeper.execute()

            while not sweeper.finished():
                if self.is_run_stopped():
                    sweeper.finish()
                    break
                time.sleep(0.1)

            data = sweeper.read(True)
            sweeper.unsubscribe(self.polling_topic)
        finally:
            sweeper.clear()

        if self.is_run_stopped():
            return {}

        # one entry per sweep loop, each holding the impedance sample of the whole sweep
        sample = data[self.polling_topic][0][0]
        if self.is_first_list_sweep:
            # The field names of the impedance sweep are taken from the API reference; the log shows what arrived
            self.message_log(f"MFIA list sweep: result fields {sorted(sample)}")
            self.is_first_list_sweep = False

        return {key: np.asarray(sample[key], dtype=float) for key in ("grid", "realz", "imagz", "frequency")}

    def get_sweeper_settings(self, scan: int) -> list[tuple[str, Any]]:
        """Return the Sweeper module settings for the list sweep. 'device' must be set first."""
        return [
            ("device", self.device_id),
            ("gridnode", self.get_sweep_node()),
            ("start", self.list_start),
            ("stop", self.list_end),
            ("samplecount", self.list_point_count),
            ("xmapping", self.list_xmapping),
            ("scan", scan),
            ("bandwidthcontrol", BANDWIDTH_CONTROL_AUTO),
            ("loopcount", 1),
            ("settling/time", self.list_settling_time),
            ("settling/inaccuracy", self.list_settling_inaccuracy),
            ("averaging/sample", self.average),
            ("averaging/tc", self.list_averaging_tc),
        ]

    def get_sweep_node(self) -> str:
        """Return the node the Sweeper sweeps: the frequency of the impedance oscillator or the bias."""
        if self.sweep_mode.startswith("Frequency"):
            return f"oscs/{self.get_impedance_oscillator()}/freq"

        if self.bias_source == BIAS_INTERNAL:
            return "imps/0/bias/value"

        return f"auxouts/{self.aux_output_index}/offset"  # BIAS_AUX_OUTPUT, check_bias_configuration excludes External

    """ here, GUI parameters are converted and checked """

    def read_gui_parameters(self) -> None:
        """Convert the GUI parameters that are needed in every mode."""
        parameters = self.gui_parameters

        self.value_type_rms = parameters.get("ValueTypeRMS", "Voltage RMS in V:")
        self.value_rms = self.to_number(parameters.get("ValueRMS", 0.02), "RMS value")
        self.value_type_bias = parameters.get("ValueTypeBias", "Voltage bias in V:")
        self.value_bias = self.to_number(parameters.get("ValueBias", 0.0), "Bias value")
        self.frequency = self.to_number(parameters.get("Frequency", 1000.0), "Frequency")
        self.average = int(self.to_number(parameters.get("Average", "1"), "Average"))

        integration = parameters.get("Integration", "Short -> medium precision")
        if integration not in INTEGRATIONS:
            msg = f"Unknown integration '{integration}'. Choose one of: {', '.join(INTEGRATIONS)}."
            raise ValueError(msg)
        self.precision = INTEGRATIONS[integration]

        operating_mode = parameters.get("OperatingMode", "4-Terminal")
        if operating_mode not in OPERATING_MODES:
            msg = f"Unknown operating mode '{operating_mode}'. Choose one of: {', '.join(OPERATING_MODES)}."
            raise ValueError(msg)
        self.operating_mode = OPERATING_MODES[operating_mode]

        self.bias_source = parameters.get("BiasSource", BIAS_INTERNAL)
        if self.bias_source not in BIAS_SOURCES:
            msg = f"Unknown bias source '{self.bias_source}'. Choose one of: {', '.join(BIAS_SOURCES)}."
            raise ValueError(msg)
        self.aux_output_index = int(self.to_number(parameters.get("BiasAuxOutput", "1"), "Bias Aux Output")) - 1

    def read_list_sweep_parameters(self) -> None:
        """Convert and check the list sweep parameters for the Sweeper module."""
        parameters = self.gui_parameters

        if self.sweep_mode not in ("Frequency in Hz", "Voltage bias in V"):
            msg = "The list sweep needs the sweep mode 'Frequency in Hz' or 'Voltage bias in V'."
            raise ValueError(msg)

        if parameters.get("ListSweepType", "Sweep") != "Sweep":
            msg = "The instrument's Sweeper only runs sweeps from a start to an end value, not custom values."
            raise ValueError(msg)

        self.list_start = self.to_number(parameters.get("ListSweepStart", 100.0), "List sweep start value")
        self.list_end = self.to_number(parameters.get("ListSweepEnd", 100000.0), "List sweep end value")

        step_points_type = parameters.get("ListSweepStepPointsType", "Points (lin.):")
        if step_points_type not in STEP_POINTS_TYPES:
            msg = f"Unknown step type '{step_points_type}'. Choose one of: {', '.join(STEP_POINTS_TYPES)}."
            raise ValueError(msg)
        self.list_xmapping = STEP_POINTS_TYPES[step_points_type]
        step_points_value = self.to_number(parameters.get("ListSweepStepPointsValue", 31), "List sweep step/points")
        self.list_point_count = self.get_point_count(step_points_type, step_points_value)

        if self.list_xmapping == 1 and (self.list_start <= 0 or self.list_end <= 0):
            msg = "A logarithmic list sweep needs start and end values above 0."
            raise ValueError(msg)

        self.list_dual = bool(parameters.get("ListSweepDual", False))
        self.list_settling_time = self.to_number(parameters.get("ListSweepDelaytime", 0.0), "List sweep delay time")
        self.list_settling_inaccuracy = self.to_number(
            parameters.get("Sweep settling inaccuracy", "1e-3"),
            "Sweep settling inaccuracy",
        )
        if not 1e-13 <= self.list_settling_inaccuracy <= 0.1:  # noqa: PLR2004 - limits of settling/inaccuracy
            msg = f"The sweep settling inaccuracy must be between 1e-13 and 0.1, not {self.list_settling_inaccuracy}."
            raise ValueError(msg)
        self.list_averaging_tc = self.to_number(parameters.get("Sweep averaging in TC", "0"), "Sweep averaging in TC")
        if self.list_settling_time < 0 or self.list_averaging_tc < 0:
            msg = "The list sweep delay time and the sweep averaging must not be negative."
            raise ValueError(msg)

    def get_point_count(self, step_points_type: str, step_points_value: float) -> int:
        """Return the number of sweep points. A step width must divide the sweep range into equal steps."""
        if step_points_type.startswith("Step width"):
            if step_points_value <= 0:
                msg = f"The step width of the list sweep must be above 0, not {step_points_value}."
                raise ValueError(msg)
            steps = abs(self.list_end - self.list_start) / step_points_value
            if abs(steps - round(steps)) > 1e-6 * max(1.0, steps):  # tolerance for rounding errors
                msg = (
                    f"The step width {step_points_value} does not divide the range from {self.list_start} to "
                    f"{self.list_end} into equal steps, which the instrument's Sweeper needs. Use 'Points (lin.):' "
                    f"or adjust the step width."
                )
                raise ValueError(msg)
            point_count = round(steps) + 1
        else:
            point_count = int(step_points_value)

        if point_count < 2:  # noqa: PLR2004 - a sweep needs a start and an end point
            msg = f"The list sweep needs at least 2 points, not {point_count}."
            raise ValueError(msg)
        return point_count

    def get_largest_bias(self) -> float:
        """Return the largest bias in V of this configuration, used to choose the output range in configure()."""
        if self.list_sweep and self.sweep_mode.startswith("Voltage bias"):
            return max(abs(self.list_start), abs(self.list_end), abs(self.value_bias))
        return self.value_bias

    @staticmethod
    def to_number(value: object, name: str) -> float:
        """Return the value as float, or raise a ValueError with a user-readable message."""
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            msg = f"'{name}' must be a number, but is '{value}'."
            raise ValueError(msg) from None

    """ here, the bias handling is wrapped into convenience functions """

    def check_bias_configuration(self) -> None:
        """Check whether the requested bias can be applied by the selected bias source.

        None of the bias sources of this instrument can source a current, and an external bias source cannot be swept
        by this driver.
        """
        bias_is_swept = "bias" in self.sweep_mode or "bias" in self.step_mode
        if self.bias_source == BIAS_EXTERNAL and not bias_is_swept:
            return

        bias_types = [self.value_type_bias]
        if "bias" in self.sweep_mode:
            bias_types.append(self.sweep_mode)
        if "bias" in self.step_mode:
            bias_types.append(self.step_mode)

        if any(bias_type.startswith("Current") for bias_type in bias_types):
            msg = (
                "The Zurich Instruments MFIA driver can only apply a voltage bias. Please select 'Voltage bias in V' "
                "instead of 'Current bias in A'."
            )
            raise ValueError(msg)

        if self.bias_source == BIAS_EXTERNAL:
            msg = (
                "The bias source 'External' means that the bias is applied by another instrument, so this driver "
                f"cannot sweep it. Please choose the bias source '{BIAS_INTERNAL}' or '{BIAS_AUX_OUTPUT}', or sweep "
                "the bias with the driver of the biasing instrument."
            )
            raise ValueError(msg)

    def get_bias_setup_settings(self) -> list[list[Any]]:
        """Return the settings that switch on the selected bias source. Sent once during 'configure'."""
        if self.bias_source == BIAS_INTERNAL:
            # the bias value alone has no effect, the bias source must be enabled explicitly
            return [[f"/{self.device_id}/imps/0/bias/enable", 1]]

        if self.bias_source == BIAS_AUX_OUTPUT:
            aux_output = f"/{self.device_id}/auxouts/{self.aux_output_index}"
            return [
                # the Auxiliary Output must output a static level, otherwise a signal is added to the bias
                [f"{aux_output}/outputselect", -1],  # -1 = Manual
                [f"{aux_output}/preoffset", 0.0],
                [f"{aux_output}/scale", 1.0],
                # adds the signal that is present at Aux Input 1 to the Signal Output
                [f"/{self.device_id}/sigouts/0/add", 1],
            ]

        return []  # External, the bias is applied by another instrument

    def get_bias_value_settings(self, value: float) -> list[list[Any]]:
        """Return the settings that apply the bias 'value' in V using the selected bias source."""
        if self.bias_source == BIAS_INTERNAL:
            return [[f"/{self.device_id}/imps/0/bias/value", float(value)]]

        if self.bias_source == BIAS_AUX_OUTPUT:
            return [[f"/{self.device_id}/auxouts/{self.aux_output_index}/offset", float(value)]]

        return []  # External, the bias is applied by another instrument

    def get_bias_reset_settings(self) -> list[list[Any]]:
        """Return the settings that set the bias back to 0 V and switch the bias source off."""
        if self.bias_source == BIAS_INTERNAL:
            return [
                [f"/{self.device_id}/imps/0/bias/value", 0.0],
                [f"/{self.device_id}/imps/0/bias/enable", 0],
            ]

        if self.bias_source == BIAS_AUX_OUTPUT:
            return [
                [f"/{self.device_id}/auxouts/{self.aux_output_index}/offset", 0.0],
                [f"/{self.device_id}/sigouts/0/add", 0],
            ]

        return []  # External, the bias is applied by another instrument

    def get_bias_value(self) -> float:
        """Return the DC bias in V that is currently set at the selected bias source."""
        if self.bias_source == BIAS_INTERNAL:
            return float(self.daq.getDouble(f"/{self.device_id}/imps/0/bias/value"))

        if self.bias_source == BIAS_AUX_OUTPUT:
            return float(self.daq.getDouble(f"/{self.device_id}/auxouts/{self.aux_output_index}/offset"))

        return float("nan")  # External, the applied bias is unknown to this driver

    def set_output_range(self, bias: float) -> None:
        """Select an output range wide enough for drive amplitude plus DC bias 'bias' in V.

        The bias of the sources "Internal" and "Aux Output" is added as an offset to the Signal Output, and the output
        range must cover the sum of drive amplitude and offset. If the range is too small, the instrument clamps the
        bias without any error, e.g. to +/-1 V in the 1 V range.

        The range is written on its own and synchronized before any bias is written, and it is read back, because a
        range change sent in the same list as the bias did not take effect in time during a bias sweep.

        With a bias source, the 10 mV and 100 mV ranges are not used. This avoids range switching for small bias values
        and matches the behaviour of earlier driver versions, which left the instrument in the 1 V range.

        The range is only increased within a run, so that a bias sweep does not switch the output back and forth.
        """
        # The drive amplitude is treated as RMS value, so its peak value is used as worst case.
        required_voltage = 2**0.5 * abs(self.value_rms)
        minimum_range = OUTPUT_RANGES[0]
        if self.bias_source != BIAS_EXTERNAL:
            required_voltage += abs(float(bias))
            minimum_range = 1.0

        if required_voltage > OUTPUT_RANGES[-1]:
            msg = (
                f"The MFIA cannot apply a DC bias of {bias} V together with a drive amplitude of {self.value_rms} V, "
                f"as the sum exceeds the largest output range of {OUTPUT_RANGES[-1]} V. Please reduce bias or drive "
                f"amplitude, or use an external bias tee."
            )
            raise ValueError(msg)

        new_range = min(
            output_range for output_range in OUTPUT_RANGES if output_range >= max(required_voltage, minimum_range)
        )

        if self.output_range is not None and new_range <= self.output_range:
            return

        self.daq.set([[f"/{self.device_id}/imps/0/output/range", new_range]])
        self.daq.sync()

        active_range = self.daq.getDouble(f"/{self.device_id}/imps/0/output/range")
        if abs(active_range - new_range) > 1e-3 * new_range:  # relative tolerance
            msg = (
                f"The MFIA did not switch to the output range of {new_range} V needed for a DC bias of {bias} V, it "
                f"reports an output range of {active_range} V."
            )
            raise ValueError(msg)

        self.output_range = new_range

    def verify_bias_value(self, bias: float) -> None:
        """Check that the instrument really applies the requested DC bias 'bias' in V.

        The instrument does not report an error for a bias outside its limits, it clamps the value instead. Without
        this check, the measurement would continue at a wrong bias.
        """
        if self.bias_source == BIAS_EXTERNAL:
            return

        applied_bias = self.get_bias_value()
        if abs(applied_bias - float(bias)) > self.bias_tolerance:
            msg = (
                f"The MFIA did not apply the requested DC bias of {bias} V, it reports {applied_bias} V instead "
                f"(output range {self.output_range} V). The bias is limited by the output range and, in 4-Terminal "
                f"mode, by the common mode input range of about +/-3 V. Please use 2-Terminal mode or an external "
                f"bias tee for larger bias voltages."
            )
            raise ValueError(msg)

    """ here, communication commands are wrapped into python convenience functions """

    def subscribe_polling_topic(self, retries: int = 5) -> None:
        """Subscribe to the impedance samples, retrying a few times."""
        for _ in range(retries):
            try:
                self.daq.subscribe(self.polling_topic)
            except Exception:  # the API raises various errors, retried and reported below
                error("Unable to subscribe polling topic of Zurich Instruments MFIA")
            else:
                return

        msg = f"Unable to subscribe to the impedance samples of the MFIA with {retries} retries."
        raise RuntimeError(msg)

    def set_output_state(self, state: bool) -> None:
        """Switch the Signal Output of the impedance unit on or off."""
        self.daq.set([[f"/{self.device_id}/imps/0/output/on", 1 if state else 0]])
        self.daq.sync()

    def get_time_constant(self) -> float:
        """Return the time constant in s of the demodulator used by the impedance unit."""
        return float(self.daq.getDouble(f"/{self.device_id}/demods/0/timeconstant"))

    def get_impedance_oscillator(self) -> int:
        """Return the index of the oscillator that drives the impedance measurement."""
        try:
            return int(self.daq.getInt(f"/{self.device_id}/imps/0/demod/oscselect"))
        except Exception:  # node not available on every firmware, the impedance unit then uses oscillator 0
            return 0
