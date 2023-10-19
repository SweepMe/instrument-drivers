# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH
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

# Contribution: We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D. for providing the initial version of this driver.

# SweepMe! device class
# Type: Logger
# Device: Keithley 3706A


from EmptyDeviceClass import EmptyDevice
import time
import numpy as np

class Device(EmptyDevice):

    description = """
                    <p>This driver gives access to the multimeter functions of the Keithley 3706A. There is an additional driver Switch-Keihtley_3706A that can be used to control only the switching matrix.</p>
                    <p>The driver was only tested for some use cases which is why we recommend to test the driver for your scenario before using it productively.</p>
                    <p>&nbsp;</p>
                    <p><strong>Keywords:&nbsp;</strong>Tektronix, system switch, multimeter</p>
                    <p>&nbsp;</p>
                    <p><strong>Models:</strong>&nbsp;Keithley 3706A-NFP, Keithley 3706A</p>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>If you use "Scanning", you need to enter a comma-separated string of the selected channels, e.g "1101, 1201, 1301" and optionally some channel variable names.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Contribution:</strong></p>
                    <p>We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D. for providing the initial version of this driver.</p>
                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keithley3706A"

        self.port_manager = True
        self.port_types = ["USB", "GPIB"]

        self.port_properties = {
                                    "timeout": 20,
                                    "EOL": "\n",
                                    "baudrate": 9600, # factory default
                                }


        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC":   "dmm.DC_VOLTS",
            "Voltage AC":   "dmm.AC_VOLTS",
            "Current DC":   "dmm.AC_CURRENT",
            "Current AC":   "dmm.DC_CURRENT",
            "Common side ohms": "dmm.COMMON_SIDE_OHMS",
            "Four wire ohms":  "dmm.FOUR_WIRE_OHMS",
            "Two wire ohms": "dmm.TWO_WIRE_OHMS",
            "Frequency":    "dmm.FREQUENCY",
            "Period":       "dmm.PERIOD",
            "Temperature":  "dmm.TEMPERATURE",
            "Continuity":   "dmm.CONTINUITY",
            "No function": "dmm.NO_FUNCTION"
                        }
        self.mode_variables = {
            "Voltage DC":   "Voltage",
            "Voltage AC":   "Voltage",
            "Current DC":   "Current",
            "Current AC":   "Current",
            "Common side ohms": "Resistance (common side)",
            "Four wire ohms":  "Resistance (four wire)",
            "Two wire ohms": "Resistance (two wire)",
            "Frequency":    "Frequency",
            "Period":       "Period",
            "Temperature":  "Temperature",
            "Continuity":   "Continuity",
            "No function": "None"
        }
        self.variables=['test']

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC":   "V",
            "Voltage AC":   "V",
            "Current DC":   "A",
            "Current AC":   "A",
            "Common side ohms": "Ohm",
            "Four wire ohms":  "Ohm",
            "Two wire ohms": "Ohm",
            "Frequency":    "Hz",
            "Period":       "s",
            "Temperature":  "K",
            "Continuity":   "",
            "No function": ""
        }

        # a list of available resolutions as they can be sent to the instrument
        self.resolutions = [
                            "0.1",      # i.e., 100.0 V (3½ digits)
                            "0.01",     # i.e., 10.00 V (3½ digits)
                            "0.001",    # i.e., 1.000 V (3½ digits)
                            "0.0001",   # i.e., 1.0000 V (4½ digits)
                            "0.00001",  # i.e., 1.00000 V (5½ digits)
                            "0.000001", # i.e., 1.000000 V (6½ digits)
                            ]

        self.nplc_types = {
                                "Fast (0.1)"  : 0.1,
                                "Medium (1.0)": 1.0,
                                "Slow (10.0)" : 10.0,
                            }



    def set_GUIparameter(self):

        GUIparameter = {
                        "Mode" : list(self.modes.keys()),
                        "Average":1,
                        "NPLC": list(self.nplc_types.keys()),
                        "Range": ["Auto","1e-3","1","10","100","1e3","10e4","1e5","1e6"],
                        "Autodelay":True,
                        "Line sync":True,
                        "Scanning":False, # Scanning is no faster than separately switching=
                        "Channel list":"",
                        "Channel names":"",

                        #"Display": ["On", "Off"],
                        #"Temperature unit": ["°C", "K", "°F"],
                        #"Trigger": list(self.trigger_types.keys()),
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter = {}):
        self.mode = parameter['Mode']
        self.scanning = parameter['Scanning']
        self.measure_function = self.modes[self.mode]
        self.measure_count = int(parameter['Average'])
        self.channel_list = parameter['Channel list'].split(';')
        self.channel_names = parameter['Channel names'].split(';')
        self.range = parameter['Range']
        self.autorange = 'dmm.ON' if self.range=='Auto' else 'dmm.OFF'
        self.nplc = self.nplc_types[parameter['NPLC']] #.replace("(", "").replace(")", "").split()[-1]
        self.autodelay = 'dmm.ON' if parameter['Autodelay'] else 'dmm.OFF'
        self.linesync = 'dmm.ON' if parameter['Line sync'] else 'dmm.OFF'

        #self.resolution = parameter['Resolution']
        #self.clist = parameter['Channel'].replace(" ", "").replace("-", "").split(",")
        #self.trigger_type = parameter['Trigger']
        #self.display = parameter['Display']
        #self.temperature_unit = str(parameter["Temperature unit"])
        #self.port_string = parameter["Port"]
        #average = int(parameter['Average'])


        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected

        if self.scanning:
            self.variables=[]
            for i,ch in enumerate(self.channel_list):
                self.variables.append(self.mode_variables[self.mode] + " " + str(self.channel_names[i]))
        else:
            self.variables = [self.mode_variables[self.mode]]

        if "Temperature" in self.mode:
            self.units = [self.temperature_unit]*len(self.variables)
        else:
            self.units = [self.mode_units[self.mode]]*len(self.variables)

        self.plottype =  [True]*len(self.variables)  # True to plot data
        self.savetype =  [True]*len(self.variables)  # True to save data

        # print('Channel list length: ',len(self.channel_list))
        # print(self.channel_list)
        # print(self.channel_names)
        # print('variables: ',self.variables)
        # print('units: ',self.units)


    def initialize(self):
        # Optionally, check slot interlock status:
        # for slot in self.slots_in_use:
            # if not bool(self.port.query('print(slot['+str(slot)+'].interlock.state)').strip('\n')):
                # raise ValueError('Slot ' + str(slot) ' interlock not closed. Make sure interlock is in place if you want to use the analog backplane relays.')
        pass

    def deinitialize(self):
        pass

    def configure(self):
        # Configure DMM measurement parameters
        config_commands = [
            "dmm.func = " + self.measure_function,
            "dmm.autozero = dmm.AUTOZERO_ONCE",
            "dmm.autodelay = " + self.autodelay,
            "dmm.autorange = " + self.autorange,
            "dmm.linesync = " + self.linesync,
            "dmm.nplc = " + str(self.nplc),
            "dmm.measurecount = " + str(self.measure_count),
            ]
        for command in config_commands:
            self.port.write(command)
        if not (self.range=="Auto"):
            self.port.write("dmm.range = " + str(self.range))

        # Set up channel scanning, if this option is selected
        if self.scanning:
            self.port.write('dmm.configure.set("test")')
            self.port.write('scan.create()')
            self.port.write('scan.measurecount = '+ str(self.measure_count))
            for ch in self.channel_list:
                self.port.write('scan.addimagestep("' + str(ch) + '","test")')

        # Configure buffer
        if self.scanning:
            self.buffer_size = len(self.channel_list)*self.measure_count
        else:
            self.buffer_size = self.measure_count
        buffer_commands = [
            'buffer1 = dmm.makebuffer(' + str(self.buffer_size) + ')',
            'buffer1.collecttimestamps = 1'
        ]
        for command in buffer_commands:
            self.port.write(command)

    def unconfigure(self):
        pass

    def measure(self):
        if self.scanning:
            self.port.write("scan.background(buffer1)")  # start scan in the background
        else:
            self.port.write("dmm.measure(buffer1)")

    def call(self):
        # If scanning, check the scan state until complete (returns state='6')
        if self.scanning:
            currrent_state = '2'
            estimated_measure_time = float(self.nplc)/60*float(self.measure_count)*len(self.channel_list)
            sleep_time = 0.005
            for i in range(int((estimated_measure_time*2+1)/sleep_time)):
                self.port.write('print(scan.state())')
                state = self.port.read()[0]
                if state=='6':
                    #print(i)
                    break
                time.sleep(sleep_time)
        # Read buffer
        self.port.write('printbuffer(1, buffer1.n, buffer1.readings)')
        readings = self.port.read()
        readings_list = np.array([float(x) for x in readings.split(',')])

        # Make sure the length of the reading_list is right
        # If the buffer was read before the scan finished, it could be too small
        if len(readings_list) < (int(self.measure_count)*len(self.channel_list)):
            print('buffer not full yet, wait another 0.5s and try again')
            time.sleep(0.5)
            self.port.write('printbuffer(1, buffer1.n, buffer1.readings)')
            readings = self.port.read()
            readings_list = np.array([float(x) for x in readings.split(',')])
        # self.port.write('print(buffer1.n)')
        # buffer_n = self.port.read().split('.')[0]
        # print(buffer_n)
        # if int(buffer_n)<(int(self.measure_count)*len(self.channel_list)):
            # print('buffer not full yet, wait another 0.5s')
            # time.sleep(0.5)

        if self.scanning:
            return [np.mean(x) for x in
                    np.split(readings_list,len(self.channel_list))]
        else:
            return [np.mean(readings_list)]
