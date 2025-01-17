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
# * Module: Logger
# * Instrument: Bronkhorst Propar


# must be done before 'import propar' to make sure libs folder is added to PATH
import FolderManager as FoMa
FoMa.addFolderToPATH()

import propar
import os

from pysweepme.ErrorMessage import error, debug

from pyweepme.EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    description =   """
                    <p><strong>Bronkhorst Propar<br /><br /></strong></p>
                    <p>This device class can be used to connect to different devices such as&nbsp;EL-Flow, ES-Flow, (mini) CORI-FLOW, IQ+FLOW, and others), Pressure Meters and Controllers (EL-PRESS).</p>
                    <p>&nbsp;</p>
                    <p><strong>Handling:</strong></p>
                    <ul>
                    <li>Flow is a value 0 and 100 with unit %.</li>
                    <li>Choose between RS-232 or FLOW-BUS. In case of FLOW-BUS that is based on RS-485, please select the corresponding address your controller unit has.</li>
                    <li>The baudrate is only used for communication via RS-232. Otherwise, the default value is used.</li>
                    </ul>
                    <p><strong>Custom unit:</strong></p>
                    <ul>
                    <li>Calculating a custom unit can be activated by entering a unit, e.g. 'l/min'.</li>
                    <li>If a custom unit is given, please enter a float-type conversion factor.</li>
                    <li>The conversion factor has the unit 'custom unit per %'.</li>
                    <li>If a custom unit is used, the sweep mode "Flow in custom unit" can be used.&nbsp;</li>
                    </ul>
                    <p><strong>Information:</strong></p>
                    <ul>
                    <li>Not all devices are tested yet and returned variables might have to be adapted later to certain types of controllers.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Acknowledgement:</strong></p>
                    <p>This device class is based on the python package bronkhorst-propar<br /><a href="https://pypi.org/project/bronkhorst-propar/"> https://pypi.org/project/bronkhorst-propar/</a><br />that has been released under MIT license by Bronkhorst.</p>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Bronkhorst" # short name will be shown in the sequencer       
        
        #self.port_manager = True  # We don't need it because propar package handles the communication
           
        self.port_types = ["COM"]  # We just this here, to find ports via SweepMe! port manager, but we do not use the port manager to do the communication
            

    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        
        GUIparameter = {
                        "SweepMode": ["Flow in %", "Flow in custom unit"],  # 'None' ??
                                  
                        # "Model": ["EL-FLOW"], # can be later used to make a difference between different models
                        "Address" : ["RS232"] + ["FLOW-BUS address %i" % (i+1) for i in range(120)],
                        "Baudrate": ["38400", "115200"],

                        "": None,
                        
                        "Custom unit (c.u.)": "",
                        "Flow in c.u. at 100%": "",
                        }

        
        return GUIparameter
     
        
    def get_GUIparameter(self, parameter):

        self.sweepmode = parameter["SweepMode"]
        self.port_string = parameter["Port"]
        self.address = parameter["Address"]
        self.baudrate = parameter["Baudrate"]
        
        self.use_custom_unit = parameter["Custom unit (c.u.)"] != ""
        self.custom_unit = parameter["Custom unit (c.u.)"]
        self.conversion_factor = parameter["Flow in c.u. at 100%"]

        if self.use_custom_unit:
        
            self.variables = ["Flow", "Flow", "Flow, set", "Flow, set", "Temperature", "Density"] 
            self.units = [self.custom_unit, "%", self.custom_unit, "%", "°C", "g/l"] 
            self.plottype = [True, True, True, True, True, True]
            self.savetype = [True, True, True, True, True, True] 
        
        else:
            self.variables = ["Flow", "Flow, set", "Temperature", "Density"]
            self.units = ["%", "%", "°C", "g/l"] 
            self.plottype = [True, True, True, True] 
            self.savetype = [True, True, True, True]

    """ here, semantic standard function start """
            
    def connect(self):
                    
        # Please find a full list of all parameters at the bottom of this file. #
        
        self.database = propar.database()
        # print("Database:", self.database)
        
        self.create_friendly_parameter_list()
               
        if self.address == "RS232":
            self.flow_controller = propar.instrument(self.port_string, baudrate = int(self.baudrate))
            
        elif self.address.startswith("FLOW-BUS"):
            address_number = int(self.address.split()[-1])
            self.flow_controller = propar.instrument(self.port_string, address = address_number)
        
        ## Can be used to find nodes
        # self.flow_controller.get_nodes()
            
        self.flow_controller.master.start()
        
    def disconnect(self):
        self.flow_controller.master.stop()

    def initialize(self):
   
        identification = self.get_identification()
        # print("Identification:", identification)
        
        if self.sweepmode == "Flow in custom unit" and not self.use_custom_unit:
            self.stop_Measurement("Please use custom unit to use sweep mode 'Flow in custom unit'")
            return False
        
    def configure(self):
    
        if self.use_custom_unit:
            try:
                self.conversion_factor = float(self.conversion_factor)/100.0  # we divide by 100.0 to have the conversion factor in c.u per %, so that it can be multiplied directly with any flow value in %
            except:
                self.stop_Measurement("Cannot convert conversion factor to float.")
                return False

            if self.conversion_factor == 0.0:
                self.stop_Measurement("Conversion factor cannot be zero.")
                return False

    def apply(self):
    
        self.value = float(self.value)
        
        if self.sweepmode == "Flow in %":
            self.set_flow_rate(self.value)
        
        elif self.sweepmode == "Flow in custom unit":            
            self.set_flow_rate(self.value/self.conversion_factor)

    def reach(self):
        pass
        # we might have to add some code here to ensure the new flow value has been reached

    def request_result(self):
        self.flow_rate = self.get_measured_flow_rate()
        self.temperature = self.get_temperature()
        self.density = self.get_density()
        
        # Comment: Pressure is not read out yet, as not all controllers provide a pressure sensor
        # It means that one needs to check whether the controller has a pressure sensor first or
        # whether the value is returned with status Ok

    def call(self):
    
        if self.use_custom_unit:
            if self.sweepmode == "Flow in %":
                return self.flow_rate*self.conversion_factor, self.flow_rate, self.value*self.conversion_factor, self.value, self.temperature, self.density
            elif self.sweepmode == "Flow in custom unit": 
                return self.flow_rate*self.conversion_factor, self.flow_rate, self.value, self.value/self.conversion_factor, self.temperature, self.density
        else:
            return self.flow_rate, self.value, self.temperature, self.density

    """ convenience functions """

        # get all parameters
        # print(self.database.get_all_parameters())
                
        # returns a dictionary with dde number, process number, parameter number, parameter type, and parameter name
        # print(self.database.get_parameter(8))#

    def create_friendly_parameter_list(self):
        """ we create it every time as it does not take much time """
        
        self.parameters_dict = {}
        for index in range(1, 379, 1):
            try:
                params = self.database.get_parameter(index)
                self.parameters_dict[params["parm_name"]] = index
            except (IndexError, KeyError):
                # We skip errors related to non-existing items
                # IndexError is needed for SweepMe! 1.5.5/Python 3.6
                # KeyError is needed for SweepMe! 1.5.6/Python 3.9
                pass
        
        return self.parameters_dict
        
    def get_index_from_friendly_name(self, name):
        
        if name in self.parameters_dict:
            return self.parameters_dict[name]
        else:
            raise Exception("Bronkhorst: Parameter name '%s' unknown. Please check use of capital letters." % name)
    
    def get_parameter(self, *args):
        """ convenience function to get the value of a parameter indicated by the dde_nr index """
    
        # later on multiple indices can be handed over and returned
        
        if isinstance(args[0], (int, float)):
            index = int(args[0])
            params = self.database.get_parameter(index)
        elif isinstance(args[0], str):
            index = self.get_index_from_friendly_name(args[0])
            params = self.database.get_parameter(index)
        else:
            raise Exception("Bronkhorst: Data type not defined in get_parameter. Please use int, float for dde_nr index or string of a variable name to identify a parameter.")
                
        values = self.flow_controller.read_parameters([params])
        
        return values[0]["data"]
        
    def set_parameter(self, index, value):
        """ convenience function to set the value of a parameter indicated by the dde_nr index """
            
        if isinstance(index, (int, float)):
            index = int(index)
            params = self.database.get_parameter(index)
        elif isinstance(index, str):
            params = self.database.get_parameters_like('value')
        else:
            raise Exception("Bronkhorst: Data type not defined in set_parameter. Please use int, float for dde_nr index or string of a variable name to identify a parameter.")

        params.update({"data": value})
        values = self.flow_controller.write_parameters([params])

    """ setter/getter functions start here """
    
    def get_identification(self):
        """ returns the identification number including the serial number as string """

        return self.get_parameter("Identification string")

    def get_flow_rate(self):
        """ get the setpoint flowrate in % """
        
        value = self.get_parameter(9)
        
        value = float(value)/32000 * 100.0  # conversion to %
        
        return value

    def set_flow_rate(self, value):
        """ set the setpoint flow rate in % """
        
        value = int(float(value)/100.0*32000)
        
        self.set_parameter(9, value)
        # self.flow_controller.setpoint = value
        
    def get_measured_flow_rate(self):
        """ get the measured flow rate in % """
        
        value = self.get_parameter(8)
        
        value = float(value)/32000 * 100.0  # conversion to %
        
        return value
        
    def get_temperature(self):
        """ returns the temperature of the sensor in °C """

        return self.get_parameter(142)
        
    def get_density(self):
        
        """ returns the density in g/cm^3? """

        return self.get_parameter(170)
        
    def set_density(self, value):
        
        """ sets the density in g/cm^3? """

        return self.get_parameter(170, value)
        
        
"""
{'dde_nr': 1, 'proc_nr': 0, 'parm_nr': 0, 'parm_type': 96, 'parm_name': 'Identification string'}
{'dde_nr': 2, 'proc_nr': 0, 'parm_nr': 1, 'parm_type': 0, 'parm_name': 'Primary node address'}
{'dde_nr': 3, 'proc_nr': 0, 'parm_nr': 2, 'parm_type': 0, 'parm_name': 'Secondary node address'}
{'dde_nr': 4, 'proc_nr': 0, 'parm_nr': 3, 'parm_type': 0, 'parm_name': 'Next node address'}
{'dde_nr': 5, 'proc_nr': 0, 'parm_nr': 4, 'parm_type': 0, 'parm_name': 'Last node address'}
{'dde_nr': 6, 'proc_nr': 0, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Arbitrage'}
{'dde_nr': 7, 'proc_nr': 0, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'Initreset'}
{'dde_nr': 8, 'proc_nr': 1, 'parm_nr': 0, 'parm_type': 34, 'parm_name': 'Measure'}
{'dde_nr': 9, 'proc_nr': 1, 'parm_nr': 1, 'parm_type': 32, 'parm_name': 'Setpoint'}
{'dde_nr': 10, 'proc_nr': 1, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'Setpoint slope'}
{'dde_nr': 11, 'proc_nr': 1, 'parm_nr': 3, 'parm_type': 34, 'parm_name': 'Analog input'}
{'dde_nr': 12, 'proc_nr': 1, 'parm_nr': 4, 'parm_type': 0, 'parm_name': 'Control mode'}
{'dde_nr': 13, 'proc_nr': 1, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'Polynomial constant A'}
{'dde_nr': 14, 'proc_nr': 1, 'parm_nr': 6, 'parm_type': 65, 'parm_name': 'Polynomial constant B'}
{'dde_nr': 15, 'proc_nr': 1, 'parm_nr': 7, 'parm_type': 65, 'parm_name': 'Polynomial constant C'}
{'dde_nr': 16, 'proc_nr': 1, 'parm_nr': 8, 'parm_type': 65, 'parm_name': 'Polynomial constant D'}
{'dde_nr': 17, 'proc_nr': 1, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Polynomial constant E'}
{'dde_nr': 18, 'proc_nr': 1, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Polynomial constant F'}
{'dde_nr': 19, 'proc_nr': 1, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Polynomial constant G'}
{'dde_nr': 20, 'proc_nr': 1, 'parm_nr': 12, 'parm_type': 65, 'parm_name': 'Polynomial constant H'}
{'dde_nr': 21, 'proc_nr': 1, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Capacity 100%'}
{'dde_nr': 22, 'proc_nr': 1, 'parm_nr': 14, 'parm_type': 0, 'parm_name': 'Sensor type'}
{'dde_nr': 23, 'proc_nr': 1, 'parm_nr': 15, 'parm_type': 0, 'parm_name': 'Capacity unit index'}
{'dde_nr': 24, 'proc_nr': 1, 'parm_nr': 16, 'parm_type': 0, 'parm_name': 'Fluidset index'}
{'dde_nr': 25, 'proc_nr': 1, 'parm_nr': 17, 'parm_type': 96, 'parm_name': 'Fluid name'}
{'dde_nr': 26, 'proc_nr': 1, 'parm_nr': 18, 'parm_type': 0, 'parm_name': 'Claim node'}
{'dde_nr': 27, 'proc_nr': 1, 'parm_nr': 19, 'parm_type': 0, 'parm_name': 'Modify'}
{'dde_nr': 28, 'proc_nr': 1, 'parm_nr': 20, 'parm_type': 0, 'parm_name': 'Alarm info'}
{'dde_nr': 29, 'proc_nr': 0, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Channel amount'}
{'dde_nr': 30, 'proc_nr': 0, 'parm_nr': 13, 'parm_type': 0, 'parm_name': 'First channel'}
{'dde_nr': 31, 'proc_nr': 0, 'parm_nr': 14, 'parm_type': 0, 'parm_name': 'Last channel'}
{'dde_nr': 32, 'proc_nr': 9, 'parm_nr': 1, 'parm_type': 0, 'parm_name': '<hostcontrl>'}
{'dde_nr': 33, 'proc_nr': 10, 'parm_nr': 0, 'parm_type': 96, 'parm_name': 'Alarm message unit type'}
{'dde_nr': 34, 'proc_nr': 10, 'parm_nr': 1, 'parm_type': 96, 'parm_name': 'Alarm message number'}
{'dde_nr': 35, 'proc_nr': 10, 'parm_nr': 2, 'parm_type': 96, 'parm_name': 'Relay status'}
{'dde_nr': 36, 'proc_nr': 1, 'parm_nr': 0, 'parm_type': 65, 'parm_name': 'Actual counter value'}
{'dde_nr': 37, 'proc_nr': 1, 'parm_nr': 1, 'parm_type': 96, 'parm_name': 'Signal input selection'}
{'dde_nr': 38, 'proc_nr': 1, 'parm_nr': 2, 'parm_type': 96, 'parm_name': 'Reset input selection'}
{'dde_nr': 39, 'proc_nr': 1, 'parm_nr': 3, 'parm_type': 65, 'parm_name': '<limit>'}
{'dde_nr': 40, 'proc_nr': 1, 'parm_nr': 4, 'parm_type': 96, 'parm_name': 'Delay time'}
{'dde_nr': 41, 'proc_nr': 1, 'parm_nr': 5, 'parm_type': 96, 'parm_name': 'Duration time'}
{'dde_nr': 42, 'proc_nr': 1, 'parm_nr': 6, 'parm_type': 96, 'parm_name': 'Valve output setting'}
{'dde_nr': 43, 'proc_nr': 1, 'parm_nr': 7, 'parm_type': 96, 'parm_name': 'Relay output setting'}
{'dde_nr': 44, 'proc_nr': 1, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Operation mode T/A'}
{'dde_nr': 45, 'proc_nr': 1, 'parm_nr': 9, 'parm_type': 96, 'parm_name': 'Readout unit'}
{'dde_nr': 46, 'proc_nr': 1, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Readout factor'}
{'dde_nr': 47, 'proc_nr': 1, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Reset unit'}
{'dde_nr': 48, 'proc_nr': 1, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Valve differentiator down'}
{'dde_nr': 49, 'proc_nr': 1, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Valve differentiator up'}
{'dde_nr': 50, 'proc_nr': 1, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Sensor differentiator down'}
{'dde_nr': 51, 'proc_nr': 1, 'parm_nr': 12, 'parm_type': 65, 'parm_name': 'Sensor differentiator up'}
{'dde_nr': 52, 'proc_nr': 114, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Cycle time'}
{'dde_nr': 53, 'proc_nr': 115, 'parm_nr': 3, 'parm_type': 0, 'parm_name': 'Analog mode'}
{'dde_nr': 54, 'proc_nr': 116, 'parm_nr': 6, 'parm_type': 32, 'parm_name': 'Reference voltage'}
{'dde_nr': 55, 'proc_nr': 114, 'parm_nr': 1, 'parm_type': 64, 'parm_name': 'Valve output'}
{'dde_nr': 56, 'proc_nr': 117, 'parm_nr': 1, 'parm_type': 65, 'parm_name': 'Dynamic display factor'}
{'dde_nr': 57, 'proc_nr': 117, 'parm_nr': 2, 'parm_type': 65, 'parm_name': 'Static display factor'}
{'dde_nr': 58, 'proc_nr': 115, 'parm_nr': 1, 'parm_type': 0, 'parm_name': 'Calibration mode'}
{'dde_nr': 59, 'proc_nr': 116, 'parm_nr': 7, 'parm_type': 33, 'parm_name': 'Valve offset'}
{'dde_nr': 60, 'proc_nr': 115, 'parm_nr': 2, 'parm_type': 0, 'parm_name': 'Monitor mode'}
{'dde_nr': 61, 'proc_nr': 114, 'parm_nr': 2, 'parm_type': 96, 'parm_name': 'Alarm register1'}
{'dde_nr': 62, 'proc_nr': 114, 'parm_nr': 3, 'parm_type': 96, 'parm_name': 'Alarm register2'}
{'dde_nr': 63, 'proc_nr': 116, 'parm_nr': 1, 'parm_type': 64, 'parm_name': '<CalRegZS1>'}
{'dde_nr': 64, 'proc_nr': 116, 'parm_nr': 2, 'parm_type': 64, 'parm_name': '<CalRegFS1>'}
{'dde_nr': 65, 'proc_nr': 116, 'parm_nr': 3, 'parm_type': 64, 'parm_name': '<CalRegZS2>'}
{'dde_nr': 66, 'proc_nr': 116, 'parm_nr': 4, 'parm_type': 64, 'parm_name': '<CalRegFS2>'}
{'dde_nr': 67, 'proc_nr': 114, 'parm_nr': 4, 'parm_type': 64, 'parm_name': 'ADC control register'}
{'dde_nr': 68, 'proc_nr': 116, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Bridge potmeter'}
{'dde_nr': 69, 'proc_nr': 115, 'parm_nr': 4, 'parm_type': 0, 'parm_name': '<AlarmEnble>'}
{'dde_nr': 70, 'proc_nr': 115, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Test mode'}
{'dde_nr': 71, 'proc_nr': 115, 'parm_nr': 6, 'parm_type': 0, 'parm_name': '<ADC channel select>'}
{'dde_nr': 72, 'proc_nr': 114, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Normal step controller response'}
{'dde_nr': 73, 'proc_nr': 117, 'parm_nr': 3, 'parm_type': 65, 'parm_name': 'Setpoint exponential smoothing filter'}
{'dde_nr': 74, 'proc_nr': 117, 'parm_nr': 4, 'parm_type': 65, 'parm_name': 'Sensor exponential smoothing filter'}
{'dde_nr': 75, 'proc_nr': 1, 'parm_nr': 21, 'parm_type': 33, 'parm_name': 'Analog output zero scale'}
{'dde_nr': 76, 'proc_nr': 1, 'parm_nr': 22, 'parm_type': 32, 'parm_name': 'Analog output full scale'}
{'dde_nr': 77, 'proc_nr': 1, 'parm_nr': 23, 'parm_type': 33, 'parm_name': 'Analog input zero scale'}
{'dde_nr': 78, 'proc_nr': 1, 'parm_nr': 24, 'parm_type': 32, 'parm_name': 'Analog input full scale'}
{'dde_nr': 79, 'proc_nr': 115, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Tuning mode'}
{'dde_nr': 80, 'proc_nr': 114, 'parm_nr': 6, 'parm_type': 0, 'parm_name': 'Valve default'}
{'dde_nr': 81, 'proc_nr': 0, 'parm_nr': 19, 'parm_type': 0, 'parm_name': 'Global modify'}
{'dde_nr': 82, 'proc_nr': 114, 'parm_nr': 7, 'parm_type': 65, 'parm_name': 'Valve span correction factor'}
{'dde_nr': 83, 'proc_nr': 114, 'parm_nr': 8, 'parm_type': 96, 'parm_name': 'Valve curve correction'}
{'dde_nr': 84, 'proc_nr': 114, 'parm_nr': 9, 'parm_type': 96, 'parm_name': '<MemShipNor>'}
{'dde_nr': 85, 'proc_nr': 114, 'parm_nr': 10, 'parm_type': 96, 'parm_name': '<MemShipOpn>'}
{'dde_nr': 86, 'proc_nr': 114, 'parm_nr': 11, 'parm_type': 0, 'parm_name': 'IO status'}
{'dde_nr': 90, 'proc_nr': 113, 'parm_nr': 1, 'parm_type': 96, 'parm_name': 'Device type'}
{'dde_nr': 91, 'proc_nr': 113, 'parm_nr': 2, 'parm_type': 96, 'parm_name': 'BHT model number'}
{'dde_nr': 92, 'proc_nr': 113, 'parm_nr': 3, 'parm_type': 96, 'parm_name': 'Serial number'}
{'dde_nr': 93, 'proc_nr': 113, 'parm_nr': 4, 'parm_type': 96, 'parm_name': 'Customer model number'}
{'dde_nr': 94, 'proc_nr': 118, 'parm_nr': 1, 'parm_type': 96, 'parm_name': 'BHT1'}
{'dde_nr': 95, 'proc_nr': 118, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'BHT2'}
{'dde_nr': 96, 'proc_nr': 118, 'parm_nr': 3, 'parm_type': 64, 'parm_name': 'BHT3'}
{'dde_nr': 97, 'proc_nr': 118, 'parm_nr': 4, 'parm_type': 32, 'parm_name': 'BHT4'}
{'dde_nr': 98, 'proc_nr': 118, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'BHT5'}
{'dde_nr': 99, 'proc_nr': 118, 'parm_nr': 6, 'parm_type': 0, 'parm_name': 'BHT6'}
{'dde_nr': 100, 'proc_nr': 118, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'BHT7'}
{'dde_nr': 101, 'proc_nr': 118, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'BHT8'}
{'dde_nr': 102, 'proc_nr': 118, 'parm_nr': 9, 'parm_type': 64, 'parm_name': 'BHT9'}
{'dde_nr': 103, 'proc_nr': 118, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'BHT10'}
{'dde_nr': 104, 'proc_nr': 114, 'parm_nr': 16, 'parm_type': 0, 'parm_name': 'Broadcast repeating time'}
{'dde_nr': 105, 'proc_nr': 113, 'parm_nr': 5, 'parm_type': 96, 'parm_name': 'Firmware version'}
{'dde_nr': 106, 'proc_nr': 115, 'parm_nr': 9, 'parm_type': 0, 'parm_name': 'Pressure sensor type'}
{'dde_nr': 107, 'proc_nr': 116, 'parm_nr': 8, 'parm_type': 65, 'parm_name': 'Barometer pressure'}
{'dde_nr': 108, 'proc_nr': 1, 'parm_nr': 25, 'parm_type': 33, 'parm_name': 'Sensor input zero scale'}
{'dde_nr': 109, 'proc_nr': 1, 'parm_nr': 26, 'parm_type': 32, 'parm_name': 'Sensor input full scale'}
{'dde_nr': 110, 'proc_nr': 1, 'parm_nr': 27, 'parm_type': 33, 'parm_name': 'Reference voltage input zero scale'}
{'dde_nr': 111, 'proc_nr': 1, 'parm_nr': 28, 'parm_type': 32, 'parm_name': 'Reference voltage input full scale'}
{'dde_nr': 112, 'proc_nr': 1, 'parm_nr': 29, 'parm_type': 33, 'parm_name': 'Analog setpoint zero scale'}
{'dde_nr': 113, 'proc_nr': 1, 'parm_nr': 30, 'parm_type': 32, 'parm_name': 'Analog setpoint full scale'}
{'dde_nr': 114, 'proc_nr': 115, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Reset'}
{'dde_nr': 115, 'proc_nr': 113, 'parm_nr': 6, 'parm_type': 96, 'parm_name': 'User tag'}
{'dde_nr': 116, 'proc_nr': 97, 'parm_nr': 1, 'parm_type': 32, 'parm_name': 'Alarm limit maximum'}
{'dde_nr': 117, 'proc_nr': 97, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'Alarm limit minimum'}
{'dde_nr': 118, 'proc_nr': 97, 'parm_nr': 3, 'parm_type': 0, 'parm_name': 'Alarm mode'}
{'dde_nr': 119, 'proc_nr': 97, 'parm_nr': 4, 'parm_type': 0, 'parm_name': 'Alarm output mode'}
{'dde_nr': 120, 'proc_nr': 97, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Alarm setpoint mode'}
{'dde_nr': 121, 'proc_nr': 97, 'parm_nr': 6, 'parm_type': 32, 'parm_name': 'Alarm new setpoint'}
{'dde_nr': 122, 'proc_nr': 104, 'parm_nr': 1, 'parm_type': 65, 'parm_name': 'Counter value'}
{'dde_nr': 123, 'proc_nr': 104, 'parm_nr': 2, 'parm_type': 0, 'parm_name': 'Counter unit index'}
{'dde_nr': 124, 'proc_nr': 104, 'parm_nr': 3, 'parm_type': 65, 'parm_name': 'Counter limit'}
{'dde_nr': 125, 'proc_nr': 104, 'parm_nr': 4, 'parm_type': 0, 'parm_name': 'Counter output mode'}
{'dde_nr': 126, 'proc_nr': 104, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Counter setpoint mode'}
{'dde_nr': 127, 'proc_nr': 104, 'parm_nr': 6, 'parm_type': 32, 'parm_name': 'Counter new setpoint'}
{'dde_nr': 128, 'proc_nr': 104, 'parm_nr': 7, 'parm_type': 96, 'parm_name': 'Counter unit'}
{'dde_nr': 129, 'proc_nr': 1, 'parm_nr': 31, 'parm_type': 96, 'parm_name': 'Capacity unit'}
{'dde_nr': 130, 'proc_nr': 104, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Counter mode'}
{'dde_nr': 131, 'proc_nr': 113, 'parm_nr': 7, 'parm_type': 96, 'parm_name': 'Minimum hardware revision'}
{'dde_nr': 132, 'proc_nr': 1, 'parm_nr': 1, 'parm_type': 65, 'parm_name': '<RCreadfact>'}
{'dde_nr': 133, 'proc_nr': 1, 'parm_nr': 2, 'parm_type': 0, 'parm_name': '<channumber>'}
{'dde_nr': 134, 'proc_nr': 1, 'parm_nr': 3, 'parm_type': 0, 'parm_name': '<masterchan>'}
{'dde_nr': 135, 'proc_nr': 1, 'parm_nr': 4, 'parm_type': 32, 'parm_name': '<RCslavefct>'}
{'dde_nr': 136, 'proc_nr': 1, 'parm_nr': 5, 'parm_type': 0, 'parm_name': '<inputnode>'}
{'dde_nr': 137, 'proc_nr': 1, 'parm_nr': 6, 'parm_type': 0, 'parm_name': '<inputproc>'}
{'dde_nr': 138, 'proc_nr': 1, 'parm_nr': 7, 'parm_type': 96, 'parm_name': '<RCreadunit>'}
{'dde_nr': 139, 'proc_nr': 33, 'parm_nr': 1, 'parm_type': 65, 'parm_name': 'Slave factor'}
{'dde_nr': 140, 'proc_nr': 33, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'Reference voltage input'}
{'dde_nr': 141, 'proc_nr': 114, 'parm_nr': 17, 'parm_type': 0, 'parm_name': 'Stable situation controller response'}
{'dde_nr': 142, 'proc_nr': 33, 'parm_nr': 7, 'parm_type': 65, 'parm_name': 'Temperature'}
{'dde_nr': 143, 'proc_nr': 33, 'parm_nr': 8, 'parm_type': 65, 'parm_name': 'Pressure'}
{'dde_nr': 144, 'proc_nr': 33, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Time'}
{'dde_nr': 145, 'proc_nr': 33, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Calibrated volume'}
{'dde_nr': 146, 'proc_nr': 1, 'parm_nr': 16, 'parm_type': 0, 'parm_name': 'Sensor number'}
{'dde_nr': 147, 'proc_nr': 115, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'Range select'}
{'dde_nr': 148, 'proc_nr': 1, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'Time out'}
{'dde_nr': 149, 'proc_nr': 33, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Frequency'}
{'dde_nr': 150, 'proc_nr': 33, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Impulses/m3'}
{'dde_nr': 151, 'proc_nr': 33, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'Normal volume flow'}
{'dde_nr': 152, 'proc_nr': 33, 'parm_nr': 6, 'parm_type': 65, 'parm_name': 'Volume flow'}
{'dde_nr': 153, 'proc_nr': 33, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Delta-p'}
{'dde_nr': 154, 'proc_nr': 33, 'parm_nr': 13, 'parm_type': 32, 'parm_name': '<scalefact>'}
{'dde_nr': 155, 'proc_nr': 1, 'parm_nr': 17, 'parm_type': 96, 'parm_name': 'Sensor name'}
{'dde_nr': 156, 'proc_nr': 97, 'parm_nr': 9, 'parm_type': 0, 'parm_name': 'Reset alarm enable'}
{'dde_nr': 157, 'proc_nr': 104, 'parm_nr': 9, 'parm_type': 0, 'parm_name': 'Reset counter enable'}
{'dde_nr': 158, 'proc_nr': 33, 'parm_nr': 14, 'parm_type': 0, 'parm_name': 'Master node'}
{'dde_nr': 159, 'proc_nr': 33, 'parm_nr': 15, 'parm_type': 0, 'parm_name': 'Master process'}
{'dde_nr': 160, 'proc_nr': 33, 'parm_nr': 16, 'parm_type': 0, 'parm_name': 'Remote instrument node'}
{'dde_nr': 161, 'proc_nr': 33, 'parm_nr': 17, 'parm_type': 0, 'parm_name': 'Remote instrument process'}
{'dde_nr': 162, 'proc_nr': 33, 'parm_nr': 18, 'parm_type': 65, 'parm_name': 'Minimum custom range'}
{'dde_nr': 163, 'proc_nr': 33, 'parm_nr': 20, 'parm_type': 65, 'parm_name': 'Maximum custom range'}
{'dde_nr': 164, 'proc_nr': 115, 'parm_nr': 11, 'parm_type': 0, 'parm_name': 'Relay/TTL output'}
{'dde_nr': 165, 'proc_nr': 114, 'parm_nr': 18, 'parm_type': 0, 'parm_name': 'Open from zero controller response'}
{'dde_nr': 166, 'proc_nr': 114, 'parm_nr': 20, 'parm_type': 0, 'parm_name': 'Controller features'}
{'dde_nr': 167, 'proc_nr': 114, 'parm_nr': 21, 'parm_type': 65, 'parm_name': 'PID-Kp'}
{'dde_nr': 168, 'proc_nr': 114, 'parm_nr': 22, 'parm_type': 65, 'parm_name': 'PID-Ti'}
{'dde_nr': 169, 'proc_nr': 114, 'parm_nr': 23, 'parm_type': 65, 'parm_name': 'PID-Td'}
{'dde_nr': 170, 'proc_nr': 33, 'parm_nr': 21, 'parm_type': 65, 'parm_name': 'Density'}
{'dde_nr': 171, 'proc_nr': 113, 'parm_nr': 8, 'parm_type': 96, 'parm_name': 'Calibration certificate'}
{'dde_nr': 172, 'proc_nr': 113, 'parm_nr': 9, 'parm_type': 96, 'parm_name': 'Calibration date'}
{'dde_nr': 173, 'proc_nr': 113, 'parm_nr': 10, 'parm_type': 96, 'parm_name': 'Service number'}
{'dde_nr': 174, 'proc_nr': 113, 'parm_nr': 11, 'parm_type': 96, 'parm_name': 'Service date'}
{'dde_nr': 175, 'proc_nr': 113, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Identification number'}
{'dde_nr': 176, 'proc_nr': 118, 'parm_nr': 11, 'parm_type': 0, 'parm_name': 'BHT11'}
{'dde_nr': 177, 'proc_nr': 115, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Power mode'}
{'dde_nr': 178, 'proc_nr': 113, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Pressure inlet'}
{'dde_nr': 179, 'proc_nr': 113, 'parm_nr': 14, 'parm_type': 65, 'parm_name': 'Pressure outlet'}
{'dde_nr': 180, 'proc_nr': 113, 'parm_nr': 15, 'parm_type': 65, 'parm_name': 'Orifice'}
{'dde_nr': 181, 'proc_nr': 113, 'parm_nr': 16, 'parm_type': 65, 'parm_name': 'Fluid temperature'}
{'dde_nr': 182, 'proc_nr': 97, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Alarm delay'}
{'dde_nr': 183, 'proc_nr': 33, 'parm_nr': 22, 'parm_type': 65, 'parm_name': 'Capacity 0%'}
{'dde_nr': 184, 'proc_nr': 0, 'parm_nr': 18, 'parm_type': 0, 'parm_name': 'Number of channels'}
{'dde_nr': 185, 'proc_nr': 0, 'parm_nr': 20, 'parm_type': 0, 'parm_name': 'Device function'}
{'dde_nr': 186, 'proc_nr': 123, 'parm_nr': 1, 'parm_type': 0, 'parm_name': 'Scan channel'}
{'dde_nr': 187, 'proc_nr': 123, 'parm_nr': 3, 'parm_type': 0, 'parm_name': 'Scan parameter'}
{'dde_nr': 188, 'proc_nr': 123, 'parm_nr': 4, 'parm_type': 32, 'parm_name': 'Scan time'}
{'dde_nr': 189, 'proc_nr': 123, 'parm_nr': 10, 'parm_type': 96, 'parm_name': 'Scan data'}
{'dde_nr': 190, 'proc_nr': 114, 'parm_nr': 24, 'parm_type': 65, 'parm_name': 'Valve open'}
{'dde_nr': 191, 'proc_nr': 115, 'parm_nr': 13, 'parm_type': 0, 'parm_name': 'Number of runs'}
{'dde_nr': 192, 'proc_nr': 115, 'parm_nr': 14, 'parm_type': 0, 'parm_name': 'Minimum process time'}
{'dde_nr': 193, 'proc_nr': 116, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Leak rate'}
{'dde_nr': 194, 'proc_nr': 115, 'parm_nr': 15, 'parm_type': 96, 'parm_name': 'Mode info request'}
{'dde_nr': 195, 'proc_nr': 115, 'parm_nr': 16, 'parm_type': 96, 'parm_name': 'Mode info option list'}
{'dde_nr': 196, 'proc_nr': 115, 'parm_nr': 17, 'parm_type': 96, 'parm_name': 'Mode info option description'}
{'dde_nr': 197, 'proc_nr': 115, 'parm_nr': 18, 'parm_type': 0, 'parm_name': 'Calibrations options'}
{'dde_nr': 198, 'proc_nr': 33, 'parm_nr': 4, 'parm_type': 65, 'parm_name': 'Mass flow'}
{'dde_nr': 199, 'proc_nr': 125, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'Fieldbus1 address'}
{'dde_nr': 200, 'proc_nr': 125, 'parm_nr': 3, 'parm_type': 0, 'parm_name': 'Interface configuration'}
{'dde_nr': 201, 'proc_nr': 125, 'parm_nr': 9, 'parm_type': 64, 'parm_name': 'Fieldbus1 baudrate'}
{'dde_nr': 202, 'proc_nr': 125, 'parm_nr': 20, 'parm_type': 96, 'parm_name': 'Fieldbus1 diagnostic string'}
{'dde_nr': 203, 'proc_nr': 115, 'parm_nr': 22, 'parm_type': 0, 'parm_name': 'Number of vanes'}
{'dde_nr': 204, 'proc_nr': 125, 'parm_nr': 21, 'parm_type': 96, 'parm_name': 'Fieldbus1 name'}
{'dde_nr': 205, 'proc_nr': 33, 'parm_nr': 0, 'parm_type': 65, 'parm_name': 'fMeasure'}
{'dde_nr': 206, 'proc_nr': 33, 'parm_nr': 3, 'parm_type': 65, 'parm_name': 'fSetpoint'}
{'dde_nr': 207, 'proc_nr': 33, 'parm_nr': 23, 'parm_type': 65, 'parm_name': 'Mass'}
{'dde_nr': 208, 'proc_nr': 119, 'parm_nr': 1, 'parm_type': 96, 'parm_name': 'Manufacturer status register'}
{'dde_nr': 209, 'proc_nr': 119, 'parm_nr': 2, 'parm_type': 96, 'parm_name': 'Manufacturer warning register'}
{'dde_nr': 210, 'proc_nr': 119, 'parm_nr': 3, 'parm_type': 96, 'parm_name': 'Manufacturer error register'}
{'dde_nr': 211, 'proc_nr': 119, 'parm_nr': 4, 'parm_type': 96, 'parm_name': 'Diagnostic history string'}
{'dde_nr': 212, 'proc_nr': 119, 'parm_nr': 5, 'parm_type': 0, 'parm_name': 'Diagnostic mode'}
{'dde_nr': 213, 'proc_nr': 119, 'parm_nr': 6, 'parm_type': 0, 'parm_name': 'Manufacturer status enable'}
{'dde_nr': 214, 'proc_nr': 116, 'parm_nr': 21, 'parm_type': 65, 'parm_name': 'Analog output zero adjust'}
{'dde_nr': 215, 'proc_nr': 116, 'parm_nr': 22, 'parm_type': 65, 'parm_name': 'Analog output span adjust'}
{'dde_nr': 216, 'proc_nr': 116, 'parm_nr': 23, 'parm_type': 65, 'parm_name': 'Analog input zero adjust'}
{'dde_nr': 217, 'proc_nr': 116, 'parm_nr': 24, 'parm_type': 65, 'parm_name': 'Analog input span adjust'}
{'dde_nr': 218, 'proc_nr': 116, 'parm_nr': 25, 'parm_type': 65, 'parm_name': 'Sensor input zero adjust'}
{'dde_nr': 219, 'proc_nr': 116, 'parm_nr': 26, 'parm_type': 65, 'parm_name': 'Sensor input span adjust'}
{'dde_nr': 220, 'proc_nr': 116, 'parm_nr': 27, 'parm_type': 65, 'parm_name': 'Temperature input zero adjust'}
{'dde_nr': 221, 'proc_nr': 116, 'parm_nr': 28, 'parm_type': 65, 'parm_name': 'Temperature input span adjust'}
{'dde_nr': 222, 'proc_nr': 117, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'Adaptive smoothing factor'}
{'dde_nr': 223, 'proc_nr': 33, 'parm_nr': 24, 'parm_type': 32, 'parm_name': 'Slope setpoint step'}
{'dde_nr': 224, 'proc_nr': 117, 'parm_nr': 6, 'parm_type': 32, 'parm_name': 'Filter length'}
{'dde_nr': 225, 'proc_nr': 33, 'parm_nr': 25, 'parm_type': 65, 'parm_name': 'Absolute accuracy'}
{'dde_nr': 226, 'proc_nr': 33, 'parm_nr': 26, 'parm_type': 0, 'parm_name': 'Lookup table index'}
{'dde_nr': 227, 'proc_nr': 33, 'parm_nr': 27, 'parm_type': 65, 'parm_name': 'Lookup table X'}
{'dde_nr': 228, 'proc_nr': 33, 'parm_nr': 28, 'parm_type': 65, 'parm_name': 'Lookup table Y'}
{'dde_nr': 229, 'proc_nr': 33, 'parm_nr': 29, 'parm_type': 0, 'parm_name': 'Lookup table temperature index'}
{'dde_nr': 230, 'proc_nr': 33, 'parm_nr': 30, 'parm_type': 65, 'parm_name': 'Lookup table temperature'}
{'dde_nr': 231, 'proc_nr': 114, 'parm_nr': 25, 'parm_type': 65, 'parm_name': 'Valve maximum'}
{'dde_nr': 232, 'proc_nr': 114, 'parm_nr': 26, 'parm_type': 0, 'parm_name': 'Valve mode'}
{'dde_nr': 233, 'proc_nr': 114, 'parm_nr': 27, 'parm_type': 65, 'parm_name': 'Valve open correction'}
{'dde_nr': 234, 'proc_nr': 114, 'parm_nr': 28, 'parm_type': 65, 'parm_name': 'Valve zero hold'}
{'dde_nr': 235, 'proc_nr': 114, 'parm_nr': 29, 'parm_type': 65, 'parm_name': 'Valve slope'}
{'dde_nr': 236, 'proc_nr': 0, 'parm_nr': 21, 'parm_type': 96, 'parm_name': 'IFI data'}
{'dde_nr': 237, 'proc_nr': 115, 'parm_nr': 20, 'parm_type': 96, 'parm_name': 'Range used'}
{'dde_nr': 238, 'proc_nr': 33, 'parm_nr': 31, 'parm_type': 0, 'parm_name': 'Fluidset properties'}
{'dde_nr': 239, 'proc_nr': 33, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Lookup table unit type index'}
{'dde_nr': 240, 'proc_nr': 33, 'parm_nr': 13, 'parm_type': 96, 'parm_name': 'Lookup table unit type'}
{'dde_nr': 241, 'proc_nr': 33, 'parm_nr': 16, 'parm_type': 0, 'parm_name': 'Lookup table unit index'}
{'dde_nr': 242, 'proc_nr': 33, 'parm_nr': 17, 'parm_type': 96, 'parm_name': 'Lookup table unit'}
{'dde_nr': 243, 'proc_nr': 1, 'parm_nr': 29, 'parm_type': 0, 'parm_name': 'Capacity unit type index'}
{'dde_nr': 244, 'proc_nr': 1, 'parm_nr': 30, 'parm_type': 96, 'parm_name': 'Capacity unit type'}
{'dde_nr': 245, 'proc_nr': 33, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Capacity unit type temperature'}
{'dde_nr': 246, 'proc_nr': 33, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Capacity unit type pressure'}
{'dde_nr': 247, 'proc_nr': 1, 'parm_nr': 27, 'parm_type': 65, 'parm_name': 'Capacity minimum'}
{'dde_nr': 248, 'proc_nr': 1, 'parm_nr': 28, 'parm_type': 65, 'parm_name': 'Capacity maximum'}
{'dde_nr': 249, 'proc_nr': 113, 'parm_nr': 17, 'parm_type': 32, 'parm_name': 'Formula type'}
{'dde_nr': 250, 'proc_nr': 113, 'parm_nr': 18, 'parm_type': 65, 'parm_name': 'Heat capacity'}
{'dde_nr': 251, 'proc_nr': 113, 'parm_nr': 20, 'parm_type': 65, 'parm_name': 'Thermal conductivity'}
{'dde_nr': 252, 'proc_nr': 113, 'parm_nr': 21, 'parm_type': 65, 'parm_name': 'Viscosity'}
{'dde_nr': 253, 'proc_nr': 113, 'parm_nr': 22, 'parm_type': 65, 'parm_name': 'Standard flow'}
{'dde_nr': 254, 'proc_nr': 114, 'parm_nr': 30, 'parm_type': 65, 'parm_name': 'Controller speed'}
{'dde_nr': 255, 'proc_nr': 113, 'parm_nr': 23, 'parm_type': 32, 'parm_name': 'Sensor code'}
{'dde_nr': 256, 'proc_nr': 113, 'parm_nr': 24, 'parm_type': 0, 'parm_name': 'Sensor configuration code'}
{'dde_nr': 257, 'proc_nr': 113, 'parm_nr': 25, 'parm_type': 32, 'parm_name': 'Restriction code'}
{'dde_nr': 258, 'proc_nr': 113, 'parm_nr': 26, 'parm_type': 0, 'parm_name': 'Restriction configurator code'}
{'dde_nr': 259, 'proc_nr': 113, 'parm_nr': 27, 'parm_type': 64, 'parm_name': 'Restriction NxP'}
{'dde_nr': 260, 'proc_nr': 113, 'parm_nr': 28, 'parm_type': 96, 'parm_name': 'Seals information'}
{'dde_nr': 261, 'proc_nr': 113, 'parm_nr': 29, 'parm_type': 32, 'parm_name': 'Valve code'}
{'dde_nr': 262, 'proc_nr': 113, 'parm_nr': 30, 'parm_type': 0, 'parm_name': 'Valve configuration code'}
{'dde_nr': 263, 'proc_nr': 113, 'parm_nr': 31, 'parm_type': 64, 'parm_name': 'Instrument properties'}
{'dde_nr': 264, 'proc_nr': 116, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'Lookup table frequency index'}
{'dde_nr': 265, 'proc_nr': 116, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Lookup table frequency frequency'}
{'dde_nr': 266, 'proc_nr': 116, 'parm_nr': 12, 'parm_type': 65, 'parm_name': 'Lookup table frequency temperature'}
{'dde_nr': 267, 'proc_nr': 116, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Lookup table frequency density'}
{'dde_nr': 268, 'proc_nr': 116, 'parm_nr': 14, 'parm_type': 65, 'parm_name': 'Lookup table frequency span adjust'}
{'dde_nr': 269, 'proc_nr': 65, 'parm_nr': 15, 'parm_type': 0, 'parm_name': 'Capacity unit index (ext)'}
{'dde_nr': 270, 'proc_nr': 116, 'parm_nr': 15, 'parm_type': 65, 'parm_name': 'Density actual'}
{'dde_nr': 271, 'proc_nr': 116, 'parm_nr': 18, 'parm_type': 65, 'parm_name': 'Measured restriction'}
{'dde_nr': 272, 'proc_nr': 116, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Temperature potmeter'}
{'dde_nr': 273, 'proc_nr': 116, 'parm_nr': 9, 'parm_type': 0, 'parm_name': 'Temperature potmeter gain'}
{'dde_nr': 274, 'proc_nr': 104, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Counter controller overrun correction'}
{'dde_nr': 275, 'proc_nr': 104, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Counter controller gain'}
{'dde_nr': 276, 'proc_nr': 65, 'parm_nr': 1, 'parm_type': 0, 'parm_name': 'Sub fluid number'}
{'dde_nr': 277, 'proc_nr': 116, 'parm_nr': 17, 'parm_type': 65, 'parm_name': 'Temperature compensation factor'}
{'dde_nr': 278, 'proc_nr': 116, 'parm_nr': 29, 'parm_type': 64, 'parm_name': 'DSP register address'}
{'dde_nr': 279, 'proc_nr': 116, 'parm_nr': 30, 'parm_type': 64, 'parm_name': 'DSP register long'}
{'dde_nr': 280, 'proc_nr': 116, 'parm_nr': 30, 'parm_type': 65, 'parm_name': 'DSP register floating point'}
{'dde_nr': 281, 'proc_nr': 116, 'parm_nr': 31, 'parm_type': 32, 'parm_name': 'DSP register integer'}
{'dde_nr': 282, 'proc_nr': 121, 'parm_nr': 0, 'parm_type': 65, 'parm_name': 'Standard deviation'}
{'dde_nr': 283, 'proc_nr': 121, 'parm_nr': 1, 'parm_type': 32, 'parm_name': 'Measurement status'}
{'dde_nr': 284, 'proc_nr': 121, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'Measurement stop criteria'}
{'dde_nr': 285, 'proc_nr': 121, 'parm_nr': 3, 'parm_type': 32, 'parm_name': 'Measurement time out'}
{'dde_nr': 286, 'proc_nr': 121, 'parm_nr': 4, 'parm_type': 32, 'parm_name': 'Maximum number of runs'}
{'dde_nr': 287, 'proc_nr': 121, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'Minimum standard deviation'}
{'dde_nr': 288, 'proc_nr': 114, 'parm_nr': 31, 'parm_type': 64, 'parm_name': 'IO switch status'}
{'dde_nr': 295, 'proc_nr': 65, 'parm_nr': 21, 'parm_type': 32, 'parm_name': 'Sensor bridge settings'}
{'dde_nr': 296, 'proc_nr': 65, 'parm_nr': 22, 'parm_type': 65, 'parm_name': 'Sensor bridge current'}
{'dde_nr': 297, 'proc_nr': 65, 'parm_nr': 23, 'parm_type': 65, 'parm_name': 'Sensor resistance'}
{'dde_nr': 298, 'proc_nr': 65, 'parm_nr': 24, 'parm_type': 65, 'parm_name': 'Sensor bridge voltage'}
{'dde_nr': 299, 'proc_nr': 65, 'parm_nr': 25, 'parm_type': 96, 'parm_name': 'Sensor group name'}
{'dde_nr': 300, 'proc_nr': 116, 'parm_nr': 20, 'parm_type': 65, 'parm_name': 'Sensor calibration temperature'}
{'dde_nr': 301, 'proc_nr': 115, 'parm_nr': 31, 'parm_type': 0, 'parm_name': 'Valve safe state'}
{'dde_nr': 302, 'proc_nr': 104, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Counter unit type index'}
{'dde_nr': 303, 'proc_nr': 104, 'parm_nr': 13, 'parm_type': 96, 'parm_name': 'Counter unit type'}
{'dde_nr': 304, 'proc_nr': 104, 'parm_nr': 14, 'parm_type': 0, 'parm_name': 'Counter unit index (ext)'}
{'dde_nr': 305, 'proc_nr': 125, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Fieldbus1 selection'}
{'dde_nr': 306, 'proc_nr': 125, 'parm_nr': 11, 'parm_type': 0, 'parm_name': 'Fieldbus1 medium'}
{'dde_nr': 307, 'proc_nr': 124, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Fieldbus2 mode'}
{'dde_nr': 308, 'proc_nr': 124, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Fieldbus2 selection'}
{'dde_nr': 309, 'proc_nr': 124, 'parm_nr': 10, 'parm_type': 0, 'parm_name': 'Fieldbus2 address'}
{'dde_nr': 310, 'proc_nr': 124, 'parm_nr': 9, 'parm_type': 64, 'parm_name': 'Fieldbus2 baudrate'}
{'dde_nr': 311, 'proc_nr': 124, 'parm_nr': 11, 'parm_type': 0, 'parm_name': 'Fieldbus2 medium'}
{'dde_nr': 312, 'proc_nr': 124, 'parm_nr': 20, 'parm_type': 96, 'parm_name': 'Fieldbus2 diagnostics'}
{'dde_nr': 313, 'proc_nr': 124, 'parm_nr': 21, 'parm_type': 96, 'parm_name': 'Fieldbus2 name'}
{'dde_nr': 314, 'proc_nr': 120, 'parm_nr': 0, 'parm_type': 0, 'parm_name': 'PIO channel selection'}
{'dde_nr': 315, 'proc_nr': 120, 'parm_nr': 2, 'parm_type': 32, 'parm_name': 'PIO parameter'}
{'dde_nr': 316, 'proc_nr': 120, 'parm_nr': 6, 'parm_type': 65, 'parm_name': 'PIO input/output filter'}
{'dde_nr': 317, 'proc_nr': 120, 'parm_nr': 7, 'parm_type': 65, 'parm_name': 'PIO parameter capacity 0%'}
{'dde_nr': 318, 'proc_nr': 120, 'parm_nr': 3, 'parm_type': 65, 'parm_name': 'PIO parameter capacity 100%'}
{'dde_nr': 319, 'proc_nr': 120, 'parm_nr': 1, 'parm_type': 0, 'parm_name': 'PIO configuration selection'}
{'dde_nr': 320, 'proc_nr': 120, 'parm_nr': 4, 'parm_type': 65, 'parm_name': 'PIO analog zero adjust'}
{'dde_nr': 321, 'proc_nr': 120, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'PIO analog span adjust'}
{'dde_nr': 322, 'proc_nr': 120, 'parm_nr': 8, 'parm_type': 65, 'parm_name': 'PIO hardware capacity max'}
{'dde_nr': 323, 'proc_nr': 120, 'parm_nr': 9, 'parm_type': 0, 'parm_name': 'PIO capacity set selection'}
{'dde_nr': 324, 'proc_nr': 120, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'PIO hardware capacity 0%'}
{'dde_nr': 325, 'proc_nr': 120, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'PIO hardware capacity 100%'}
{'dde_nr': 326, 'proc_nr': 0, 'parm_nr': 6, 'parm_type': 32, 'parm_name': 'Hardware platform id'}
{'dde_nr': 327, 'proc_nr': 0, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Hardware platform sub id'}
{'dde_nr': 328, 'proc_nr': 124, 'parm_nr': 31, 'parm_type': 64, 'parm_name': 'Temporary baudrate'}
{'dde_nr': 329, 'proc_nr': 115, 'parm_nr': 23, 'parm_type': 0, 'parm_name': 'Setpoint monitor mode'}
{'dde_nr': 330, 'proc_nr': 118, 'parm_nr': 12, 'parm_type': 64, 'parm_name': 'BHT12'}
{'dde_nr': 331, 'proc_nr': 65, 'parm_nr': 26, 'parm_type': 65, 'parm_name': 'Nominal sensor voltage'}
{'dde_nr': 332, 'proc_nr': 116, 'parm_nr': 16, 'parm_type': 65, 'parm_name': 'Sensor voltage compensation factor'}
{'dde_nr': 333, 'proc_nr': 119, 'parm_nr': 31, 'parm_type': 96, 'parm_name': 'PCB serial number'}
{'dde_nr': 334, 'proc_nr': 115, 'parm_nr': 24, 'parm_type': 0, 'parm_name': 'Minimum measure time'}
{'dde_nr': 335, 'proc_nr': 125, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Fieldbus1 parity'}
{'dde_nr': 336, 'proc_nr': 124, 'parm_nr': 12, 'parm_type': 0, 'parm_name': 'Fieldbus2 parity'}
{'dde_nr': 337, 'proc_nr': 0, 'parm_nr': 8, 'parm_type': 0, 'parm_name': 'Firmware id'}
{'dde_nr': 338, 'proc_nr': 114, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Valve 100%'}
{'dde_nr': 339, 'proc_nr': 114, 'parm_nr': 14, 'parm_type': 65, 'parm_name': 'Setpoint minimum'}
{'dde_nr': 340, 'proc_nr': 119, 'parm_nr': 30, 'parm_type': 0, 'parm_name': 'PCB serial number index'}
{'dde_nr': 341, 'proc_nr': 125, 'parm_nr': 13, 'parm_type': 96, 'parm_name': 'Fieldbus1 MAC address'}
{'dde_nr': 342, 'proc_nr': 126, 'parm_nr': 0, 'parm_type': 0, 'parm_name': 'Source fluidset index'}
{'dde_nr': 343, 'proc_nr': 126, 'parm_nr': 1, 'parm_type': 32, 'parm_name': 'Capacity range calculation method'}
{'dde_nr': 344, 'proc_nr': 126, 'parm_nr': 2, 'parm_type': 0, 'parm_name': 'Actual fluid property index'}
{'dde_nr': 345, 'proc_nr': 126, 'parm_nr': 3, 'parm_type': 32, 'parm_name': 'Actual fluid property calculation method'}
{'dde_nr': 346, 'proc_nr': 126, 'parm_nr': 4, 'parm_type': 0, 'parm_name': 'Mix fraction type'}
{'dde_nr': 347, 'proc_nr': 126, 'parm_nr': 5, 'parm_type': 65, 'parm_name': 'Mix volume temperature'}
{'dde_nr': 348, 'proc_nr': 126, 'parm_nr': 6, 'parm_type': 65, 'parm_name': 'Mix volume pressure'}
{'dde_nr': 349, 'proc_nr': 126, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Mix component index'}
{'dde_nr': 350, 'proc_nr': 126, 'parm_nr': 8, 'parm_type': 65, 'parm_name': 'Mix component fraction'}
{'dde_nr': 351, 'proc_nr': 126, 'parm_nr': 9, 'parm_type': 96, 'parm_name': 'Mix component fluid name'}
{'dde_nr': 352, 'proc_nr': 126, 'parm_nr': 10, 'parm_type': 96, 'parm_name': 'Equivalent measure fluid name'}
{'dde_nr': 353, 'proc_nr': 126, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Equivalent measure'}
{'dde_nr': 354, 'proc_nr': 126, 'parm_nr': 12, 'parm_type': 32, 'parm_name': 'Fluid conversion conditions selection'}
{'dde_nr': 355, 'proc_nr': 126, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Sensor+restriction capacity minimum'}
{'dde_nr': 356, 'proc_nr': 126, 'parm_nr': 14, 'parm_type': 65, 'parm_name': 'Sensor+restriction capacity maximum'}
{'dde_nr': 357, 'proc_nr': 126, 'parm_nr': 15, 'parm_type': 65, 'parm_name': 'Valve capacity minimum'}
{'dde_nr': 358, 'proc_nr': 126, 'parm_nr': 16, 'parm_type': 65, 'parm_name': 'Valve capacity maximum'}
{'dde_nr': 359, 'proc_nr': 104, 'parm_nr': 15, 'parm_type': 65, 'parm_name': 'Maximum allowed dosing time'}
{'dde_nr': 360, 'proc_nr': 104, 'parm_nr': 16, 'parm_type': 65, 'parm_name': 'Most recent dosing time'}
{'dde_nr': 361, 'proc_nr': 114, 'parm_nr': 15, 'parm_type': 65, 'parm_name': 'Controller hysteresis'}
{'dde_nr': 362, 'proc_nr': 126, 'parm_nr': 17, 'parm_type': 65, 'parm_name': 'Pressure sensor input zero adjust'}
{'dde_nr': 363, 'proc_nr': 126, 'parm_nr': 18, 'parm_type': 65, 'parm_name': 'Pressure sensor input span adjust'}
{'dde_nr': 364, 'proc_nr': 127, 'parm_nr': 0, 'parm_type': 64, 'parm_name': 'Special parameter index'}
{'dde_nr': 365, 'proc_nr': 127, 'parm_nr': 1, 'parm_type': 64, 'parm_name': 'Special parameter i long'}
{'dde_nr': 366, 'proc_nr': 127, 'parm_nr': 2, 'parm_type': 65, 'parm_name': 'Special parameter i float'}
{'dde_nr': 367, 'proc_nr': 127, 'parm_nr': 3, 'parm_type': 96, 'parm_name': 'Special parameter i name'}
{'dde_nr': 368, 'proc_nr': 127, 'parm_nr': 4, 'parm_type': 64, 'parm_name': 'Special parameter l1 long'}
{'dde_nr': 369, 'proc_nr': 127, 'parm_nr': 5, 'parm_type': 64, 'parm_name': 'Special parameter l2 long'}
{'dde_nr': 370, 'proc_nr': 127, 'parm_nr': 6, 'parm_type': 64, 'parm_name': 'Special parameter l3 long'}
{'dde_nr': 371, 'proc_nr': 127, 'parm_nr': 7, 'parm_type': 64, 'parm_name': 'Special parameter l4 long'}
{'dde_nr': 372, 'proc_nr': 127, 'parm_nr': 8, 'parm_type': 64, 'parm_name': 'Special parameter l5 long'}
{'dde_nr': 373, 'proc_nr': 127, 'parm_nr': 9, 'parm_type': 65, 'parm_name': 'Special parameter f1 float'}
{'dde_nr': 374, 'proc_nr': 127, 'parm_nr': 10, 'parm_type': 65, 'parm_name': 'Special parameter f2 float'}
{'dde_nr': 375, 'proc_nr': 127, 'parm_nr': 11, 'parm_type': 65, 'parm_name': 'Special parameter f3 float'}
{'dde_nr': 376, 'proc_nr': 127, 'parm_nr': 12, 'parm_type': 65, 'parm_name': 'Special parameter f4 float'}
{'dde_nr': 377, 'proc_nr': 127, 'parm_nr': 13, 'parm_type': 65, 'parm_name': 'Special parameter f5 float'}
{'dde_nr': 378, 'proc_nr': 125, 'parm_nr': 7, 'parm_type': 0, 'parm_name': 'Fieldbus interface index'}
"""
        