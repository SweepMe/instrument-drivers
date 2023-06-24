# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021 SweepMe! GmbH
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
# Device: Keysight PNA


# import time
import datetime
import numpy as np
import os

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import error, debug
from pysweepme import FolderManager

FoMa = FolderManager.FolderManager()


class Device(EmptyDevice):
    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "PNA"  # short name will be shown in the sequencer

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]

        self.port_properties = {
            "timeout": 20.0,
        }

        self.port_identification = [
            "Agilent Technologies"
        ]  # temporarily not used by SweepMe!

        """
        Online command reference:
        http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/SCPI_Command_Tree.htm
        """

        self.data_format_type = "REAL,64"
        # options:
        # "ASC" -> ascii,
        # "REAL,32" -> 32bit floating point format,
        # "REAL,64" -> 64bit floating point format

        # fmt:off
        self.if_bandwidth_values = [
            1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500, 700, 1e3,
            1.5e3, 2e3, 3e3, 5e3, 7e3, 10e3, 15e3, 20e3, 30e3, 50e3, 70e3, 100e3,
            150e3, 200e3, 280e3, 360e3, 600e3, 1e6, 1.5e6, 2e6, 3e6, 5e6, 7e6,
            10e6, 15e6
        ]
        # fmt:on

        self.calibration_file_extensions = [".csa", ".cst", ".sta", ".cal"]

    def find_calibrations(self):

        calibration_files = []

        """
        calibration_file_extensions = [".csa", ".cst", ".sta", ".cal"]
        calibration_folder = FoMa.get_path("CALIBRATIONS")
        ## add files stored in public folder CalibrationsFiles
        for cal_file in os.listdir(calibration_folder):
            # print(cal_file)
            for ext in self.calibration_file_extensions:
                if cal_file.endswith(ext):
                    calibration_files.append(cal_file)
        """

        try:
            # add files stored on PNA
            self.port.write(":CSET:CAT?")
            answer = self.port.read()
            # print("Calibrations stored:", answer)
            calibration_files += answer.split(",")
        except Exception:
            error("Failed to retrieve calibrations from Keysight/Agilent PNA/VNA.")

        calibration_files += ["None"]  # can be used to deselect a calibration

        # return a list of strings that can be selected by the user
        return calibration_files

    def get_calibrationfile_properties(self, port):

        calibration_file_extensions = self.calibration_file_extensions
        calibration_file_names = [""]  # this means any name is accepted

        return calibration_file_extensions, calibration_file_names

    def set_GUIparameter(self):

        GUIparameter = {
            "Terminals": "1,2",
            "Sparameters": "",
            # lets insert the names of all found calibration files
            # "Calibration": self.get_Calibrations(), "Average": 1,
            "SourcePower": ["Min", "Max"] + ["%i" % i for i in range(-95, 30, 5)],
            "SourceAttenuation": ["Auto"] + ["%i" % i for i in range(0, 70, 5)],
            "IFBandwidth": ["%s" % str(int(x)) for x in self.if_bandwidth_values],
            "Correction": ["On", "Off"],
            "Trigger": ["Internal", "External"],
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

        return GUIparameter

    def get_GUIparameter(self, parameter):

        # see all available keys you get from the GUI
        # print(parameter)

        self.f_start = float(parameter["FrequencyStart"])
        self.f_end = float(parameter["FrequencyEnd"])
        self.f_type = parameter["FrequencyStepPointsType"]
        self.f_steppoints = float(parameter["FrequencyStepPoints"])

        self.source_power = parameter["SourcePower"]
        self.source_attenuation = parameter["SourceAttenuation"]
        self.if_bandwidth = parameter["IFBandwidth"]

        self.calibration_file_name = parameter["Calibration"]

        self.number_averages = int(parameter["Average"])
        self.correction = parameter["Correction"]
        self.trigger_state = parameter["Trigger"]
        self.trigger_delay = parameter["TriggerDelay"]

        self.update_display = parameter["Display"]

        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        self.Sparameters = []
        self.terminals = []

        try:
            self.terminals = list(
                map(
                    int,
                    parameter["Terminals"]
                    .replace(" ", "")
                    .replace(";", ",")
                    .replace(",,", ",")
                    .split(","),
                )
            )
        except Exception:
            self.terminals = []

        try:
            sparameters = (
                parameter["Sparameters"]
                .replace(" ", "")
                .replace(";", ",")
                .replace(",,", ",")
                .split(",")
            )
        except Exception:
            sparameters = []

        is_Spar_correct = [
            x.startswith("S") and len(x) == 3 and x[1:].isdigit() for x in sparameters
        ]
        # this is the case if the user defines the S-parameter directly, e.g. "S11, S31"
        if len(is_Spar_correct) > 0 and all(is_Spar_correct):
            self.Sparameters = sparameters

        # this is the case if te user defines just the terminal port numbers
        # and we have to construct all possible S-parameters
        elif not any(is_Spar_correct):
            # create variable and units depending on the number of terminals
            for i in self.terminals:
                for j in self.terminals:
                    self.Sparameters.append("S%i%i" % (j, i))
        # this is the case if none above the options is used and self.Sparameters will
        # remain empty so that we can throw an error message
        # TODO SWITCH TO RAISE!
        else:
            pass

        self.variables += self.Sparameters
        self.units += [""] * len(self.Sparameters)
        self.plottype += [False] * len(self.Sparameters)
        self.savetype += [True] * len(self.Sparameters)

        # print(self.terminals)
        # print(self.Sparameters)

    def initialize(self):

        # check whether S-parameters are correctly defined
        if len(self.Sparameters) == 0:
            raise Exception(
                """Unable to parse S-parameters. Please define S-parameters in th
                e field 'S-parameters' e.g. 'S11, S21'."""
            )

        # check whether terminals are defined
        if len(self.terminals) == 0:
            raise Exception(
                """Unable to parse terminal numbers. Please define
                the terminals to be used in the field 'Terminals' e.g. '1, 2'."""
            )

        # Clear the event status registers and empty the error queue
        self.port.write("*CLS")

        # cset = "<name>"
        # self.port.write(':MMEM:LOAD:CSTATE "%s"' % cset)
        # self.port.write("SYST:ERR?")
        # print(self.port.read())

        # self.port.write("*IDN?")
        # answer = self.port.read()
        # # print(answer)

        # Data transfer format
        self.port.write(
            ":FORM:DATA %s" % self.data_format_type
        )  # as defined in __init__

        # self.port.write(":FORMat:DATA?")
        # answer = self.port.read()
        # print("Format Spar Data:", answer)

        """Set binary data order:"""
        # self.port.write(":FORM:BORD NORM") # options: NORM or SWAP
        self.port.write(":FORM:BORD SWAP")  # SWAP is needed

    def configure(self):
        # Performs a standard Preset, then deletes the default trace, measurement
        # and window. The PNA screen becomes blank.
        self.port.write("SYST:FPR")
        self.port.write("CALC:PAR:DEL:ALL")  # Deletes all measurements on the PNA.

        self.window_number = 1
        channel_number = 1  # only one channel is needed

        """ Measurements """
        for i, spar in enumerate(self.Sparameters):
            # must be placed before the creation of the sweep
            self.port.write(
                "CALC%i:PAR:DEF:EXT 'Meas%s','%s'" % (channel_number, spar, spar)
            )
            self.port.write(":CALC%i:PAR:SEL 'Meas%s', FAST" % (channel_number, spar))

        """ Power levels """
        for term in self.terminals:
            self.port.write(":SOUR%i:POW%i:COUPLE OFF" % (channel_number, term))
            self.port.write(
                ":SOUR%i:POW%i %s" % (channel_number, term, self.source_power)
            )
            self.port.write(":SOUR%i:POW%i:SLOPE:STATE ON" % (channel_number, 1))
            self.port.write(":SOUR%i:POW%i:SLOPE 0.1" % (channel_number, 1))

            if self.source_attenuation == "Auto":
                self.port.write(
                    ":SOUR%i:POW%i:ATT:Auto On" % (channel_number, term)
                )  # sets auto attenuation on (is default anyway)

            else:
                self.port.write(
                    ":SOUR%i:POW%i:ATT %s"
                    % (channel_number, term, self.source_attenuation)
                )

            # TODO Check if needed:

            # self.port.write(":SOUR%i:POW%i?" % (channel_number,term))
            # print('Port%i Power at ch %i: %s' %(term,channel_number,self.port.read()))
            # self.port.write(":SOUR%i:POW%i:ATT?" % (channel_number,term))
            # print('Port%i Power Attenuation at ch %i: %s'%(term,channel_number,
            #        self.port.read()))

            # self.port.write(":SOUR%i:POW%i? MIN" % (channel_number,term))
            # print('Port%i MIN Power at ch %i: %s' %(term,channel_number,
            #          self.port.read()))
            # self.port.write(":SOUR%i:POW%i? MAX" % (channel_number,term))
            # print('Port%i MAX Power at ch %i: %s' %(term,channel_number,
            #   self.port.read()))

            # self.port.write(":SOUR%i:POW%i:ATT? MIN" % (channel_number,term))
            # print('Port%i MIN Power Attenuation at ch %i: %s' %(
            #       term,channel_number,self.port.read()))
            # self.port.write(":SOUR%i:POW%i:ATT? MAX" % (channel_number,term))
            # print('Port%i MAX Power Attenuation at ch %i: %s'%(
            #       term,channel_number,self.port.read()))

        """ IF bandwidth """
        self.port.write(
            ":SENS%i:BAND %s" % (channel_number, self.if_bandwidth)
        )  # sets if_bandwidth to 300Hz
        self.port.write(
            ":SENS%i:BAND:TRAC Off" % (channel_number)
        )  # sets IF tracking at low frequency off (default is on, but off in ICCAP)

        # TODO Check if needed
        # self.port.write(":SENS%i:BAND?" % (channel_number))
        # print('IF BW at ch %i: %s' % (channel_number, self.port.read()))

        """ Frequency sweep """
        if self.f_type.startswith("Linear"):
            self.port.write(
                ":SENS%i:SWE:TYPE LIN" % (channel_number)
            )  # Linear frequency sweep
        else:
            self.port.write(
                ":SENS%i:SWE:TYPE LOG" % (channel_number)
            )  # Logarithmic frequency sweep

        if "points" in self.f_type:

            self.number_points = int(self.f_steppoints)

            if self.f_type.startswith("Linear"):
                self.frequency_values = np.linspace(
                    float(self.f_start), float(self.f_end), self.number_points
                )
            elif self.f_type.startswith("Logarithmic"):
                self.frequency_values = np.logspace(
                    np.log10(float(self.f_start)),
                    np.log10(float(self.f_end)),
                    self.number_points,
                )

            self.f_start = float(self.f_start)  # Start
            self.f_end = float(self.f_end)  # End

        elif "steps" in self.f_type:

            self.frequency_values = np.arange(
                float(self.f_start),
                float(self.f_end) + float(self.f_steppoints),
                float(self.f_steppoints),
            )
            self.number_points = len(self.frequency_values)

            self.f_start = self.frequency_values[0]  # Start
            self.f_end = self.frequency_values[-1]  # End

        self.port.write(
            ":SENS%i:FREQ:START %s" % (channel_number, str(self.f_start))
        )  # Start
        self.port.write(
            ":SENS%i:FREQ:STOP %s" % (channel_number, str(self.f_end))
        )  # End
        self.port.write(":SENS%i:SWE:POIN %i" % (channel_number, self.number_points))
        self.port.write(":SENS%i:SWE:DWELL 0" % (channel_number))
        # print("Frequency values:", self.number_points)

        """ Sweep time """
        #  automatic sweep time
        self.port.write("SENS%i:SWE:TIME:AUTO ON" % (channel_number))
        # self.port.write("SENS%i:SWE:TIME %s" % (channel_number) , .....) #  sweep time

        """ Trigger Point Off """
        self.port.write(
            ":SENS%i:SWE:TRIG:POIN OFF" % (channel_number)
        )  # pointwise trigger off

        """ Display, Windows, and Traces """
        if not self.update_display:
            self.port.write(":DISP:ENAB OFF")
            self.port.write(":DISP:VIS OFF")
        else:
            self.port.write(":DISP:VIS ON")
            self.port.write(":DISP:ENAB ON")  # Display on
            self.port.write(":DISP:ANN ON")  # Bottom Status Bar On

            self.port.write(
                ":DISP:WIND%i:STAT ON" % self.window_number
            )  # switch window on

            for i, spar in enumerate(self.Sparameters):
                trace_number = i + 1
                self.port.write(
                    "DISP:WIND%i:TRAC%i:FEED 'Meas%s'"
                    % (self.window_number, trace_number, spar)
                )  # Setting a trace to a window based on a channel label
                self.port.write(
                    "DISP:WIND%i:TRAC%i:SEL" % (self.window_number, trace_number)
                )
                self.port.write(
                    "DISP:WIND%i:TRAC%i:STAT ON" % (self.window_number, trace_number)
                )

            self.port.write(
                "DISP:WIND%i:TRAC:Y:COUP:METH WIND" % (self.window_number)
            )  # coupling method of showing traces in a window, option OFF, WIND, ALL
            # self.port.write(":DISP:WIND%i:Y:AUTO" % (self.window_number)) #auto scale
            # self.port.write(":CALC{1-16}:PAR{1-16}:SEL")  # Setting up the active trace

        """ Average """
        if self.number_averages > 1:
            self.port.write(":SENS%i:AVER:STAT ON;*WAI" % (channel_number))  # state
            self.port.write(
                ":SENS%i:AVER:COUN %i;*WAI" % (channel_number, self.number_averages)
            )  # counts
            self.port.write(":SENS%i:AVER:MODE SWEEP;*WAI" % (channel_number))  # mode
            # print("Average Mode: Nav=%i" %(self.number_averages))
            self.port.write(
                ":SENS%i:AVER:CLE;*WAI" % (channel_number)
            )  # starts new averaging cycle
        else:
            # print('leaving average mode')
            self.port.write(":SENS%i:AVER:COUN 1;*WAI" % (channel_number))  # counts
            self.port.write(":SENS%i:AVER:STAT OFF;*WAI" % (channel_number))  # state

        """ Trigger """
        if self.trigger_state == "Internal":
            # ThE innit immediate command used by sweepMe requires
            # Trigger:Source to be set to Manual
            self.port.write(":TRIG:SOUR MAN")

        elif self.trigger_state == "External":
            self.port.write(":TRIG:SOUR EXT")  # External trigger
            self.port.write(":TRIG:DEL %s" % self.trigger_delay)  # trigger delay

        self.port.write(":INIT:CONT OFF")  # switch off continous measurement

        self.port.write(":TRIG:SCOP ALL")  # ALL is default
        # self.port.write(":TRIG:SCOP CURR") #ALL is default

        """ Calibration """
        channel_number = 1
        self.port.write("CALC:CORR:IND?")
        cal_state = self.port.read()
        # print("Calibration State: ", cal_state)
        # print(type(cal_state))
        # print(self.calibration_file_name)
        if self.calibration_file_name == "None":
            if cal_state[:4] != "NONE":
                # print("'%s'" %(cal_state))
                self.port.write(":SENS%i:CORR:CSET:DEAC" % (channel_number))
                # self.port.write(":SENS%i:CORR:CSET:ACT 'CalSet_898', OFF"%
                #   (channel_number)
            # the user selected None and we can deactivate the current cal set

        else:
            # print("Selected calibration:", self.calibration_file_name)
            # print("Calibration folder:", FoMa.get_path("CALIBRATIONS"))

            # figure out whether the selected calibration has a standard file extension
            #  which means that it is saved on the computer
            file_on_computer = False
            for file_extension in self.calibration_file_extensions:
                if self.calibration_file_name.endswith(file_extension):
                    file_on_computer = True

            # if the user selected a file on the computer, it will be loaded
            if file_on_computer:
                calibration_file_path = (
                    FoMa.get_path("CALIBRATIONS") + os.sep + self.calibration_file_name
                )

                if os.path.exists(calibration_file_path):

                    """
                    http://na.support.keysight.com/vna/help/latest/S5_Output/SaveRecall.htm
                    """

                    # print("MMEM:LOAD:FILE '%s'" % (calibration_file_path))
                    self.port.write(":MMEM:LOAD '%s'" % (calibration_file_path))
                    # self.port.write("MMEM:LOAD:FILE '%s'" % (calibration_file_path))

                else:
                    self.stop_Measurement(
                        """Calibration file '%s' not found in public folder
                         'CalibrationFiles'."""
                        % self.calibration_file_name
                    )
                    return False

            # if the file is not stored on the computer, it is a cal set on the PNA
            else:
                # self.port.write(":MMEM:LOAD:CSTATE '%s'" % (calibration_file_path))
                self.port.write(
                    ":SENS%i:CORR:CSET:ACT '%s', OFF"
                    % (channel_number, self.calibration_file_name)
                )

                # Check if needed
                self.port.write(":SENS%i:CORR:CSET:ACT? NAME" % (channel_number))
                cset_name = self.port.read()
                self.port.write(":SENS%i:CORR:CSET:DESC?" % (channel_number))
                cset_desc = self.port.read()
                self.port.write(":CSET:DATE? %s" % cset_name)
                cset_date = self.port.read()
                self.port.write(":CSET:TIME? %s" % cset_name)
                cset_time = self.port.read()
                hour, min, sec = [int(i) for i in cset_time.split(",")]
                year, month, day = [int(i) for i in cset_date.split(",")]
                text_activate_calset = (
                    "Activated Cal Set: %s with description %s created on %s"
                    % (
                        cset_name,
                        cset_desc,
                        datetime.datetime(year, month, day, hour, min, sec),
                    )
                )
                self.write_Log(text_activate_calset)
                # print(text_activate_calset)

        """ Correction """
        channel_number = 1
        if self.correction == "On":
            self.port.write(":CALC%i:CORR ON" % (channel_number))
            self.port.write(":SENS%i:CORR ON" % (channel_number))
            # print("Correction is ON")
        else:
            self.port.write(":CALC%i:CORR OFF" % (channel_number))
            self.port.write(":SENS%i:CORR OFF" % (channel_number))
            # print("Correction is OFF")

    def unconfigure(self):

        self.port.write("SYST:ERR:COUN?")
        error_count = int(self.port.read())

        for i in range(error_count):
            # report any errors encountered during measurement
            self.port.write("SYST:ERR?")
            answer = self.port.read()
            print("Error %i reported:" % i, answer)

        # abort all ongoing sweeps
        # self.port.write(":ABOR")         # Abort ongoing measurements
        self.port.write(
            ":TRIG:SOUR IMM"
        )  # internal source sends continuous trigger signals
        self.port.write(":INIT:CONT ON")  # switch on continous measurement

        self.port.write(":DISP:ENAB ON")  # Display on

    def trigger_ready(self):
        pass

    def measure(self):

        channel_number = 1

        # Averages
        for j in range(self.number_averages):
            # self.port.write(":INIT%i:IMM;*WAI" % channel_number)
            self.port.write(":INIT%i:IMM;*OPC?" % channel_number)
            self.port.read()

    def request_result(self):
        # check all commands completed, i.e. the measurement has finished
        self.port.write("*OPC?")
        self.port.read()

        # Averages
        self.port.write("STAT:OPER:COND?")
        ans = self.port.read()
        if int(ans) == 1280:
            pass
            # print("Average and Device Status: ok")
        n_traces_av_ok = 0
        for i in range(1, 42):  # 42 registers
            self.port.write("STAT:OPER:AVER%i:COND?" % i)
            ans = self.port.read()
            n_traces_av_ok += bin(int(ans))[2:-1].count("1")
            if bin(int(ans))[-1] == "0":
                break  # bit0 unequal to zero if more registers have to be considered
        # print("Averaging status bits", bin(int(ans)))
        # number of 1s = number of traces (max 14) succesfully avgd, last bit should be 0
        # print("Averaging of %i traces done succesfully" %n_traces_av_ok)

    def read_result(self):

        self.results = []

        """ Frequencies """

        # take frequency list created by software
        # self.results.append(self.frequency_values)

        # retrieve frequency list from device
        self.port.write("CALC:X?")
        answer = (
            self.read_and_parse_data()
        )  # special function to distinguish between different data formats
        self.results.append(answer)

        # indicates whether all commands are completed, i.e. the measurement has finished
        self.port.write("*WAI")

        channel_number = 1
        for i, spar in enumerate(self.Sparameters):

            self.port.write("CALC%i:PAR:SEL 'Meas%s',FAST" % (channel_number, spar))

            self.port.write("CALC%i:DATA? SDATA;*WAI" % (channel_number))
            answer = (
                self.read_and_parse_data()
            )  # special function to distinguish between different data formats

            try:
                data = answer[::2] + 1j * answer[1::2]
                self.results.append(data)

                # self.port.write("*WAI") # indicates whether all commands are completed,
                # si.e. the measurement has finished

            except Exception:
                error()
                print(answer)

    def call(self):
        return self.results

    def finish(self):
        if self.update_display:
            for i, spar in enumerate(self.Sparameters):
                trace_number = i + 1
                self.port.write(
                    "DISP:WIND%i:TRAC%i:SEL" % (self.window_number, trace_number)
                )

            self.port.write("DISP:WIND%i:Y:AUTO" % (self.window_number))

    """ further function as needed by this device class are defined here """

    # used during read_result to read and interpret the returned results
    def read_and_parse_data(self):

        if self.data_format_type == "ASC":
            data_in = self.port.read()
            return np.array(list(map(float, data_in.split(","))))

        elif self.data_format_type == "REAL,32":
            try:
                data_in = self.port.port.read_raw()
            except Exception:
                data_in = (
                    self.port.read_raw()
                )  # fallback if device class is used by external scripts

            return self.binblock_raw(data_in, "f4")

        elif self.data_format_type == "REAL,64":
            try:
                data_in = self.port.port.read_raw()
            except Exception:
                data_in = (
                    self.port.read_raw()
                )  # fallback if device class is used by external scripts

            return self.binblock_raw(data_in, "f8")

        else:
            debug(
                "The data format %s is unknown: Use 'ASC', 'REAL,32', or 'REAL,64'"
                % self.data_format_type
            )
            return False

    def binblock_raw(self, data_in, dtype_in):

        # Grab the beginning section of the data file, which will contain the header.
        Header = str(data_in[0:12])
        # print("Header is " + str(Header))

        # Find the start position of the IEEE header, which starts with a '#'.
        startpos = Header.find("#")
        # print("Start Position reported as " + str(startpos))

        # Check for problem with start position.
        if startpos < 0:
            raise IOError("No start of block found")

        # Find the number that follows '#' symbol.  This is the number of digits in
        # the block length.
        Size_of_Length = int(Header[startpos + 1])
        # print("Size of Length reported as " + str(Size_of_Length))

        # Now we know how many digits are in the size value, get the size of the data file
        Image_Size = int(Header[startpos + 2 : startpos + 2 + Size_of_Length])
        # print("Number of bytes in file are: " + str(Image_Size))

        # Get the length from the header
        offset = startpos + Size_of_Length

        # Extract the data out into a list.
        return np.frombuffer(
            data_in[offset : offset + Image_Size], dtype=np.dtype(dtype_in)
        )
