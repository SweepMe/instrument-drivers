# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! device class
# Type: NetworkAnalyzer
# Device: Rohde & Schwarz ZNLE/ZNL
import datetime
import os.path
import re
import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug  # , error
from pysweepme.FolderManager import FolderManager

FoMa = FolderManager()
# __sweep_me_calibrations__ = FoMa.get_path("CALIBRATIONS")

VERBOSE = False
ZNL_DEFAULT_CAL_DIR = r"C:\Users\Public\Documents\Rohde-Schwarz\ZNL\Calibration\Data"
DATA_FMT = "REAL,32"  # valid: "ASCII", "REAL,64", "REAL,32"
# DATA_FMT = "ASCII"
""" VNA nomenclature
    Trace: empty/filled complex data container
        - data trace
        - memory trace (stored as file ?on ZNL?). Static
        - math traces: math  operation on data trace.
    Data is typically the Sij parameter as fn of freq
    Channel: a measurement recipe containing 1 or more traces
    Window: a portion of the screen used to display a diagram
    Diagram: traces + display format from one or more channels
    terminal/port: a hardware measurement/power port (2)
    marker: in a diagram a label for a point
"""


class Device(EmptyDevice):
    """SweepMe driver for the R&S ZNL network analyser (VNA mode only)
    Trace: measured data, Channel: how trace is meas, contains traces
    Windows: displays for viewing traces
    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "ZNL"  # short name will be shown in the sequencer
        self.port_manager = True
        # timeout only for write&read, SRQ&STB have own timeout
        self.timeout = 5
        self.port_properties = {
            # only for write&read messages, SRQ&STB commands have own timeout
            "timeout": self.timeout,
            # "GPIB_EOLwrite": "\n",
            # "GPIB_EOLread": "\n",
            # "debug" : True
        }
        # @Remco: can we delete?
        # self.port.port.read_termination='\n'
        # self.port.port.write_termination='\n'
        self.port_types = ["GPIB", "TCPIP"]

        self.data_format_type = DATA_FMT
        self.variables = [""]
        self.units = [""]
        self.plottype = []
        self.savetype = []
        self.results = []

        # """ Intermediate Filter bandwiths"""
        self.IF_bandwidth_values = [
            1, 1.5, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500, 700, 1e3, 1.5e3,
            2e3, 3e3, 5e3, 7e3, 10e3, 15e3, 20e3, 30e3, 50e3, 70e3, 100e3, 150e3, 200e3, 300e3,
            500e3
        ]

        self.calibration_file_extensions = [".cal"]

    def set_GUIparameter(self):
        gui_parameters = {
            "Terminals": "1,2",
            "Sparameters": "",
            # Calibrations file from Module not from driver
            "Calibration": [""],
            "Average": 1,
            "SourcePower": ["Min", "Max"] + [f"{i}" for i in range(-95, 30, 5)],
            "SourceAttenuation": ["Auto"] + [f"{i}" for i in range(0, 70, 5)],
            "IFBandwidth": [f"{int(x)!s}" for x in self.IF_bandwidth_values],
            "Correction": ["On", "Off"],
            "Trigger": [
                "Internal",
                "External",
            ],  # IMMediate | EXTernal | MANual | MULTiple
            "TriggerDelay": 0.0,
            # All frequencies in Hz
            "FrequencyStart": 10e6,
            "FrequencyEnd": 50e6,
            "FrequencyStepPointsType": [
                "Linear (points)",
                "Linear (steps in Hz)",
                "Logarithmic (points)",
            ],
            "FrequencyStepPoints": 1e6,
            "Display": True,
        }

        return gui_parameters

    def get_GUIparameter(self, parameter):
        # to see all available keys you get from the GUI:
        # print(parameter)
        self.f_start = parameter["FrequencyStart"]
        self.f_end = parameter["FrequencyEnd"]
        self.f_type = parameter["FrequencyStepPointsType"]
        self.f_steppoints = parameter["FrequencyStepPoints"]

        self.source_power = parameter["SourcePower"]
        self.source_attenuation = parameter["SourceAttenuation"]
        self.IF_bandwidth = parameter["IFBandwidth"]

        self.calibration_file_name = parameter["Calibration"]

        self.number_averages = int(parameter["Average"])
        self.correction = parameter["Correction"]
        self.trigger_source = parameter["Trigger"]
        self.trigger_delay = parameter["TriggerDelay"]

        self.update_display = parameter["Display"]

        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        # parse user inputs for terminals (meas channels) and or sparams
        terminals = re.split(" |,|:|;", parameter["Terminals"])
        try:
            self.terminals = list(map(int, terminals))
        except ValueError:
            self.terminals = []

        # parse Spar names if specified directly by user, e.g. "S11, S31"
        self.Sparam_names = []
        sparam_names = re.split(" |,|:|;", parameter["Sparameters"])
        is_Spar_correct = [  # is_correct.spar()
            x.startswith("S") and len(x) == 3 and x[1:].isdigit() for x in sparam_names
        ]
        # case one spar were correct: use those
        if len(is_Spar_correct) > 0 and all(is_Spar_correct):
            self.Sparam_names = sparam_names
        # c2: spar werent specified, construct all spars from terminals
        elif not any(is_Spar_correct):
            self.Sparam_names = [f"S{i}{j}" for i in self.terminals for j in self.terminals]
        else:
            # do not raise error to avoid spamming debug promp
            pass

        self.variables += self.Sparam_names
        self.units += [""] * len(self.Sparam_names)
        self.plottype += [False] * len(self.Sparam_names)
        self.savetype += [True] * len(self.Sparam_names)

    def initialize(self):
        # check whether S-parameters are correctly defined
        if len(self.Sparam_names) == 0:
            raise ValueError(
                """Unable to parse S-parameters. Please define S-parameters
                in the field 'S-parameters  "e.g. 'S11, S21' or check terminals
                are  correctly defined eg. 1,2""",
            )

        # check whether terminals are defined
        if len(self.terminals) == 0:
            raise ValueError(
                """ Unable to parse terminal numbers. Please define the
                terminals to be used in the field 'Terminals' e.g. '1, 2'.""",
            )

        # Clear the event status registers and empty the error queue
        print("Connected to ZNL: ", self.port.get_identification())
        self.clear_status()
        self.reset()

        # Deletes all measurements on the PNA.
        # probably excludes calibration from dynamic mem
        self.delete_all_traces()
        self.set_trigger_continuous(0)

        # clear all errors
        self.port.write("SYSTem:ERRor:CLEar:ALL")
        self.port.write("SYSTem:ERRor:CLEar:REMote")

        self.set_data_transfer_format(self.data_format_type)

    def configure(self):
        """Configure the ZNL VNA"""
        self.window_number = 1
        channel_number = 1  # only one channel is needed
        self.f_start = float(self.f_start)
        self.f_end = float(self.f_end)
        self.f_steppoints = float(self.f_steppoints)

        # Define measurements before the sweep creation
        for spar in self.Sparam_names:
            # auto_tracenames --> f"TrC{channel}_{spar_name}"
            self.make_param_trace(spar, trace_name="Auto", channel=1)

        # instrument settings
        self.set_power_level(self.source_power)  # on all terminals
        self.set_IF_bandwidth(self.IF_bandwidth)
        if self.f_type.startswith("Linear"):
            sweep_type = "LIN"
        elif self.f_type.startswith("Log"):
            sweep_type = "LOG"
        else:
            raise NotImplementedError("Only Linear/Log (points|steps) sweeps supported")

        # configure sweep from sweepMe inputs (points or steps)
        if "points" in self.f_type:
            self.n_points = int(self.f_steppoints)
            if sweep_type == "LIN":
                self.frequency_values = np.linspace(self.f_start, self.f_end, self.n_points)
            elif self.f_type.startswith("Logarithmic"):
                self.frequency_values = np.logspace(
                    np.log10(self.f_start),
                    np.log10(self.f_end),
                    self.n_points,
                )
        elif "steps" in self.f_type:
            self.frequency_values = np.arange(
                self.f_start,
                self.f_end + self.f_steppoints,
                self.f_steppoints,
            )
            self.n_points = len(self.frequency_values)
            self.f_start = self.frequency_values[0]  # Start
            self.f_end = self.frequency_values[-1]  # End
        # apply sweep and sweep dwell times
        self.set_sweep_type(sweep_type, channel=1)
        self.set_sweep_frequency_limits(self.f_start, self.f_end, channel=1)
        self.set_sweep_num_points(self.n_points)

        self.set_sweep_dwell_time(channel=1, dt=0)
        self.set_sweep_duration(channel=1, dt_in_s="Auto")

        self.set_display_update(self.update_display)
        # could lock display
        if self.update_display:
            # switch window on
            self.set_display_window_enabled(state=1, win_number=self.window_number)
            # DISPLAY Sparameter TRACES
            tr_names = [f"TrC{channel_number}_{sp_name}" for sp_name in self.Sparam_names]
            # self.set_active_trace(trace_name)
            self.display_traces(tr_names=tr_names, win_num=self.window_number, state=1)
            # # better alternative: ?
            # self.display_all_data_traces(window_num=self.window_number, channel =ch)

        self.set_averaging(channel=channel_number, n_avg=self.number_averages)
        self.clear_averages(channel=channel_number)

        self.set_trigger_source(self.trigger_source)
        self.set_trigger_delay(self.trigger_delay)  # trigger delay
        self.set_continuous_meas(on=False)  # endless loop off

        cal_state = self.get_calibration_state(channel=channel_number)
        if VERBOSE:
            print("ZNL Calibration State: ", cal_state)
        correction_on = 1 if self.correction == "On" else 0
        self.set_calibration_state(channel_number, state=correction_on)

        # if user specified a calibration file to be loaded
        if len(self.calibration_file_name) > 0 & correction_on:
            self.apply_calibration(channel=1, from_file=self.calibration_file_name)
        elif correction_on and not self.calibration_file_name:
            raise OSError("Correction 'ON' Requested but no calibration file specified.")

    def poweron(self):
        self.set_output_on()

    def poweroff(self):
        self.set_output_off()

    def unconfigure(self):
        self.check_errors()

        # abort all ongoing sweeps
        # self.port.write(":ABOR")

        self.set_trigger_source("IMMediate", channel=1)
        self.set_trigger_continuous()  # switch on continous measurement
        self.set_display_update(1)

    def trigger_ready(self):
        pass

    def measure(self):
        channel = 1
        # in case long meas
        meas_time = float(self.get_sweep_duration(channel=channel))
        if VERBOSE:
            print("Expected measurement time ", meas_time)
        self.port.port.timeout = max(200.0, meas_time * float(self.number_averages) * 1.6 * 1000.0)  # ms

        # In case n averages require n software trigs (1 ext)
        n_software_trig = 1
        for j in range(n_software_trig):
            start_t = time.time()
            # CHANGED: removed the *OPC without question mark
            self.port.write(":INIT{channel}:IMM")
            self.check_operation_complete()

            if VERBOSE:
                print(f"done {j} of {len(range(n_software_trig))} measurements")
                print(f"data read and transfered in {time.time() - start_t:.2f}s")

        self.port.port.timeout = self.timeout * 1000  # ms
        if VERBOSE:
            print("ZNL measurement complete")

    def request_result(self):
        self.check_operation_complete()

    def read_result(self):
        channel = 1

        # UNCLEAR WHETHER THIS RETURNS ASCII DATA
        frequencies_raw = self.get_applied_frequency_data(channel=channel)
        # print("raw frequencies number = ", len(frequencies_raw))
        frequencies = self.parse_data(frequencies_raw)  # X-axis is ASCII or BIN
        # frequencies = np.fromstring(frequencies_raw, sep=",", dtype="d")  # x-axis is ASCII only
        # print("Parsed frequencies = ", frequencies.shape)
        self.results.append(frequencies)

        for spar_name in self.Sparam_names:
            tr_name = f"TrC{channel}_{spar_name}"
            data_str = self.get_trace_data(channel=channel, trace_name=tr_name, fmt="SDAT")
            # print(data_str)
            self.results.append(self.parse_data(data_str))

    def call(self):
        return self.results

    def finish(self):
        if not self.update_display:
            self.update_display_once()
            # self.port.write('SYST:TSLock SCR') #doesnt look like a ZNL command

    # """ further function as needed by this device class are defined here """

    def binblock_raw(self, data_in, dtype_) -> np.array:
        """Convert binary data to numeric"""
        # Grab the beginning section of the data file, which will contain the header.
        header = str(data_in[0:12])
        # Find the start position of the IEEE header, which starts with a '#'.
        startpos = header.find("#")
        # check for problem with start position.
        if startpos < 0:
            raise OSError("No start of block found")

        # number after '#' symbol is the number of digits in the block length.
        digits_block_length = int(header[startpos + 1])

        # Now we know how many digits are in the size value, get the size of the data file
        image_size = int(header[startpos + 2 : startpos + 2 + digits_block_length])

        # Get the length from the header
        offset = startpos + digits_block_length

        dtype_ = np.dtype(dtype_)
        return np.frombuffer(data_in[offset : offset + image_size], dtype=dtype_)

    def find_calibrations(self, cal_dir=ZNL_DEFAULT_CAL_DIR) -> list:
        """Called by the sweepMe NetworkAnalyser module returns avalable calibrations on ZNL
        at default driectory
        """
        try:
            search_pattern = os.path.join(cal_dir, "*.cal")
            return self.list_available_calibrations(search_pattern)
        # Port still not declared
        except AttributeError:
            print("ZNL not yet connected - please choose port")
            return []

    def parse_data(self, data_str):
        """Parse the incoming ASCII or BIN data which generally is complex"""
        # For ascii data represented as a flat str 'R1, Z1, R2, Z2,...'
        if self.data_format_type == "ASCII":
            data = np.fromstring(data_str, sep=",", dtype="d")

        elif self.data_format_type == "REAL,64" or self.data_format_type == "REAL,32":
            dtype = "f8" if self.data_format_type == "REAL,64" else "f4"
            data = self.binblock_raw(data_str, dtype)

        else:
            err_mesg = f"""
                Invalid data format {self.data_format_type}: Use 'ASCII', 'REAL,32'or 'REAL,64' """
            debug(err_mesg)
            return False

        # deal with complex data
        if len(data) == 2 * len(self.frequency_values):
            return data[::2] + 1.0j * data[1::2]
        elif len(data) == len(self.frequency_values):
            return data
        else:
            raise ValueError("ZNL data not of length compatible with sweep", data)

    # """ WRAPPED SCIPI COMMANDS """

    def clear_averages(self, channel=1):
        self.port.write(f":SENS{channel}:AVER:CLE;*WAI")

    def get_identification(self):
        self.write("*IDN?")
        return self.port.read()

    def apply_calibration(self, channel=1, from_file=""):
        """Calculates the sys error correction data from the
        acquired calibration meas. results stores it and applies it to
        the calibrated channel(s).
        """
        if not from_file:
            # use cal in active memmory
            self.port.write(f":SENSe{channel}:CORRection:COLLect:SAVE:SELected")
        else:
            if from_file != "None":
                self.port.write(f":MMEM:LOAD:CORR {channel}, '{from_file}'")

    def list_available_calibrations(self, search_pattern=r"*.cal") -> list:
        self.port.write(f"MMEM:CAT? {search_pattern}")
        return self.port.read().split(",")

    def delete_all_traces(self):
        """Delete traces for all or a specific channel"""
        self.port.write("CALC:PAR:DEL:ALL")

    def del_specific_trace(self, channel, tr_name):
        self.port.write(f"CALC{channel}:PAR:DEL {tr_name}")

    def load_calibration_from_file(self, fname, channel=1):
        """Analyzer always uses default cal pool dir
        C:\\Users\\Public\\Documents\\Rohde-Schwarz\\ZNL\\Calibration\\Data.
        """
        if fname != "None":
            self.port.write(f"MMEM:LOAD:CORR {channel}, {fname}")

    def save_calibration(self, channel=1, fname=""):
        """Saved to C:\\Users\\Public\\Documents\\Rohde-Schwarz\\ZNL\\Calibration\\Data
        with a .cal extension
        """
        if not fname:
            fname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "sweepMe_ZNL"

        self.port.write(f"MMEMory:STORe:CORRection {channel},{fname}")

    def make_param_trace(self, spar_name, trace_name="Auto", channel=1):
        """CALCulate<Ch>:PARameter:DEFine <TraceName>, <Result>[, <TestPortNum>]
         Creates a trace and assigns it a channel #, a name and a meas parameter.
        The trace is not displayed. Define doesnt follow ZNL nomenclature
        The command SDefine uses a complete par list with compatible names
        """
        if trace_name == "Auto":
            trace_name = f"TrC{channel}_{spar_name}"

        # self.port.write(f"Calc{channel}:PAR:DEF '{trace_name}', {spar_name}")
        self.port.write(f"Calc{channel}:PAR:SDEF '{trace_name}', '{spar_name}'")
        # self.set_active_trace(trace_name)

    def set_active_trace(self, trace_name, channel=1):
        """CALCulate<Ch>:PARameter:SELect"""
        self.port.write(f"Calc{channel}:PAR:SEL '{trace_name}'")

    def get_calibration_state(self, channel=1):
        self.port.write(f"SENSe{channel}:CORRection:SSTate?")
        return self.port.read()

    def set_calibration_state(self, channel=1, state=1):
        onoff = "ON" if state else "OFF"
        self.port.write(f"SENSe{channel}:CORR {onoff}")

    def set_continuous_meas(self, channel=1, on: bool = 0):
        """Set continuous meas on 1 or all (None) channel"""
        onoff = "ON" if on else "OFF"
        self.port.write(f":INIT{channel}:CONT {onoff}")
        if channel is None:
            self.port.write(f":INIT:CONT:ALL {onoff}")

    def reset(self):
        self.port.write("*RST")

    def clear_status(self):
        self.port.write("*CLS")

    def set_data_transfer_format(self, fmt_type):
        """Selects the fmt for numeric data transfer to & from the analyzer."""
        allowed_fmts = ["ASCII", "REAL,64", "REAL,32"]

        if fmt_type.upper() not in allowed_fmts:
            raise OSError(f"Data format {fmt_type} not in{allowed_fmts}")
        self.port.write(f":FORM:DATA {fmt_type}")

    def get_data_transfer_format(self):
        self.port.write(":FORMat:DATA?")
        return self.port.read()

    def set_default_data_directory(self, dir_path):
        self.port.write(f"MMEMory:CDIRectory DEFault {dir_path}")

    def display_traces(self, state: bool, tr_names: list, win_num=1):
        onoff = "ON" if state else "OFF"
        for name in tr_names:
            # tr_num = self.get_trace_number(name)
            self.set_active_trace(name)
            self.port.write(f":DISP:WIND{win_num}:STAT ON")
            self.port.write(f"DISP:WIND{win_num}:TRACe:EFEED '{name}'")
            self.port.write(f"DISP:WIND{win_num}:TRACe:SHOW '{name}', {onoff}")

    def display_all_data_traces(self, window_num=1):
        self.port.write(f"DISP:WIND{window_num}:TRACe DALL")

    def get_displayed_traces(self, win_number):
        """List all displayed traces
        returns unparsed string of style 'Tr_num, Tr_number' ...
        """
        self.port.write(f"DISP:WIND{win_number}:TRAC:CAT?")
        # should do some parsing because will get trace numbers too
        # 'Tr_num, Tr_number'
        return self.port.read()

    def set_display_update(self, state: bool):
        """0,1, ON, OFF accepted"""
        if type(state) == bool:
            state = int(state)
        self.port.write(f":SYSTEM:DISPLAY:UPDATE {state}")

    def set_display_window_enabled(self, state: bool, win_number: int = 1):
        onoff = "ON" if state else "OFF"
        self.port.write(f":DISP:WIND{win_number}:STAT {onoff}")
        # TODO: needed?
        self.port.write(f":DISP:WIND{win_number}:NAME 'SweepMe!'")

    def set_IF_bandwidth(self, bandwidth, channel=1):
        """Set intermediate frequency filter BW"""
        self.port.write(f"SENS{channel}:BWID {bandwidth}")

    def set_IF_selectivity(self, selectivity, channel=1):
        """SENSe<Ch>:]BWIDth[:RESolution]:SELect
        NORMal | MEDium | HIGH
        """
        # TODO do we need to change settling time somewhere?
        self.port.write(f"SENS{channel}:BWID:SEL {selectivity}")

    def set_output_enabled(self, state: bool):
        """enable/disable power output"""
        onoff = "ON" if state else "OFF"
        self.port.write(f"OUTP {onoff}")
        self.port.write("*OPC?")
        self.port.read()  # opc result

    def set_output_off(self):
        self.set_output_enabled(0)

    def set_output_on(self):
        self.set_output_enabled(1)

    def set_power_level(self, power_dB: float, channel: int = 1):
        """Set the source power level for a channel"""
        # TO DO int or float?
        self.port.write(f"SOUR{channel}:POW {power_dB}")

    # def set_sweep_mode(self, mode):
    #     self.port.write(f"SENSE:SWEEP:MODE {mode}")

    def get_applied_frequency_data(self, channel=1):
        """Get the frequencies that were applied during sweep (as
        opposed to the requested frequencies)
        """
        self.port.write(f"CALC{channel}:DATA:STIM?")

        if self.data_format_type == "ASCII":
            out = self.port.read()
        else:
            out = self.port.port.read_raw()
        return out

    def set_averaging(self, n_avg, channel=1):
        onoff = "OFF" if n_avg == 1 else "ON"
        self.port.write(f":SENS{channel}:AVER:COUN {n_avg}; :AVER {onoff}; *WAI")
        self.port.write(f"SENS{channel}:SWE:COUN {n_avg}")

    def set_sweep_frequency_limits(self, start, end, channel=1):
        """Set frequency sweep start and end.
        Multi segment sweeps not supported
        """
        self.port.write(f"SENS{channel}:FREQ:START {start}")
        self.port.write(f"SENS{channel}:FREQ:STOP {end}")

    def get_sweep_frequency_limits(self, channel=1):
        """Get sweep frequency limits"""
        self.port.write(f"SENS{channel}:FREQ:STAR?; STOP?")
        # self.port.write(f"SENS{channel}SEGM:FREQ:STAR?; STOP?")
        return self.port.read()

    def set_sweep_frequency_start(self, start, channel=1):
        self.port.write(f"SENS{channel}:FREQ:START {start}")

    def set_sweep_frequency_end(self, end, channel=1):
        self.port.write(f"SENS{channel}:FREQ:STOP {end}")

    def set_sweep_num_points(self, n_points, channel=1):
        self.port.write(f":SENS{channel}:SWE:POIN {n_points}")

    def get_sweep_num_points(self, channel=1):
        raise NotImplementedError

    def set_sweep_duration(self, dt_in_s="Auto", channel=1):
        if dt_in_s == "Auto":
            self.port.write(f":SENS{channel}:SWE:TIME:AUTO ON")
        else:
            raise NotImplementedError
            # check the time format needed by VISA (unclear)
            # self.port.write(f":SENS{channel}:SWE:TIME {int(dt_in_s)}")

    def set_sweep_dwell_time(self, channel=1, dt=0):
        """Set delay between partial measurements
        If Sparam choices require two port configurations and meas mode is 'chopped'
        this delay is applied twice per freq, else once
        """
        self.port.write(f":SENS{channel}:SWE:DWELL {dt}")

    def set_sweep_type(self, sweep_type, channel=1):
        """LINear | LOGarithmic | CW | POINt | SEGMent"""
        self.port.write(f":SENS{channel}:SWE:TYPE {sweep_type}")

    def get_sweep_duration(self, channel=1) -> float:
        self.port.write(f"SENSE{channel}:SWE:TIME?")
        return self.port.read()

    def get_error(self):
        self.port.write("SYST:ERR?")
        return self.port.read()

    def get_error_list(self):
        """Get all errors as list. Empty list if no error"""
        self.port.write("SYST:ERR:LIST? REMote")
        errors_str = self.port.read()
        errors_str = errors_str.replace("'", "").replace('"', "")

        errors = errors_str.split(",")
        # print("errors_str:", errors_str, "err[0]:'", errors[0], "'")
        errors = [tuple(err.split("|")[0:3]) for err in errors]  # (code, message, command)
        error_messages = [f"{err[1]} on command {err[2]}" for err in errors if int(err[0]) != 0]
        if not error_messages:
            return ["No errors"]
        return error_messages

    def check_error(self):
        """Check for a single error (wrapping)"""
        error = self.get_error()
        errorcode = int(error.split(",")[0])
        if errorcode == 0:
            return None
        else:
            print(f"ZNL error: {error}")
            return error

    def check_errors(self):
        """Check for errors in err buffer"""
        errors = self.get_error_list()
        if errors:
            print(f"ZNL errors: {'; '.join(errors)}")
        return errors

    def check_operation_complete(self):
        """Hold the IO bus until the instrument has completed all commands"""
        self.port.write("*OPC?")
        return self.port.read()  # opc

    def get_trace_data(self, channel, trace_name, fmt="SDAT"):
        """Get the trace data from the ZNL - fmt specifies data processing
        SDAT: unprocessed (correction ?)
        MDAT: sdat + mathematics from :CALCULATE commands
        UCData: uncalibrated
        FDATA: formatted for display on ZNL window (|Z|, Re(Z), etc
        """
        self.port.write(f":CALCULATE{channel}:DATA:TRAC? '{trace_name}', {fmt}")
        t0 = time.time()
        if self.data_format_type == "ASCII":
            ascdata_in = self.port.read()
            self.check_operation_complete()
            t1 = time.time()
            if VERBOSE:
                print(f"spar data read and transfered in {t1 - t0:.4f}s")
            return ascdata_in
        else:
            # read_raw needed if driver used outside sweepMe
            bindata_in = self.port.port.read_raw()
            self.check_operation_complete()
            t1 = time.time()
            if VERBOSE:
                print(f"spar data read and transfered in {t1 - t0:.2f}s")
            return bindata_in

    def get_trace_number(self, tr_name):
        self.port.write(f"CONFigure:TRACe:NAME:ID? {tr_name}")
        return self.port.read()

    def get_trigger_delay(self, channel):
        raise NotImplementedError

    def set_trigger_delay(self, delay_s, channel=1):
        self.port.write(f"TRIG{channel}:HOLD {delay_s}")

    def set_trigger_source(self, trigger_source, channel=1):
        """IMMediate | EXTernal | MANual | MULTiple
        sequence not supported
        """
        trig_src_cmd = trigger_source
        if trigger_source == "Internal":
            trig_src_cmd = "IMM"
        self.port.write(f"TRIG{channel}:SOURCE {trig_src_cmd}")
        self.port.write("*TRG;*OPC")

    def get_trigger_source(self, channel):
        self.port.write(f"Trig{channel}:Sour?")
        return self.port.read()

    def set_trigger_continuous(self, state=1):
        onoff = "ON" if state else 0
        self.port.write(f"INIT:CONT {onoff}")

    def update_display_once(self):
        self.port.write("SYSTem:DISPlay:UPDate ONCE")

    def set_vna_mode(self):
        """In case B1 option was purchased"""
        self.port.write("INST:SEL VNA")  # SAN for spectr analyser

    def get_znl_working_dir(self):
        self.port.write("MMEMory:CDIRectory?")
        return self.port.read()

    def set_znl_working_dir(self, dir_=""):
        """Set the ZNL's internal current working directory"""
        default_dir = r"C:\Users\Public\Documents\Rohde-Schwarz\Vna"  # \Calibration\Data"
        #  = r"C:\Users\Public\Documents\Rohde-Schwarz\ZNL\Calibration\Data"
        if not dir_:
            dir_ = default_dir
        self.port.write(f"MMEMory:CDIRectory {dir_}")
