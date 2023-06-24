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
# Type: SMU
# Device: Agilent 415x

import numpy as np
import time
from EmptyDeviceClass import EmptyDevice
from ErrorMessage import error


class Device(EmptyDevice):

    """
    This driver for an Agilent 415x parameter analyzer uses the FLEX command set. The SCPI commant set is not used.
    The FLEX command has shorter commands and is easier to handle.
    The data is read in ASCII format. Higher speed could be reached by implementing the REAL64 binary data format.

    This driver needs SMU module version 2022-04-04 or higher.
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
                
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data
        
        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {    
                                    "timeout": 10,
                                    # "delay": 0.1,
                                    "GPIB_EOLwrite": "\n",
                                    "GPIB_EOLread": "\n",
                                }
                            
        # self.port_identifications = ['...']
        
        self.channel_numbers = {
                                    "A":  1,  # SMU1
                                    "B":  2,  # SMU2
                                    "C":  3,  # SMU3
                                    "D":  4,  # SMU4
                                    "E":  5,  # SMU5 in 41501A/B
                                    "F":  6,  # SMU6 in 41501A/B
                                    "Q": 21,  # VSU1
                                    "R": 22,  # VSU2
                                    "S": 23,  # VMU1
                                    "T": 24,  # VMU2
                                    "V": 26,  # GNDU in 41501A/B
                                    "W": 27,  # PGU1 in 41501A/B
                                    "X": 28,  # PGU2 in 41501A/B
                                }
                                
        self.channel_numbers_inv = {v: k for k, v in self.channel_numbers.items()}
        
        self.current_ranges = {
                                "Auto":                0,
                                
                                # limited auto
                                "10 pA limited auto":   9,  # only for 4156B
                                "100 pA limited auto": 10,  # only for 4156B 
                                "1 nA limited auto":   11,
                                "10 nA limited auto":  12,
                                "100 nA limited auto": 13, 
                                "1 µA limited auto":   14, 
                                "10 µA limited auto":  15, 
                                "100 µA limited auto": 16,
                                "1 mA limited auto":   17, 
                                "10 mA limited auto":  18, 
                                "100 mA limited auto": 19, 
                                "1 A limited auto":    20,  # only for HPSMU
                                
                                # fixed
                                "10 pA fixed":   -9,  # only for 4156B
                                "100 pA fixed": -10,  # only for 4156B 
                                "1 nA fixed":   -11,
                                "10 nA fixed":  -12,
                                "100 nA fixed": -13, 
                                "1 µA fixed":   -14, 
                                "10 µA fixed":  -15, 
                                "100 µA fixed": -16,
                                "1 mA fixed":   -17, 
                                "10 mA fixed":  -18, 
                                "100 mA fixed": -19, 
                                "1 A fixed":    -20,  # only for HPSMU
                                }
        
        self.voltages_ranges = {
                                "Auto": 0,

                                "0.2 V limited auto": 10,  # only for VMU in differential mode 
                                "2 V limited auto":   11,
                                "20 V limited auto":  12,  # for SMU and VMU in grounded mode
                                "40 V limited auto":  13,  # for SMU
                                "100 V limited auto": 14,  # for SMU 
                                "200 V limited auto": 15,  # only for HPSMU 
                                
                                "0.2 V fixed": -10,  # only for VMU in differential mode 
                                "2 V fixed":   -11,
                                "20 V fixed":  -12,  # for SMU and VMU in grounded mode
                                "40 V fixed":  -13,  # for SMU
                                "100 V fixed": -14,  # for SMU 
                                "200 V fixed": -15,  # only for HPSMU 
                                }

        self.data_status_codes = {
                                1: "A / D converter overflowed.",
                                2: "One or more units are oscillating.",
                                4: "Another unit reached its compliance setting.",
                                8: "This unit reached its compliance setting.",
                                16: "PGU reached its compliance setting.",
                                32: "Not defined.",
                                64: "Invalid data is returned. D is not used.",
                                128: "EOD(End of Data).",
                                }

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        
                        "Channel": ["CH1", "CH2", "CH3", "CH4", "CH5", "CH6"],
                        "RouteOut": ["Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Compliance": 100e-6,
                        "Average": 1,
                        
                        "Range": list(self.current_ranges.keys()),
                        "RangeVoltage": list(self.voltages_ranges.keys()),
                        
                        "ListSweepCheck": True,
                        "ListSweepStart": 0.0,
                        "ListSweepEnd": 1.0,
                        "ListSweepStepPointsType": ["Step width:", "Points (lin.):", "Points (log.):"],
                        "ListSweepStepPointsValue": 0.1,
                        "ListSweepDual": False,
                        "ListSweepHoldtime": 0.1,
                        "ListSweepDelaytime": 0.1,
                        }
                        
        return gui_parameter

    def get_GUIparameter(self, parameter={}):
    
        try:
            self.sweepvalue = parameter["SweepValue"]
        except KeyError:
            # this might be the case when driver is used with pysweepme
            # then, "SweepValue" is not defined during set_GUIparameter
            self.sweepvalue = None
            
        self.device = parameter['Device']
        self.channel = int(parameter['Channel'][2:])
        self.port_string = parameter['Port']
                
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        
        if self.source.startswith("Voltage"):
            self.source = "V"
            self.sense = "I"

        elif self.source.startswith("Current"):
            self.source = "I"
            self.sense = "V"
            
        self.current_range = self.current_ranges[parameter["Range"]]
        self.voltage_range = self.voltages_ranges[parameter["RangeVoltage"]]
        
        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        self.pulse = parameter['CheckPulse']   
        self.pulse_meas_time = parameter['PulseMeasTime']
        
        self.average = int(parameter['Average'])
       
        self.shortname = "Agilent 415x CH%s" % self.channel
        
        self.listsweep_start = float(parameter["ListSweepStart"])
        self.listsweep_end = float(parameter["ListSweepEnd"])
        self.listsweep_steppoints_type = parameter["ListSweepStepPointsType"]
        self.listsweep_steppoints_value = float(parameter["ListSweepStepPointsValue"])
        self.listsweep_dual = float(parameter["ListSweepDual"])
        self.listsweep_hold = float(parameter["ListSweepHoldtime"])
        self.listsweep_delay = float(parameter["ListSweepDelaytime"])

    """ Here, semantic standard functions start """

    def initialize(self):

        # options = self.get_options()
        # print("Options:", options)
    
        self.instrument_id = self.device + "_" + self.port_string

        # we need to initialize the intrument only once for all channels
        if self.instrument_id not in self.device_communication:

            identification = self.get_identification()
            # print("Identification:", identification)

            self.reset()
            
            # self.port.write(":SYST:LANG COMP") put the device into 4145B command syntax
        
            self.set_user_mode()
            
            self.clear_buffer()
            
            self.set_autozero(0)   # Auto-Zero off for faster measurements
            
            # self.port.write("EI0")  # <CR><LF>
            # self.port.write("EI1")  # <CR><LF> with EOI, where EOI means ^<END> (default)

            # For the sweep measurements, primary sweep source data is output with measurement data.
            self.set_data_format(1, 1)

            self.device_communication[self.instrument_id] = {}
            
            if "Channels" not in self.device_communication[self.instrument_id]:
                self.device_communication[self.instrument_id]["Channels"] = []

            if "Identification" not in self.device_communication[self.instrument_id]:
                self.device_communication[self.instrument_id]["Identification"] = identification

        # check if selected current range can be used - will result in program freeze if not compatible
        if ("4156B" not in self.device_communication[self.instrument_id]["Identification"]) and (
                self.current_range in [9, 10]):
            raise ValueError("Selected current range is not available for your model of the parameter analyzer."
                             "Only model 4156B can use the lowest current ranges.")

        if self.sweepvalue == "List sweep":
            if self.listsweep_steppoints_type.startswith("Step width"):            
                if self.listsweep_steppoints_value == 0.0:
                    if self.listsweep_end != self.listsweep_start:
                        raise ValueError("Start and end value must be equal if step width is zero.")
 
    def deinitialize(self):
        pass
 
    def configure(self):
    
        if self.speed == "Fast": 
            self.nplc = 1  # 1 Short (0.1 PLC) preconfigured selection Fast
        elif self.speed == "Medium": 
            self.nplc = 2  # 2 Medium (1.0 PLC) preconfigured selection Normal
        elif self.speed == "Slow": 
            self.nplc = 3  # 3 Long (10 PLC) preconfigured selection Quiet
        
        self.set_nplc(self.nplc)

        # integration time is hard coded here
        # only nplc is changable by the user
        # setting for nplc Medium = 2 is not allowed by instrument
        self.set_integration_time(1, 640e-6)
        self.set_integration_time(3, 320e-3)

        self.set_average(self.average)

        # declaration of variables
        listsweepmode = None
        listsweep_points = 0

        if self.sweepvalue == "List sweep":
        
            if self.listsweep_steppoints_type.startswith("Step width"):
                listsweepmode = 1

                if self.listsweep_steppoints_value == 0.0:
                    if self.listsweep_end == self.listsweep_start:           
                        listsweep_points = 1
                    else:
                        raise ValueError("Start and end value must be equal if step width is zero.")     
                else:
                    listsweep_points = \
                        abs(self.listsweep_end - self.listsweep_start) / abs(self.listsweep_steppoints_value) + 1

            elif self.listsweep_steppoints_type.startswith("Points (lin.)"):
                listsweepmode = 1
                listsweep_points = self.listsweep_steppoints_value

            elif self.listsweep_steppoints_type.startswith("Points (log.)"):
                listsweepmode = 2
                listsweep_points = self.listsweep_steppoints_value

            if self.listsweep_dual:
                # forward and backward sweep is mode 3 for linear and 4 for logarithmic
                # thus 2 larger than the modes without dual sweep/double sweep
                listsweepmode += 2

            # Creating list of set values as they are not re-measured in List sweep mode
            if self.source == "V":
                self.set_sweep(self.source, self.channel, listsweepmode, self.voltage_range,
                               self.listsweep_start, self.listsweep_end, listsweep_points, self.protection)
                self.v = np.linspace(self.listsweep_start, self.listsweep_end, listsweep_points) 
            elif self.source == "I":
                self.set_sweep(self.source, self.channel, listsweepmode, self.current_range,
                               self.listsweep_start, self.listsweep_end, listsweep_points, self.protection)
                self.i = np.linspace(self.listsweep_start, self.listsweep_end, listsweep_points) 

            self.device_communication[self.instrument_id]["Data"] = {}  # empty dictionary to store data
                      
        self.device_communication[self.instrument_id]["Channels"].append(self.channel)
                    
    def unconfigure(self):

        if self.sweepvalue == "List sweep":
            if "Data" in self.device_communication[self.instrument_id]:
                del self.device_communication[self.instrument_id]["Data"]
            
            channels = self.device_communication[self.instrument_id]["Channels"]            
            self.set_measurement_mode(1, *channels)  # we change all channels back to spot measurement
            self.device_communication[self.instrument_id]["Channels"] = []

    def poweron(self):
    
        # this line checks whether any driver instance uses List sweep
        # this done in poweron to make sure all driver instances have finished 'configure' function
        self.is_list_sweep_activated = "Data" in self.device_communication[self.instrument_id]
        
        if self.is_list_sweep_activated:
            self.set_range_voltage(self.channel, self.voltage_range)
            self.set_range_current(self.channel, self.current_range)
        
        if self.sweepvalue == "List sweep":
            channels = self.device_communication[self.instrument_id]["Channels"]
            self.set_measurement_mode(2, *channels)  # we enable all channels to participate at the measurement
        
        self.enable_channel(self.channel)
    
    def poweroff(self):
        self.disable_channel(self.channel)
              
    def apply(self):

        # List sweeps are set in configure, all other source have to set their constant voltage here
        if self.sweepvalue != "List sweep":
            if self.source == "V":
                self.set_source_value(self.source, self.channel, self.voltage_range, self.value, self.protection)
            else:
                self.set_source_value(self.source, self.channel, self.current_range, self.value, self.protection)

        # the code below could be used at some point to add synchronous sweeps,
        # e.g. if multiple sources perform a List sweep
        # if self.source == "V":
        #     self.set_sweep_synchronous(self.source, self.channel, self.voltage_range,
        #                                self.value, self.value, self.protection)
        # else:
        #     self.set_sweep_synchronous(self.source, self.channel, self.current_range,
        #                                self.value, self.value, self.protection)

    def measure(self):
   
        if not self.is_list_sweep_activated:
            self.measure_current(self.channel, self.current_range)
            self.measure_voltage(self.channel, self.voltage_range)
        else:
            # only the module in List sweep mode executes the measurement
            if self.sweepvalue == "List sweep":
                self.execute_measurement()
                # self.port.write("*OPC?")  # old solution with using 'operation complete' to check end of measurement

    def request_result(self):
    
        # only the module in List sweep mode must check whether measurement execution has finished
        if self.sweepvalue == "List sweep":
            # self.port.read()  # reading the answer of the *OPC? query in 'request_result', not used anymore

            status_timeout = 120  # two minutes for taking a list sweep should be enough
            starttime = time.perf_counter()
            while time.perf_counter() - starttime < status_timeout:
                self.port.write("*STB?")
                stb = self.port.read()
                # print("Status byte:", stb)  # stb should be an integer
                if int(stb) & 2 != 2:  # if second bit 2**1 is in status byte, the logic sum will be 2
                    break
                time.sleep(0.1)
       
    def read_result(self):
    
        if not self.is_list_sweep_activated:
            self.i = float(self.read_measurement_data()[5:])
            self.v = float(self.read_measurement_data()[5:])
        else:
        
            if self.sweepvalue == "List sweep":
                
                # If there are some errors until now we will read them out
                e = self.read_errors()
                if "No error" not in e:
                    print("Error message Agilent 415x:", e)
        
                self.device_communication[self.instrument_id]["Data"] = {}

                error_messages = set()

                while True:
                
                    data_number = self.get_number_data()
                    print("Number of points in buffer:", data_number)
                    
                    if int(data_number) > 0:
                    
                        reply = self.read_measurement_data()
                        # print("RMD? response:", reply)
                        
                        for data_point in reply.split(","):

                            status = data_point[:3]  #
                            # chan_str = data_point[3]  # channel string
                            # data_type = data_point[4]
                            data_id = data_point[3:5]  # e.g. "BI" with B for channel 2, and I for currents,
                            data = float(data_point[5:])

                            if status.isdigit():
                                status = int(status)

                                if status != 0 and status != 128:  # 0 = ok, 128 = end of data
                                    for i in self.data_status_codes:
                                        if i & status == i:  # bitwise AND operator & is used
                                            error_messages.add(self.data_status_codes[i])

                            if data > 1e37:
                                data = float('nan')  # a number larger than 1e37 indicates a false value that would 

                            # We save all values in a separate list per identifier
                            if data_id not in self.device_communication[self.instrument_id]["Data"]:
                                # create a new empty list for each data_id
                                self.device_communication[self.instrument_id]["Data"][data_id] = []
                            # append data to list
                            self.device_communication[self.instrument_id]["Data"][data_id].append(data)

                    else:
                        break

                if len(error_messages) > 0:
                    print("The following error messages are found after staircase sweep:")
                    for msg in error_messages:
                        print(msg)
                    print()
                          
        # If there are some errors until now we will read them out
        e = self.read_errors()
        if "No error" not in e:
            print("Error message Agilent 415x:", e)
            
    def process_data(self):
    
        if not self.is_list_sweep_activated:
            
            # check whether values indicate an improper value
            if self.v > 1e37:
                self.v = float('nan')
            if self.i > 1e37:
                self.i = float('nan')
            
        else:
                   
            if self.source == "V":
                data_id = self.channel_numbers_inv[self.channel] + self.sense
                self.i = self.device_communication[self.instrument_id]["Data"][data_id]
                
                if self.sweepvalue == "List sweep":
                    data_id = self.channel_numbers_inv[self.channel] + self.source.lower()
                    try:
                        self.v = self.device_communication[self.instrument_id]["Data"][data_id]
                    except KeyError:
                        error()
                else:
                    self.v = float(self.value)*np.ones(len(self.i))  # sweep values of the synchronous sources

            elif self.source == "I":
                data_id = self.channel_numbers_inv[self.channel] + self.sense
                self.v = self.device_communication[self.instrument_id]["Data"][data_id]
                
                if self.sweepvalue == "List sweep":
                    data_id = self.channel_numbers_inv[self.channel] + self.source.lower()
                    try:
                        self.i = self.device_communication[self.instrument_id]["Data"][data_id]
                    except KeyError:
                        error()
                else:
                    self.i = float(self.value)*np.ones(len(self.v))  # sweep values of the synchronous sources
                           
    def call(self):
    
        return [self.v, self.i]

    """ Here, convenience functions start that wrap the commands into python functions """
          
    def get_identification(self):
        self.port.write("*IDN?")
        return self.port.read()
        
    def get_options(self):
        self.port.write("*OPT?")
        return self.port.read()
           
    def reset(self):
        self.port.write("*RST")
          
    def set_user_mode(self):
        self.port.write("US")
        
    def clear_buffer(self):
        self.port.write("BC")
        
    def set_autozero(self, mode):
        self.port.write("AZ %i" % int(mode))   # Auto-Zero 
        
    def set_nplc(self, nplc):
        self.port.write("SLI %i" % int(nplc))
        
    def set_integration_time(self, integration_type, integration_time):
    
        """
        Args:
            integration_type: 1 (=SHORT) or 3 (=LONG), Not allowed is 2 (=Medium), see programming manual
            integration_time: time in seconds
                80E-6 to 10.16E-3 for SHORT
                16.7E-3 to 2 for LONG
        """
        
        self.port.write("SIT %i,%1.3e" % (int(integration_type), float(integration_time)))
        
    def set_average(self, count):
        self.port.write("AV %i" % int(count))
      
    def enable_channel(self, channel):
    
        self.port.write("CN %i" % int(channel))  # switches the channel on
        
    def disable_channel(self, channel):
    
        self.port.write("CL %i" % int(channel))  # switches the channel off
        
    def get_current(self, channel, range):
        
        self.port.write("TI? %i,%i" % (int(channel), int(range)))
        answer = self.port.read()
        # print(answer)
        return float(answer[5:])
        
    def get_voltage(self, channel, range):    
        
        self.port.write("TV? %i,%i" % (int(channel), int(range)))   
        answer = self.port.read()    
        # print(answer)
        return float(answer[5:])   
          
    def measure_current(self, channel, range):
        
        self.port.write("TI %i,%i" % (int(channel), int(range)))

    def measure_voltage(self, channel, range):    
        
        self.port.write("TV %i,%i" % (int(channel), int(range)))   

    def set_current(self, channel, range, value, compliance):
            
        self.set_source_value("I", channel, range, value, compliance)
        
    def set_voltage(self, channel, range, value, compliance):
        
        self.set_source_value("V", channel, range, value, compliance)
        
    def set_source_value(self, source, channel, range, value, compliance):
        
        self.port.write("D%s %i,%i,%1.4f,%1.4f" %
                        (str(source), int(channel), int(range), float(value), float(compliance)))

    def read_measurement_data(self, count=0):
        """ reads data from the output buffer
        
        Arguments:
            count (int): optional, default = 0 (read all data)
        """

        """
        The data format is: AAABCDDDDDDDDDDDDD
        A = Status code
            1 A/D converter overflowed.
            2 One or more units are oscillating.
            4 Another unit reached its compliance setting.
            8 This unit reached its compliance setting.
            16 PGU reached its compliance setting.
            32 Not defined.
            64 Invalid data is returned. D is not used.
            128 EOD (End of Data).
        B = Channel
            A Channel number 1, SMU1.
            B Channel number 2, SMU2.
            C Channel number 3, SMU3.
            D Channel number 4, SMU4.
            E Channel number 5, SMU5 (in 41501A/B).
            F Channel number 6, SMU6 (in 41501A/B).
            Q Channel number 21, VSU1.
            R Channel number 22, VSU2.
            S Channel number 23, VMU1.
            T Channel number 24, VMU2.
            V Channel number 26, GNDU (in 41501A/B).
            W Channel number 27, PGU1 (in 41501A/B).
            X Channel number 28, PGU2 (in 41501A/B).
            Z Returned D value is not measurement data.
        C = Data type
            V Voltage measurement data.
            v Voltage source setup data.
            I Current measurement data.
            i Current source setup data.
            P Sampling point index.
            S Stress status information.
            Z Invalid data is returned.
            z Invalid data is returned.
        D = Data
        """

        count = int(count)
        
        if count == 0:
            self.port.write("RMD?")
        elif count > 0:
            self.port.write("RMD? %i" % count)
        else:
            raise ValueError("Argument 'count' must be positve integer, not %i." % count)
            
        answer = self.port.read()
        # print(answer)
        return answer
        
    def execute_measurement(self):
    
        self.port.write("XE")

    def learn_parameter(self, id):
    
        self.port.write("*LRN? %i" % int(id))
        answer = self.port.read()
        return answer
        
    def set_sweep_abort_condition(self, mode):
    
        """
        1 Disables the automatic sweep abort function.
        2 One of following occurs:
            - Compliance on the measurement unit.
            - Compliance on the non-measurement unit.
            - Overflow on the AD converter.
            - Oscillation on any unit.
        4 Compliance on the non-measurement unit.
        8 Compliance on the measurement unit.
        16 Overflow on the AD converter.
        32 Oscillation on any unit.
        """
    
        self.port.write("WM %i" % int(mode))

    def set_sweep_timing(self, hold, delay):
        
        self.port.write("WT %1.3f, %1.3f" % (float(hold), float(delay)))
        
    def set_sweep_voltage(self, channel, listsweepmode, range, start, stop, points, compliance):
        return self.set_sweep("V", channel, listsweepmode, range, start, stop, points, compliance)
    
    def set_sweep_current(self, channel, listsweepmode, range, start, stop, points, compliance):
        return self.set_sweep("I", channel, listsweepmode, range, start, stop, points, compliance)
        
    def set_sweep(self, source, channel, listsweepmode, range, start, stop, points, compliance):
        """
        sets staircase sweep for voltage or current
        
        Arguments Pcomp and Rmode are not set and use default values
        
        Arguments:
            source (str): "V" or "I" (for voltage or current)
            channel (int): channel number
            listsweepmode (int): 
                1 -> Linear sweep (single stair)
                2 -> Logarithmic sweep (single stair)
                3 -> Linear sweep (double stair)
                4 -> Log sweep (double stair)
            range (int): Source ranging type
            start (float): Start value in V or A
            stop (float): End value in V or A
            points (int): Number of steps
            compliance (float): optional, either in A or V.
        """
        
        # TODO: unclear whether points is number of points or number of steps
        
        points = int(points)
        
        if points < 1:
            raise ValueError("Number of steps must be larger than 1.")
        elif points > 1001:
            raise ValueError("Number of steps must be smaller than 1002.")
             
        source = str(source)
        ch = int(channel)
        mode = int(listsweepmode)
        range = int(range)
        start = float(start)
        stop = float(stop)
        step = int(points)
        icomp = float(compliance)
        # [WS] ch,mode,range,start,stop,step [,Icomp[,Pcomp[,Rmode]]]
        self.port.write("W%s %i,%i,%i, %1.3f,%1.3f,%i, %1.3f" % (source, ch, mode, range, start, stop, step, icomp))

    def set_sweep_synchronous_voltage(self, channel, range, start, stop, compliance):
        
        return self.set_sweep_synchronous("V", channel, range, start, stop, compliance)
        
    def set_sweep_synchronous_current(self, channel, range, start, stop, compliance):
        
        return self.set_sweep_synchronous("I", channel, range, start, stop, compliance)
        
    def set_sweep_synchronous(self, source, channel, range, start, stop, compliance):
        """
        Sets synchronous sweep source
        source: "V" or "I" (for voltage or current)
        """
        
        source = str(source)    
        ch = int(channel)
        range = int(range)
        start = float(start)
        stop = float(stop)
        icomp = float(compliance)
                     
        # [WSV] ch,range,start,stop[,Icomp[,Pcomp[,Rmode]]]
        self.port.write("WS%s %i,%i, %1.3f,%1.3f, %1.3f" % (source, ch, range, start, stop, icomp))
        
    def set_measurement_mode(self, mode, *channels):
        """
        mode Description Related Source Setup Command
        1 Spot measurement DI, DV
        2 Staircase sweep measurement WI, WV, WT, WM, WSI, WSV
        3 1ch pulsed spot measurement PI, PV, PT
        4 Pulsed sweep measurement PWI, PWV, PT, WM, WSI, WSV
        5 Staircase sweep with pulsed bias measurement WI, WV, WT, WM, PI, PV, PT
        6 to 9 Not defined.
        10 Sampling measurement MI, MV, MP, MT, MSC, MCC
        11 Stress force POR, STI, STV, STP, STT, STM, STC
        """
        
        cmd = "MM %i," % int(mode) + ",".join(["%i" % int(ch) for ch in channels])
        
        self.port.write(cmd)
        
    def set_smu_measurement_mode(self, channel, mode):
    
        """
        mode Description
        0 Compliance side measurement (initial setting). If SMU is
        in the voltage source mode, SMU does current
        measurement. If SMU is in the current source mode, SMU
        does voltage measurement.
        
        1 Current measurement. SMU does current measurement,
        regardless of the SMU output source mode.
        
        2 Voltage measurement. SMU does voltage measurement,
        regardless of the SMU output source mode.
        
        3 Force side measurement. If SMU is in the voltage source
        mode, SMU does voltage measurement. If SMU is in the
        current source mode, SMU does current measurement.
        """
        
        self.port.write("CMM %i,%i" % (int(channel), int(mode)))

    def set_range_voltage(self, channel, range):
        """
        
        """
        
        self.set_range("V", channel, range)
        
    def set_range_current(self, channel, range):
        """
        
        """
        
        self.set_range("I", channel, range)
     
    def set_range(self, source, channel, range):
        """
        source: V or I (for voltage or current)

        """
        
        self.port.write("R%s %i,%i" % (str(source), int(channel), int(range)))

    def read_errors(self):
        
        self.port.write(":SYST:ERR?")
        return self.port.read()
        
    def get_number_data(self):
    
        self.port.write("NUB?")
        return int(self.port.read())

    def set_data_format(self, form, mode):
    
        """
        set data output format
        
        Arguments:
            form (int):
                1 ASCII data format with header
                2 ASCII data format without header
                3 Binary data format
                4 Binary data format <^EOI>
                5 ASCII data format with header
                
            mode:
                0 -> For the sweep measurements, sweep source data is not output. 
                For the sampling measurements, sampling point index is not output.
                1 -> For the sweep measurements, primary sweep source data is output with measurement data.
                For the sampling measurements, sampling point index is
                output with measurement data.
                2 -> For the sweep measurements, secondary sweep source
                data is output with measurement data. If WSI/WSV
                command was not entered properly, the invalid source
                data will be returned. Ignore the returned value.
                For the sampling data, sampling point index is output
                with measurement data.

        """
        
        self.port.write("FMT %i,%i" % (int(form), int(mode)))


"""
"""
        
        
